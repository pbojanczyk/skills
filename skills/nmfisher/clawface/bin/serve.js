#!/usr/bin/env node
"use strict";

const http = require("http");
const fs = require("fs");
const path = require("path");

// -- CLI arg parsing ----------------------------------------------------------

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    const arg = argv[i];
    if (arg.startsWith("--") && i + 1 < argv.length) {
      args[arg.slice(2)] = argv[++i];
    }
  }
  return args;
}

const crypto = require("crypto");

const args = parseArgs(process.argv);

const distDir = path.resolve(args.dist || path.join(__dirname, "..", "dist"));
const toolsDir = args["tools-dir"] ? path.resolve(args["tools-dir"]) : "";
const port = parseInt(args.port || "18794", 10);
const gatewayUrl = args["gateway-url"] || "";
const gatewayToken = args["gateway-token"] || "";

// Device credentials: accept --device-id/--private-key/--public-key directly,
// or load from --identity-file (path to device.json).
let deviceId = args["device-id"] || "";
let privateKey = args["private-key"] || "";
let publicKey = args["public-key"] || "";

if (!deviceId && args["identity-file"]) {
  try {
    const identity = JSON.parse(fs.readFileSync(args["identity-file"], "utf8"));
    deviceId = identity.deviceId || "";
    if (identity.privateKeyPem) {
      const key = crypto.createPrivateKey(identity.privateKeyPem);
      const der = key.export({ type: "pkcs8", format: "der" });
      privateKey = der.subarray(-32).toString("base64");
    }
    if (identity.publicKeyPem) {
      const key = crypto.createPublicKey(identity.publicKeyPem);
      const der = key.export({ type: "spki", format: "der" });
      publicKey = der.subarray(-32).toString("base64url");
    }
  } catch (e) {
    console.error(`Failed to read identity file: ${e.message}`);
    process.exit(1);
  }
}

if (!fs.existsSync(distDir)) {
  console.error(`dist directory not found: ${distDir}`);
  process.exit(1);
}

// -- MIME types ---------------------------------------------------------------

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".js": "application/javascript",
  ".mjs": "application/javascript",
  ".css": "text/css",
  ".json": "application/json",
  ".wasm": "application/wasm",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".gif": "image/gif",
  ".svg": "image/svg+xml",
  ".ico": "image/x-icon",
  ".glb": "model/gltf-binary",
  ".gltf": "model/gltf+json",
  ".ktx": "image/ktx",
  ".ktx2": "image/ktx2",
  ".bin": "application/octet-stream",
  ".ttf": "font/ttf",
  ".woff": "font/woff",
  ".woff2": "font/woff2",
  ".map": "application/json",
};

function mimeType(filePath) {
  return MIME[path.extname(filePath).toLowerCase()] || "application/octet-stream";
}

// -- Config injection ---------------------------------------------------------

const configScript = `<script>
window.CLAWFACE_CONFIG = {
  gatewayUrl: ${JSON.stringify(gatewayUrl)},
  gatewayToken: ${JSON.stringify(gatewayToken)},
  deviceId: ${JSON.stringify(deviceId)},
  privateKeyBase64: ${JSON.stringify(privateKey)},
  publicKeyBase64Url: ${JSON.stringify(publicKey)}
};
</script>
</head>`;

let indexHtml = null;

function getIndexHtml() {
  if (indexHtml !== null) return indexHtml;
  const raw = fs.readFileSync(path.join(distDir, "index.html"), "utf8");
  indexHtml = raw.replace("</head>", configScript);
  return indexHtml;
}

// -- COOP/COEP headers -------------------------------------------------------

const securityHeaders = {
  "Cross-Origin-Opener-Policy": "same-origin",
  "Cross-Origin-Embedder-Policy": "credentialless",
};

// -- TTS endpoint -------------------------------------------------------------

const { execFile } = require("child_process");
const os = require("os");

