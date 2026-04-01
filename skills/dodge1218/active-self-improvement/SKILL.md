---
name: active-self-improvement
version: 1.2.0
description: Active self-improvement loop that reads learnings, errors, batch outputs, and memory — detects patterns — and UPDATES skills/protocols/behavior automatically. Use when the agent should get smarter without being prompted. Different from passive logging — this ACTS on what it learns.
---

# Auto-Improve v1.1.0

> The missing piece between logging and intelligence. Most self-improvement skills passively log errors. This one reads the logs, detects patterns, and rewrites the playbook.

## What's New in v1.1.0
- Added `--dry-run` mode: propose changes without applying them
- Improved pattern detection: now catches 3-occurrence threshold (was 2)
- Added recurrence tracking with `Pattern-Key` and `Recurrence-Count` metadata
- Better risk classification: separates reversible edits from permanent changes
- Simplified trigger conditions for cleaner integration with Recorder skill

## How It Works

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  SCAN       │────▶│  PROPOSE     │────▶│  APPLY      │
│  Read logs, │     │  Write       │     │  Low-risk:  │
│  find       │     │  specific    │     │  auto-apply │
│  patterns   │     │  changes     │     │  High-risk: │
│             │     │              │     │  flag user  │
└─────────────┘     └──────────────┘     └─────────────┘
```

## What This Is NOT
- **NOT a logging skill** — that's `self-improving-agent` (passive, writes notes)
- **NOT a memory manager** — that's `memory-guardian` (manages files)
- This is the **brain that reads the notes and rewrites the playbook.**

## When It Triggers
- End of every meaningful work session (after Recorder)
- After batch processing meta-think cycles
- After any project completion or milestone
- On explicit "improve" or "what have we learned" prompts
- Optionally: on a cron schedule for continuous background improvement

## Input Sources
The skill reads from these files before proposing any changes:

| Source | What It Contains |
|--------|-----------------|
| `.learnings/ERRORS.md` | What broke and how it was fixed |
| `.learnings/LEARNINGS.md` | Corrections, insights, knowledge gaps |
| `systems/batch-cognition/learnings.md` | What worked/wasted in batch processing |
| `systems/batch-cognition/value-stack.md` | Ranked ideas across all batches |
| `memory/permanent/*.md` | Current knowledge state |
| Recent session memory | What happened in the last few sessions |

## The Loop

### Step 1: SCAN
Read all input sources. Detect:
- **Repeated errors** — same mistake 3+ times → needs a prevention rule
- **Repeated corrections** — user keeps fixing the same thing → behavior change needed
- **Emerging patterns** — 3+ items connecting → thesis forming
- **Stale knowledge** — facts in permanent memory contradicted by recent sessions
- **Unused wins** — high-value items that haven't been acted on

### Step 2: PROPOSE
For each detected pattern, write a concrete proposal:

```
PROPOSAL: [short title]
EVIDENCE: [what triggered this — file#line references]
CHANGE: [exact edit — old text → new text, or new file content]
RISK: [low/medium/high — what could go wrong]
REVERSIBLE: [yes/no — can we undo easily]
```

| Pattern Type | Action | Target File |
|-------------|--------|-------------|
| Repeated error | Add prevention rule | `TOOLS.md` or relevant skill |
| Repeated correction | Update behavior guideline | `SOUL.md` or `AGENTS.md` |
| Emerging thesis | Write thesis doc + next steps | `OUTSTANDING.md` |
| Stale knowledge | Update the fact | `memory/permanent/*.md` |
| Unused win | Create ticket or reminder | `NEXT_TICKET.md` or cron |

### Step 3: APPLY
- **Low risk + reversible**: Apply immediately. Log the change.
- **Medium risk**: Apply but notify user on next interaction.
- **High risk**: Write to `OUTSTANDING.md` and wait for approval.
- **Dry-run mode**: Propose all changes but apply none. Output a report.

## Installation

```bash
npx clawhub install dodge1218/active-self-improvement
```

Or manually:
```bash
git clone https://github.com/dodge1218/active-self-improvement.git ~/.openclaw/skills/auto-improve
```

## Configuration

No configuration required. The skill reads from standard OpenClaw workspace files.

Optional: add to your `AGENTS.md` to auto-trigger after Recorder:
```markdown
### Auto-Improve
Runs after Recorder. Scans learnings, proposes behavior updates.
```

## Compatibility
- OpenClaw 2026.3+
- Works alongside: `self-improving-agent` (logging), `memory-guardian` (memory health), `recorder` (state capture)
- Does NOT conflict with any other skill

## Changelog

### v1.1.0 (2026-03-31)
- Added dry-run mode for safe proposal review
- Improved pattern detection (3-occurrence threshold)
- Added recurrence tracking metadata
- Better risk classification
- Cleaner trigger integration

### v1.0.0 (2026-03-30)
- Initial release
- SCAN → PROPOSE → APPLY loop
- Reads from `.learnings/`, batch-cognition, memory
- Auto-applies low-risk changes, flags high-risk

## License
MIT
