#!/bin/bash
# AI Mother - Full patrol scan of all AI agents
# Outputs a structured report and updates state file
# Usage: ./patrol.sh [--quiet]

QUIET=${1:-""}
SKILL_DIR="$HOME/.openclaw/skills/ai-mother"
STATE_FILE="$SKILL_DIR/ai-state.txt"
CONTEXT_SCRIPT="$SKILL_DIR/scripts/get-ai-context.sh"
UPDATE_STATE="$SKILL_DIR/scripts/update-state.sh"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

ISSUES=()
COMPLETED=()
ACTIVE=()

[ "$QUIET" != "--quiet" ] && echo "=== AI Mother Patrol: $TIMESTAMP ==="
[ "$QUIET" != "--quiet" ] && echo ""

# Find all AI processes
AI_PROCS=$(ps aux | awk '
  /[[:space:]](claude|codex|opencode|gemini)[[:space:]]/ ||
  /[[:space:]](claude|codex|opencode|gemini)$/ {
    if ($0 !~ /grep/ && $0 !~ "ai-mother" && $0 !~ "get-ai-context") print $2
  }
')

if [ -z "$AI_PROCS" ]; then
    echo "No AI agents running."
    exit 0
fi

for PID in $AI_PROCS; do
    ps -p "$PID" > /dev/null 2>&1 || continue

    WORKDIR=$(pwdx "$PID" 2>/dev/null | cut -d: -f2 | xargs)
    STATE=$(ps -o stat= -p "$PID" | head -c 1)
    ELAPSED=$(ps -o etime= -p "$PID" | xargs)
    CMD=$(ps -o cmd= -p "$PID" | awk '{print $1}' | xargs basename)
    CPU=$(ps -o pcpu= -p "$PID" | xargs)

    # Detect AI type
    AI_TYPE="$CMD"

    # Get last output from context script
    CONTEXT=$("$CONTEXT_SCRIPT" "$PID" 2>/dev/null)
    LAST_OUTPUT=$(echo "$CONTEXT" | sed -n '/^--- Last Output ---/,/^---/p' | grep -v "^---" | head -10)
    RECENT_FILES=$(echo "$CONTEXT" | sed -n '/^--- Recent File Changes/,/^---/p' | grep -v "^---" | head -5)

    # Determine status
    STATUS="active"
    NOTES=""

    if [ "$STATE" = "T" ]; then
        STATUS="stopped"
        NOTES="Process suspended (Ctrl+Z)"
        ISSUES+=("⚠️  PID $PID ($AI_TYPE) STOPPED — $WORKDIR")

    elif echo "$LAST_OUTPUT" | grep -qi "429\|rate.limit\|rate_limit"; then
        STATUS="waiting_api"
        NOTES="Hit API rate limit (429)"
        ISSUES+=("🚫 PID $PID ($AI_TYPE) RATE LIMITED — $WORKDIR")

    elif echo "$LAST_OUTPUT" | grep -qi "permission denied\|EACCES\|not allowed"; then
        STATUS="error"
        NOTES="Permission denied error"
        ISSUES+=("❌ PID $PID ($AI_TYPE) PERMISSION ERROR — $WORKDIR")

    elif echo "$LAST_OUTPUT" | grep -qi "should i\|do you want\|shall i\|please confirm\|y/n\|yes/no"; then
        STATUS="waiting_input"
        NOTES="Waiting for confirmation"
        ISSUES+=("💬 PID $PID ($AI_TYPE) WAITING FOR INPUT — $WORKDIR")

    elif echo "$LAST_OUTPUT" | grep -qi "all done\|completed\|finished\|task complete\|done\."; then
        STATUS="completed"
        NOTES="Task appears complete"
        COMPLETED+=("✅ PID $PID ($AI_TYPE) COMPLETED — $WORKDIR")

    elif [ -z "$RECENT_FILES" ] && [ "$CPU" = "0.0" ]; then
        STATUS="idle"
        NOTES="No recent file changes, CPU idle"
        ACTIVE+=("💤 PID $PID ($AI_TYPE) IDLE — $WORKDIR (runtime: $ELAPSED)")

    else
        STATUS="active"
        NOTES="Working normally"
        ACTIVE+=("✅ PID $PID ($AI_TYPE) ACTIVE — $WORKDIR (runtime: $ELAPSED)")
    fi

    # Update state file
    TASK=$(grep "^$PID|" "$STATE_FILE" 2>/dev/null | cut -d'|' -f4)
    [ -z "$TASK" ] && TASK="unknown"
    "$UPDATE_STATE" "$PID" "$AI_TYPE" "$WORKDIR" "$TASK" "$STATUS" "$NOTES" 2>/dev/null

    # Print per-agent summary
    if [ "$QUIET" != "--quiet" ]; then
        echo "PID $PID | $AI_TYPE | $STATE | $ELAPSED | $WORKDIR"
        echo "  Status: $STATUS — $NOTES"
        if [ -n "$LAST_OUTPUT" ]; then
            echo "  Last: $(echo "$LAST_OUTPUT" | head -2 | tr '\n' ' ')"
        fi
        echo ""
    fi
done

# Print summary
if [ "$QUIET" != "--quiet" ]; then
    echo "=== Summary ==="
    [ ${#ISSUES[@]} -gt 0 ] && printf '%s\n' "${ISSUES[@]}"
    [ ${#COMPLETED[@]} -gt 0 ] && printf '%s\n' "${COMPLETED[@]}"
    [ ${#ACTIVE[@]} -gt 0 ] && printf '%s\n' "${ACTIVE[@]}"
    echo ""
fi

# Return issues for caller
if [ ${#ISSUES[@]} -gt 0 ] || [ ${#COMPLETED[@]} -gt 0 ]; then
    echo "NEEDS_ATTENTION=true"
    printf '%s\n' "${ISSUES[@]}" "${COMPLETED[@]}"
fi
