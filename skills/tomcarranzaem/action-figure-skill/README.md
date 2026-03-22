# AI Action Figure Generator

Turn any text description into a hyperrealistic **AI action figure toy packaging** image — complete with blister pack, accessories, and product label. Powered by the Neta talesofai API.

---

## Install

**Via npx skills:**
```bash
npx skills add TomCarranzaem/action-figure-skill
```

**Via ClawHub:**
```bash
clawhub install action-figure-skill
```

---

## Usage

```bash
# Use the default action figure prompt
node actionfigure.js

# Custom description
node actionfigure.js "Iron Man action figure in red and gold armor, blister pack packaging"

# Portrait size (default) with cinematic style
node actionfigure.js "astronaut action figure, NASA suit, accessories included" --size portrait

# Landscape format
node actionfigure.js "pirate captain collectible figurine, treasure chest accessory" --size landscape

# Reference an existing image UUID for style inheritance
node actionfigure.js "robot warrior action figure" --ref <picture_uuid>
```

The command prints a direct image URL to stdout on success.

---

## Options

| Flag | Values | Default | Description |
|------|--------|---------|-------------|
| `--size` | `portrait`, `landscape`, `square`, `tall` | `portrait` | Output image dimensions |
| `--token` | string | — | Override API token (see Token Setup) |
| `--ref` | picture_uuid | — | Inherit style from an existing image |

### Size dimensions

| Size | Width × Height |
|------|---------------|
| `square` | 1024 × 1024 |
| `portrait` | 832 × 1216 |
| `landscape` | 1216 × 832 |
| `tall` | 704 × 1408 |

---

## Token Setup

The script resolves your `NETA_TOKEN` in this order:

1. `--token <value>` CLI flag
2. `NETA_TOKEN` environment variable
3. `~/.openclaw/workspace/.env` (line matching `NETA_TOKEN=...`)
4. `~/developer/clawhouse/.env` (line matching `NETA_TOKEN=...`)

**Recommended:** add to your shell profile or `.env` file:
```bash
export NETA_TOKEN=your_token_here
```

Or store in `~/.openclaw/workspace/.env`:
```
NETA_TOKEN=your_token_here
```

---

## Default Prompt

When no description is provided, the following prompt is used:

> 3D action figure of a person sealed inside a retail blister pack toy box, collectible figurine packaging, accessories included, product name label on box, hyperrealistic 3D render, studio product photography lighting, toy store shelf aesthetic

---

## Example Output

The script prints a single image URL, e.g.:
```
https://cdn.talesofai.cn/artifacts/abc123.png
```

Pipe it into your workflow, open it in a browser, or download with `curl`.

---

Built with Claude Code · Powered by Neta
