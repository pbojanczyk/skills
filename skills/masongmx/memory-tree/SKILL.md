---
name: memory-tree
description: >
  Confidence-based memory lifecycle management for OpenClaw agents.
  Uses local Ollama embeddings for semantic search and automatic confidence decay.
  Activate when user mentions: memory management, memory tree, 记忆树,
  memory lifecycle, confidence decay, memory cleanup, 记忆治理, 记忆衰减,
  记忆健康, memory health, memory search.
  Also use for: searching long-term memory semantically, checking memory health,
  archiving stale knowledge, or managing MEMORY.md size.
---

# Memory Tree 🌳

Confidence-based memory lifecycle for OpenClaw agents. Runs on local Ollama embeddings — no cloud API, no extra cost.

## Automatic Behavior (No Manual Setup Needed)

**On install, auto-configure these via OpenClaw cron:**
1. **Index**: Every session startup, auto-index MEMORY.md changes (new knowledge blocks get registered)
2. **Decay**: Daily at 3 AM, auto-decay inactive knowledge confidence scores
3. **Cleanup**: Weekly at 4 AM Sunday, auto-archive knowledge below confidence 0.3

**Setup script (run once after install):**
```bash
python3 skills/memory-tree/scripts/memory_tree.py setup
```
This creates all cron jobs automatically. After that, everything is hands-free.

## Core Concept

Each knowledge block in MEMORY.md has a **confidence score** (0.0–1.0):

| Stage | Score | Emoji | Meaning |
|-------|-------|-------|---------|
| Sprout | 0.7 | 🌱 | New knowledge |
| Green | ≥0.8 | 🌿 | Frequently used, thriving |
| Yellow | 0.5–0.8 | 🍂 | Infrequently used, decaying |
| Dead | 0.3–0.5 | 🍁 | Rarely used, near archival |
| Soil | <0.3 | 🪨 | Archived, essence preserved |

**Key insight: forgetfulness is a feature.** Memory that's never recalled should fade.

## Commands

All commands run from workspace root. Use `exec` tool.

```bash
# Check memory tree health (most useful command)
python3 skills/memory-tree/scripts/memory_tree.py visualize

# Semantic search (auto-boosts hit confidence by +0.03)
python3 skills/memory-tree/scripts/memory_tree.py search "query"

# Mark knowledge as actively used (boosts confidence by +0.08)
python3 skills/memory-tree/scripts/memory_tree.py use <hash_prefix>

# Manual index (usually auto-run on startup)
python3 skills/memory-tree/scripts/memory_tree.py index

# Manual decay (usually auto-run daily)
python3 skills/memory-tree/scripts/memory_tree.py decay

# Check for dead leaves
python3 skills/memory-tree/scripts/memory_tree.py cleanup

# Auto-archive dead leaves
python3 skills/memory-tree/scripts/memory_tree.py cleanup --auto

# One-time setup: creates all cron jobs
python3 skills/memory-tree/scripts/memory_tree.py setup
```

## Confidence Mechanics

| Event | Change |
|-------|--------|
| New knowledge created | Set to 0.7 |
| Found by search | +0.03 |
| Actively used | +0.08 |
| Manual confirmation | Set to 0.95 |
| Each day unaccessed (P2) | -0.008 |
| Each day unaccessed (P1) | -0.004 |
| P0 (core principles) | Never decays |

Time to archive: P2 ≈ 110 days, P1 ≈ 160 days, P0 = never.

## Priority Labels

Use in MEMORY.md section headers:

```markdown
## [P0] Core Principles       # Never decays
## [P1] Important Knowledge   # Slow decay (~5 months)
## [P2] Daily Notes           # Fast decay (~3.5 months)
```

No tag = P2 (default).

## Search Backends (Auto-Detected)

Memory Tree automatically picks the best available backend at runtime:

| Priority | Backend | Cost | Requirement |
|----------|---------|------|-------------|
| 1st | **Ollama** (local) | Free | `ollama serve` + embedding model |
| 2nd | **Zhipu API** (cloud) | ~¥0.0007/1K tokens | API key in config or `ZHIPU_API_KEY` env |
| 3rd | **OpenAI-compatible** (cloud) | Varies | API key in config or `OPENAI_API_KEY` env |
| 4th | **Keyword fallback** | Free | None |

No manual backend config needed — setup auto-detects and uses the best option available. Configure manually via `memory_tree.py config backend <name>`.

## Requirements

- Python 3.8+ (stdlib only, no pip packages)
- At least one search backend (keyword mode works with zero dependencies)

## Data Files

Stored under `memory-tree/data/` in workspace:
- `confidence.json` — Confidence scores and metadata
- `embeddings.json` — Cached embedding vectors
- `archive.json` — Archived knowledge records
