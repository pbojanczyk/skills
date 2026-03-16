---
name: count
version: 1.0.0
author: BytesAgain
license: MIT-0
tags: [count, tool, utility]
---

# Count

Count toolkit — word count, line count, character frequency, and file statistics.

## Commands

| Command | Description |
|---------|-------------|
| `count help` | Show usage info |
| `count run` | Run main task |
| `count status` | Check state |
| `count list` | List items |
| `count add <item>` | Add item |
| `count export <fmt>` | Export data |

## Usage

```bash
count help
count run
count status
```

## Examples

```bash
count help
count run
count export json
```

## Output

Results go to stdout. Save with `count run > output.txt`.

## Configuration

Set `COUNT_DIR` to change data directory. Default: `~/.local/share/count/`

---
*Powered by BytesAgain | bytesagain.com*
*Feedback & Feature Requests: https://bytesagain.com/feedback*
