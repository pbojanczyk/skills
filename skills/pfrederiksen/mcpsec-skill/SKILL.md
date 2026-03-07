---
name: mcpsec
description: "Scan MCP server configuration files for security vulnerabilities using mcpsec (OWASP MCP Top 10). Use when: auditing MCP tool configs for prompt injection, hardcoded secrets, missing auth, insecure transport, or excessive permissions. Auto-discovers config files for Claude Desktop, Cursor, VS Code, and custom paths. Reports findings by severity. Read-only — never modifies any config."
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["mcpsec"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "shell",
              "label": "Install mcpsec (Homebrew, macOS)",
              "cmd": "brew install pfrederiksen/tap/mcpsec",
            },
            {
              "id": "binary",
              "kind": "shell",
              "label": "Install mcpsec (pre-built binary, Linux/macOS) — verify checksum before running",
              "cmd": "curl -L https://github.com/pfrederiksen/mcpsec/releases/download/v1.0.0/checksums.txt && curl -L https://github.com/pfrederiksen/mcpsec/releases/download/v1.0.0/mcpsec_1.0.0_linux_amd64.tar.gz -o /tmp/mcpsec.tar.gz && sha256sum /tmp/mcpsec.tar.gz && tar -xzf /tmp/mcpsec.tar.gz -C /tmp/ && mv /tmp/mcpsec /usr/local/bin/mcpsec",
            },
          ],
      },
  }
---

# MCPSec

Security scanner for Model Context Protocol (MCP) server configurations. Covers all 10 OWASP MCP Top 10 risk categories via [pfrederiksen/mcpsec](https://github.com/pfrederiksen/mcpsec) — an Apache 2.0 open-source Go binary.

## ⚠️ Before Installing

This skill depends on an external binary (`mcpsec`). Before using:

1. **Verify provenance** — the binary is authored by [@pfrederiksen](https://github.com/pfrederiksen). Review the source at <https://github.com/pfrederiksen/mcpsec> and confirm the release binary matches the published checksums:
   ```bash
   curl -L https://github.com/pfrederiksen/mcpsec/releases/download/v1.0.0/checksums.txt
   sha256sum mcpsec  # compare against checksums.txt
   ```

2. **Network behavior** — the skill's Python wrapper makes no network calls. The `mcpsec` binary itself reads local config files only and makes no network calls per its source code, but this skill cannot enforce that. Review the source if you need certainty.

3. **What it reads** — the scanner reads MCP config JSON files on your system (Claude Desktop, Cursor, VS Code, custom paths). It does not exfiltrate, write, or transmit these files. Run `--quiet` to suppress output when there are no findings.

4. **Isolation** — if you need stronger guarantees, run in a container or review the mcpsec source before use.

## Usage

```bash
# Auto-discover and scan all known MCP config locations
python3 scripts/scan.py

# Scan a specific config file
python3 scripts/scan.py ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Only show critical and high findings
python3 scripts/scan.py --severity critical,high

# JSON output (for dashboards/SIEM)
python3 scripts/scan.py --format json

# Quiet mode: only output if findings exist (good for cron)
python3 scripts/scan.py --quiet
```

## Installing mcpsec

```bash
# macOS (Homebrew)
brew install pfrederiksen/tap/mcpsec

# Linux/macOS — pre-built binary
curl -L https://github.com/pfrederiksen/mcpsec/releases/download/v1.0.0/mcpsec_1.0.0_linux_amd64.tar.gz -o mcpsec.tar.gz
# Verify checksum before running:
curl -L https://github.com/pfrederiksen/mcpsec/releases/download/v1.0.0/checksums.txt
sha256sum mcpsec.tar.gz
tar -xzf mcpsec.tar.gz && mv mcpsec /usr/local/bin/
```

## What It Scans

Auto-discovers configs at these paths:
- `~/Library/Application Support/Claude/claude_desktop_config.json` (Claude Desktop)
- `~/Library/Application Support/Claude/Claude Extensions/` (DXT extensions)
- `~/.cursor/mcp.json` (Cursor)
- `~/.vscode/mcp.json` (VS Code)
- `~/.openclaw/workspace/mcp-config.json` (custom)

## OWASP MCP Top 10 Coverage

| ID | Risk | Severity |
|---|---|---|
| MCP01 | Prompt injection in tool descriptions | High |
| MCP02 | Excessive tool permissions | Critical/High |
| MCP03 | Missing authentication | Critical/High |
| MCP04 | Hardcoded secrets in env vars | Critical |
| MCP05 | Unsafe resource URIs (SSRF) | High |
| MCP06 | Tool definition spoofing | High/Medium |
| MCP07 | Insecure transport (HTTP, weak TLS) | Critical/High |
| MCP08 | Missing input validation schemas | Medium |
| MCP09 | Missing logging/audit config | Medium/High |
| MCP10 | No rate limiting | Medium |

## Security Design (wrapper script)

- `subprocess` used exclusively with `shell=False`
- All file paths validated against an allowlist pattern before use
- All exceptions caught by specific type — no bare `except`
- Full type hints and docstrings throughout
- Read-only — no config files are modified

## System Access

- **Reads:** MCP config JSON files at known paths (or paths you specify)
- **Executes:** `mcpsec scan` binary — reads local config files only; no network calls per upstream source, but this cannot be enforced by the wrapper
- **No writes, no network calls from the wrapper script**
- **Sensitive data note:** config files may contain API keys or tokens; mcpsec reads them to detect hardcoded secrets but does not transmit them

## Requirements

- Python 3.10+
- `mcpsec` binary on PATH — see install instructions above
