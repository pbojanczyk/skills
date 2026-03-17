# AI Mother 👩‍👧‍👦

**Monitor and manage AI coding agents (Claude Code, Codex, OpenCode, Gemini) running on your machine.**

AI Mother automatically detects stuck, idle, or errored AI agents and can auto-heal common issues or notify you when manual intervention is needed.

## Features

- 🔍 **Auto-discovery** - Finds all running AI agents
- 🩺 **Health monitoring** - Detects stopped, idle, rate-limited, or errored states
- 🔧 **Auto-healing** - Safely resumes stopped processes, sends Enter/Continue, requests status
- 📊 **Analytics** - Track performance, runtime, and patterns over time
- 🎛️ **Dashboard** - Real-time TUI monitoring
- 💬 **Smart notifications** - DMs you on Feishu only when attention needed

## Prerequisites

- **Python 3.7+** with pip
- **OpenClaw** with Feishu channel configured
- **AI agents** (Claude Code, Codex, OpenCode, or Gemini)

## Installation

```bash
# Install from ClawHub
clawhub install ai-mother

# Or clone manually
git clone <repo-url> ~/.openclaw/skills/ai-mother
cd ~/.openclaw/skills/ai-mother

# Install Python dependencies
pip3 install -r requirements.txt

# Run setup wizard
./scripts/setup.sh
```

## Quick Start

### 1. First-Time Setup

```bash
~/.openclaw/skills/ai-mother/scripts/setup.sh
```

This will:
- Prompt for your Feishu open_id
- Test notification delivery
- Create config.json

**How to get your Feishu open_id:**
1. Send any message to your OpenClaw bot on Feishu
2. Run: `openclaw logs --tail 20 | grep 'ou_'`
3. Look for: `received message from ou_xxxxx`
4. Copy the `ou_xxxxx` string

### 2. Manual Patrol (Check All AIs)

```bash
~/.openclaw/skills/ai-mother/scripts/patrol.sh
```

### 3. Auto-Heal Issues

```bash
# Check and fix all agents
~/.openclaw/skills/ai-mother/scripts/health-check.sh

# Fix specific agent
~/.openclaw/skills/ai-mother/scripts/auto-heal.sh <PID>

# Dry-run (preview actions)
~/.openclaw/skills/ai-mother/scripts/auto-heal.sh <PID> --dry-run
```

### 4. View Dashboard

```bash
~/.openclaw/skills/ai-mother/scripts/dashboard.sh
```

### 5. Analytics

```bash
# All agents
~/.openclaw/skills/ai-mother/scripts/analytics.py

# Specific agent
~/.openclaw/skills/ai-mother/scripts/analytics.py <PID>
```

## Automatic Monitoring

AI Mother runs patrol every 30 minutes via cron (auto-configured on first use). It will:
- Scan all AI agents
- Auto-heal safe issues
- Notify you on Feishu only when manual intervention needed

## What Gets Auto-Healed

✅ **Safe (no approval needed):**
- Resume stopped processes (with safety checks)
- Send Enter for "press enter to continue"
- Auto-confirm read-only operations
- Request status from idle AIs (>2h)
- Suggest model switch on rate limits

❌ **Always escalates to you:**
- Elevated permissions
- Destructive commands
- Code modifications
- External communications
- Financial operations

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `setup.sh` | First-time configuration wizard |
| `patrol.sh` | Scan all AI agents |
| `health-check.sh` | Quick health check + auto-heal |
| `auto-heal.sh <PID>` | Auto-fix common issues |
| `analytics.py [PID]` | Performance analytics |
| `get-ai-context.sh <PID>` | Deep context for one agent |
| `send-to-ai.sh <PID> <msg>` | Send message to AI |
| `smart-diagnose.sh <PID>` | Detect abnormal patterns |
| `dashboard.sh` | Real-time TUI dashboard |
| `notify-owner.sh <msg>` | Send Feishu DM |
| `resume-ai.sh <PID>` | Resume stopped process |

## Troubleshooting

### "No owner open_id configured"
Run setup wizard: `./scripts/setup.sh`

### "Test message failed"
Check:
- Feishu channel enabled: `openclaw config`
- Bot has message permissions in Feishu admin panel
- open_id is correct (starts with `ou_`)

### Analytics shows no data
- Database integration requires patrol to run at least once
- Run: `./scripts/patrol.sh` to populate initial data
- Check: `sqlite3 ~/.openclaw/skills/ai-mother/ai-mother.db "SELECT COUNT(*) FROM history;"`

### Dashboard won't start
Install rich library: `pip3 install rich --user`

### Auto-heal not working
- Check if process is actually stuck: `ps -p <PID>`
- Run with dry-run first: `./scripts/auto-heal.sh <PID> --dry-run`
- Check logs for safety skip reasons

## Configuration

Edit `~/.openclaw/skills/ai-mother/config.json`:

```json
{
  "owner_feishu_open_id": "ou_your_actual_id_here"
}
```

**Security note**: Never commit `config.json` to git - it contains your personal Feishu ID.

## Uninstall

```bash
# Remove cron job
openclaw cron list  # Find ai-mother-patrol job ID
openclaw cron remove <job-id>

# Remove skill
rm -rf ~/.openclaw/skills/ai-mother

# Optional: Remove data
rm -f ~/.openclaw/skills/ai-mother/ai-mother.db
rm -f ~/.openclaw/skills/ai-mother/ai-state.txt
```

## Privacy & Security

- **DM-only notifications** - Never sends to group chats
- **Local storage** - All data stays on your machine
- **No external APIs** - Only uses OpenClaw's Feishu integration
- **Conservative auto-heal** - Skips anything potentially unsafe

## Contributing

Found a bug or have a feature request? Open an issue or PR on GitHub.

## License

MIT
