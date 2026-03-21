---
name: claw-self-improvement
description: "Injects claw-self-improvement reminder during agent bootstrap"
metadata: {"openclaw":{"emoji":"🧠","events":["agent:bootstrap"]}}
---

# Claw Self-Improvement Hook

Injects a reminder to evaluate learnings during agent bootstrap.

## What It Does

- Fires on `agent:bootstrap` (before workspace files are injected)
- Adds a reminder block to check `.learnings/` for relevant entries
- Prompts the agent to log corrections, errors, and discoveries
- Prompts the agent to distill proven patterns into `.learnings/PROMOTED.md`

## Configuration

No configuration needed. Enable with:

```bash
openclaw hooks enable claw-self-improvement
```
