---
name: antigravity-bridge
description: >-
  Bidirectional knowledge bridge between OpenClaw and Google Antigravity IDE.
  Sync Knowledge Items, tasks, memory, and lessons learned across both agent systems.
  Use when: (1) syncing Antigravity knowledge to OpenClaw context,
  (2) picking up tasks from .agent/tasks.md for coding sub-agents,
  (3) running cross-agent self-improve (updates both systems),
  (4) checking what Antigravity sessions produced,
  (5) creating session handoffs between agents,
  (6) user says "sync antigravity", "pick task", "what did antigravity do",
  "self-improve", "bridge sync", or "antigravity status".
  NOT for: Antigravity model/provider configuration (use google-antigravity-auth plugin),
  or starting the Antigravity IDE (use `agy` CLI directly).
homepage: https://github.com/heintonny/antigravity-bridge
metadata: {"openclaw":{"emoji":"🌉","tags":["antigravity","gemini","knowledge-sync","multi-agent","bridge","ide","tasks","coding"]}}
---

# Antigravity Bridge

Bidirectional knowledge bridge between OpenClaw and Google Antigravity IDE.
Both agents share the same knowledge, tasks, and learnings — no manual sync needed.

## Prerequisites

- Google Antigravity IDE installed (with `~/.gemini/antigravity/` directory)
- A project with `.agent/` directory (Antigravity's standard agent config)
- Python 3.10+ (for sync scripts)

## Configuration

Before first use, create a config file:

```bash
python3 "$(dirname "$0")/scripts/configure.py"
```

Or create `~/.openclaw/antigravity-bridge.json` manually:

```json
{
  "knowledge_dir": "~/.gemini/antigravity/knowledge",
  "project_dir": "~/path/to/your/project",
  "agent_dir": "~/path/to/your/project/.agent",
  "gemini_md": "~/path/to/your/project/.gemini/GEMINI.md",
  "auto_commit": false
}
```

## Commands

### Sync Knowledge (`sync`)

Pull latest Antigravity knowledge into OpenClaw context:

```bash
python3 scripts/sync_knowledge.py
```

What it does:
1. Reads all Knowledge Item (KI) summaries from `knowledge/*/metadata.json`
2. Reads `.agent/tasks.md` for current project state
3. Reads `.agent/memory/` for recent lessons learned
4. Reads `.agent/sessions/` for continuation prompts
5. Generates a summary file in your OpenClaw workspace

### Diff Tasks (`diff`)

Show what changed in tasks since last sync:

```bash
python3 scripts/diff_tasks.py
```

### Next Task (`next-task`)

Analyze project state and recommend 2-3 tasks interactively
(mirrors Antigravity's `/next-task` workflow):

**Step 1: Gather context** (run the script for raw data):
```bash
python3 scripts/pick_task.py --dry-run
```

**Step 2: Agent analysis** (do NOT just pick the first `[ ]` task):

1. Read `.agent/tasks.md` — check `[>]` (active) tasks first
2. Read `git log --oneline -15` for recent development context
3. Read relevant `.agent/memory/` files for lessons learned
4. Read KI summaries for domain awareness
5. Cross-reference: what's active? What's blocked? What's a quick win?

**Step 3: Present 2-3 recommendations** in this format:

> 🎯 **Recommended Next Tasks** — Reply with the number to start.
>
> **Option 1: [Task Name]** ⭐ (if active/in-progress)
> - Context: Why this task is recommended now
> - Scope: What's involved
> - Effort: Small / Medium / Large
>
> **Option 2: [Task Name]**
> - Context: ...
> - Scope: ...
> - Effort: ...
>
> Reply `1`, `2`, or `3` to start • `all` for details • `skip` to defer

**Step 4: On selection:**
- Mark chosen task `[>]` in tasks.md
- Create feature branch: `clawd/<task-kebab-name>`
- Load all relevant rules, memory, KIs
- Spawn coding sub-agent or begin implementation

**Priority criteria (in order):**
1. Active but incomplete (`[>]` tasks)
2. Unblocking (enables other work)
3. Quick wins (low effort, high value)
4. Technical debt
5. Natural phase progression

### Self-Improve (`self-improve`)

Update BOTH knowledge systems with session learnings:

```bash
python3 scripts/self_improve.py --topic "<topic>" --lesson "<what was learned>"
```

What it does:
1. **OpenClaw side:** Updates `MEMORY.md` and `memory/YYYY-MM-DD.md`
2. **Antigravity side:**
   - Creates/updates `.agent/memory/lessons-learned-<topic>.md`
   - Creates/updates KI artifacts in `knowledge/<topic>/artifacts/`
   - Updates `metadata.json` and `timestamps.json`
3. Optionally commits changes

### Write Knowledge Item (`write-ki`)

Write directly to Antigravity's native Knowledge Item system:

```bash
python3 scripts/write_ki.py \
  --topic "my_topic" \
  --title "My Topic" \
  --summary "What this knowledge covers" \
  --artifact "pattern_name" \
  --content "# Pattern\n\nDetailed content here..."
```

### Create Antigravity Skill (`create-agy-skill`)

Generate the reverse-direction Antigravity skill that enables
Antigravity to delegate tasks to OpenClaw:

```bash
python3 scripts/create_agy_skill.py --project-dir ~/path/to/project
```

This creates `.agent/skills/openclaw-bridge/SKILL.md` in your project,
teaching Antigravity how to communicate with OpenClaw agents.

## Architecture

For detailed architecture documentation, see [references/architecture.md](references/architecture.md).

```
┌─────────────────────┐       ┌─────────────────────┐
│    Antigravity       │       │    OpenClaw          │
│    (Gemini)          │       │    (Any LLM)         │
│                      │       │                      │
│  knowledge/       ◄──┼───────┼──► MEMORY.md         │
│  .agent/tasks.md  ◄──┼───────┼──► tasks (sub-agents)│
│  .agent/memory/   ◄──┼───────┼──► memory/*.md       │
│  .agent/sessions/ ◄──┼───────┼──► session handoffs   │
└─────────────────────┘       └─────────────────────┘
```

## Security & Privacy

- **All data stays local.** No external API calls. No cloud sync.
- Scripts only read/write files within configured directories.
- No credentials or tokens are required.
- The skill never modifies code — only knowledge/task/memory files.

## External Endpoints

None. This skill operates entirely on local files.

## Trust Statement

This skill reads and writes files within your Antigravity knowledge directory
(`~/.gemini/antigravity/`) and your project's `.agent/` directory. It does not
send any data to external services. Only install if you trust the skill to
modify these directories.