function handleTts(req, res) {
  let body = "";
  req.on("data", (chunk) => (body += chunk));
  req.on("end", () => {
    let text;
    try {
      text = JSON.parse(body).text || "";
    } catch {
      res.writeHead(400);
      res.end("Bad request");
      return;
    }
    if (!text.trim()) {
      res.writeHead(400);
      res.end("Missing text");
      return;
    }

    // Resolve TTS paths: --tools-dir > env vars
    const runtimeDir = toolsDir ? path.join(toolsDir, "runtime") : (process.env.SHERPA_ONNX_RUNTIME_DIR || "");
    if (!runtimeDir) {
      res.writeHead(503);
      res.end("TTS not configured (no --tools-dir or SHERPA_ONNX_RUNTIME_DIR)");
      return;
    }

    const bin = path.join(runtimeDir, "bin", "sherpa-onnx-offline-tts");
    if (!fs.existsSync(bin)) {
      res.writeHead(503);
      res.end("TTS binary not found");
      return;
    }

    // Resolve model dir: --tools-dir > env var; auto-detect first model subdir
    let modelDir = process.env.SHERPA_ONNX_MODEL_DIR || "";
    if (!modelDir && toolsDir) {
      const modelsRoot = path.join(toolsDir, "models");
      try {
        const subdirs = fs.readdirSync(modelsRoot).filter((f) =>
          fs.statSync(path.join(modelsRoot, f)).isDirectory()
        );
        if (subdirs.length >= 1) modelDir = path.join(modelsRoot, subdirs[0]);
      } catch {}
    }
    if (!modelDir) {
      res.writeHead(503);
      res.end("TTS model not found (no --tools-dir or SHERPA_ONNX_MODEL_DIR)");
      return;
    }

    // Resolve model files
    let modelFile;
    try {
      const candidates = fs.readdirSync(modelDir).filter((f) => f.endsWith(".onnx"));
      if (candidates.length === 1) modelFile = path.join(modelDir, candidates[0]);
      else { res.writeHead(503); res.end("Model not found"); return; }
    } catch { res.writeHead(503); res.end("Model dir error"); return; }

    const tokensFile = path.join(modelDir, "tokens.txt");
    const dataDir = path.join(modelDir, "espeak-ng-data");
    const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "tts-"));
    const outputPath = path.join(tmpDir, "speech.wav");

    const libDir = path.join(runtimeDir, "lib");
    const env = { ...process.env };
    env.LD_LIBRARY_PATH = libDir + (env.LD_LIBRARY_PATH ? ":" + env.LD_LIBRARY_PATH : "");

    execFile(
      bin,
      [
        `--vits-model=${modelFile}`,
        `--vits-tokens=${tokensFile}`,
        `--vits-data-dir=${dataDir}`,
        `--output-filename=${outputPath}`,
        text,
      ],
      { env, timeout: 30000 },
      (err) => {
        if (err) {
          res.writeHead(500);
          res.end(`TTS failed: ${err.message}`);
          try { fs.rmSync(tmpDir, { recursive: true }); } catch {}
          return;
        }
        try {
          const audio = fs.readFileSync(outputPath);
          res.writeHead(200, {
            ...securityHeaders,
            "Content-Type": "audio/wav",
            "Content-Length": audio.length,
          });
          res.end(audio);
        } finally {
          try { fs.rmSync(tmpDir, { recursive: true }); } catch {}
        }
      }
    );
  });
}

// -- HTTP server --------------------------------------------------------------

const server = http.createServer((req, res) => {
  // Strip query string and decode
  let urlPath = decodeURIComponent(req.url.split("?")[0]);

  // TTS endpoint
  if (urlPath === "/tts" && req.method === "POST") {
    return handleTts(req, res);
  }

  // Prevent path traversal
  if (urlPath.includes("..")) {
    res.writeHead(400);
    res.end("Bad request");
    return;
  }

  // Default to index.html
  if (urlPath === "/" || urlPath === "") {
    urlPath = "/index.html";
  }

  // Serve injected index.html
  if (urlPath === "/index.html") {
    const body = getIndexHtml();
    res.writeHead(200, {
      ...securityHeaders,
      "Content-Type": "text/html; charset=utf-8",
      "Content-Length": Buffer.byteLength(body),
      "Cache-Control": "no-cache",
    });
    res.end(body);
    return;
  }

  // Serve static files
  const filePath = path.join(distDir, urlPath);

  // Ensure resolved path is within distDir
  if (!path.resolve(filePath).startsWith(path.resolve(distDir))) {
    res.writeHead(403);
    res.end("Forbidden");
    return;
  }

  fs.stat(filePath, (err, stats) => {
    if (err || !stats.isFile()) {
      res.writeHead(404);
      res.end("Not found");
      return;
    }

    res.writeHead(200, {
      ...securityHeaders,
      "Content-Type": mimeType(filePath),
      "Content-Length": stats.size,
      "Cache-Control": "public, max-age=3600",
    });

    fs.createReadStream(filePath).pipe(res);
  });
});

server.listen(port, () => {
  console.log(`http://localhost:${port}`);
});
