---
name: helm
version: 1.0.0
author: BytesAgain
license: MIT-0
tags: [helm, tool, utility]
---

# Helm

Helm chart toolkit — create, lint, template, package, and manage Kubernetes charts.

## Commands

| Command | Description |
|---------|-------------|
| `helm help` | Show usage info |
| `helm run` | Run main task |
| `helm status` | Check current state |
| `helm list` | List items |
| `helm add <item>` | Add new item |
| `helm export <fmt>` | Export data |

## Usage

```bash
helm help
helm run
helm status
```

## Examples

```bash
# Get started
helm help

# Run default task
helm run

# Export as JSON
helm export json
```

## Output

Results go to stdout. Save with `helm run > output.txt`.

## Configuration

Set `HELM_DIR` to change data directory. Default: `~/.local/share/helm/`

---
*Powered by BytesAgain | bytesagain.com*
*Feedback & Feature Requests: https://bytesagain.com/feedback*
