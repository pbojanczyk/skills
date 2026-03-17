#!/bin/bash
# Send a message to an AI agent, reusing its existing session (no context loss)
# Supports: Claude Code (--resume), OpenCode (db inject), stdin fallback
#
# Usage:
#   ./send-to-ai.sh <PID> <message>
#   ./send-to-ai.sh <PID> --yes
#   ./send-to-ai.sh <PID> --continue
#   ./send-to-ai.sh <PID> --enter

PID=$1
MSG=$2
SKILL_DIR="$HOME/.openclaw/skills/ai-mother"
TRACKER="$SKILL_DIR/scripts/track-conversation.sh"

if [ -z "$PID" ] || [ -z "$MSG" ]; then
    echo "Usage: $0 <PID> <message|--yes|--no|--continue|--enter>"
    exit 1
fi

if ! ps -p "$PID" > /dev/null 2>&1; then
    echo "Error: Process $PID not found"
    exit 1
fi

# Check if conversation already escalated - block further messages
STATE_FILE="$SKILL_DIR/conversations/${PID}.state"
if [ -f "$STATE_FILE" ] && grep -q "ESCALATED=true" "$STATE_FILE"; then
    echo "🚨 Conversation with PID $PID has been escalated to owner"
    echo "   Cannot send more messages until owner resolves the issue"
    exit 1
fi

# Track outgoing message (skip for --enter, it's just a nudge)
if [ "$MSG" != "--enter" ] && [ -n "$TRACKER" ]; then
    "$TRACKER" "$PID" "to_baby" "$MSG"
    TRACKER_EXIT=$?
    if [ "$TRACKER_EXIT" -eq 2 ]; then
        echo "🚨 Escalated to owner - message not sent"
        exit 1
    fi
fi

CMD=$(ps -o cmd= -p "$PID" | awk '{print $1}' | xargs basename)
WORKDIR=$(pwdx "$PID" 2>/dev/null | cut -d: -f2 | xargs)

# Resolve shortcut messages
case "$MSG" in
    --enter)    SEND_MSG="" ;;
    --yes)      SEND_MSG="yes" ;;
    --no)       SEND_MSG="no" ;;
    --continue) SEND_MSG="continue" ;;
    *)          SEND_MSG="$MSG" ;;
esac

echo "AI Type: $CMD | PID: $PID | Workdir: $WORKDIR"

# ─── Claude Code: resume session ─────────────────────────────────────────────
if [ "$CMD" = "claude" ]; then
    # Find the latest session file for this workdir
    SAFE_PATH=$(echo "$WORKDIR" | sed 's|/|-|g' | sed 's|^-||')
    SESSION_DIR="$HOME/.claude/projects/$SAFE_PATH"
    LATEST_SESSION=""

    if [ -d "$SESSION_DIR" ]; then
        LATEST_FILE=$(ls -t "$SESSION_DIR"/*.jsonl 2>/dev/null | head -1)
        if [ -n "$LATEST_FILE" ]; then
            # Extract session ID from filename
            LATEST_SESSION=$(basename "$LATEST_FILE" .jsonl)
        fi
    fi

    if [ -n "$LATEST_SESSION" ] && [ -n "$SEND_MSG" ]; then
        echo "Resuming Claude session: $LATEST_SESSION"
        # Use --resume to inject message into existing session (preserves full context)
        cd "$WORKDIR" && claude \
            --resume "$LATEST_SESSION" \
            --permission-mode bypassPermissions \
            --print \
            "$SEND_MSG" &
        echo "✅ Message sent via claude --resume $LATEST_SESSION"
        exit 0
    elif [ -z "$SEND_MSG" ]; then
        # Just press Enter via stdin
        printf '\n' > "/proc/$PID/fd/0" 2>/dev/null
        echo "✅ Sent Enter to PID $PID"
        exit 0
    else
        echo "⚠️  No session found, falling back to stdin"
    fi

# ─── OpenCode: inject via stdin (interactive mode) ───────────────────────────
elif [ "$CMD" = "opencode" ]; then
    if [ -n "$SEND_MSG" ]; then
        printf '%s\n' "$SEND_MSG" > "/proc/$PID/fd/0" 2>/dev/null
        echo "✅ Sent to OpenCode PID $PID via stdin: $SEND_MSG"
    else
        printf '\n' > "/proc/$PID/fd/0" 2>/dev/null
        echo "✅ Sent Enter to OpenCode PID $PID"
    fi
    exit 0

# ─── Codex: stdin ────────────────────────────────────────────────────────────
elif [ "$CMD" = "codex" ]; then
    if [ -n "$SEND_MSG" ]; then
        printf '%s\n' "$SEND_MSG" > "/proc/$PID/fd/0" 2>/dev/null
        echo "✅ Sent to Codex PID $PID via stdin: $SEND_MSG"
    else
        printf '\n' > "/proc/$PID/fd/0" 2>/dev/null
        echo "✅ Sent Enter to Codex PID $PID"
    fi
    exit 0
fi

# ─── Fallback: stdin ─────────────────────────────────────────────────────────
if [ -n "$SEND_MSG" ]; then
    printf '%s\n' "$SEND_MSG" > "/proc/$PID/fd/0" 2>/dev/null
    echo "✅ Sent to PID $PID via stdin (fallback): $SEND_MSG"
else
    printf '\n' > "/proc/$PID/fd/0" 2>/dev/null
    echo "✅ Sent Enter to PID $PID (fallback)"
fi
