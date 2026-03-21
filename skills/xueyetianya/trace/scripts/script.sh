#!/usr/bin/env bash
set -euo pipefail

# trace — skill script
# Powered by BytesAgain | bytesagain.com | hello@bytesagain.com

DATA_DIR="${HOME}/.trace"
mkdir -p "$DATA_DIR"

show_help() {
    cat << 'HELPEOF'
trace — command-line tool

Commands:
  start          Run start operation
  stop           Run stop operation
  search         Run search operation
  filter         Run filter operation
  tail           Run tail operation
  export         Run export operation
  stats          Run stats operation
  span           Run span operation
  context        Run context operation
  config         Run config operation
  stats      Show statistics
  export     Export data (json|csv|txt)
  search     Search across entries
  recent     Show recent entries
  status     Show current status
  help       Show this help message
  version    Show version number

Data stored in: ~/.trace/
HELPEOF
}

show_version() {
    echo "trace v1.0.0 — Powered by BytesAgain"
}

cmd_stats() {
    echo "=== trace Statistics ==="
    local total=0
    for f in "$DATA_DIR"/*.log; do
        [ -f "$f" ] || continue
        local name=$(basename "$f" .log)
        local c=$(wc -l < "$f" 2>/dev/null || echo 0)
        total=$((total + c))
        echo "  $name: $c entries"
    done
    echo "  Total: $total entries"
    echo "  Data size: $(du -sh "$DATA_DIR" 2>/dev/null | cut -f1 || echo 'N/A')"
    echo "  Since: $(head -1 "$DATA_DIR/history.log" 2>/dev/null | cut -d'|' -f1 || echo 'N/A')"
}

cmd_export() {
    local fmt="${1:-json}"
    local out="trace-export.$fmt"
    case "$fmt" in
        json)
            echo "[" > "$out"
            local first=1
            for f in "$DATA_DIR"/*.log; do
                [ -f "$f" ] || continue
                while IFS= read -r line; do
                    [ $first -eq 1 ] && first=0 || echo "," >> "$out"
                    local ts=$(echo "$line" | cut -d'|' -f1)
                    local cmd=$(echo "$line" | cut -d'|' -f2)
                    local data=$(echo "$line" | cut -d'|' -f3-)
                    printf '  {"timestamp":"%s","command":"%s","data":"%s"}' "$ts" "$cmd" "$data" >> "$out"
                done < "$f"
            done
            echo "" >> "$out"
            echo "]" >> "$out"
            ;;
        csv)
            echo "timestamp,command,data" > "$out"
            for f in "$DATA_DIR"/*.log; do
                [ -f "$f" ] || continue
                while IFS= read -r line; do
                    echo "$line" | awk -F'|' '{printf "\"%s\",\"%s\",\"%s\"\n", $1, $2, $3}' >> "$out"
                done < "$f"
            done
            ;;
        txt)
            > "$out"
            for f in "$DATA_DIR"/*.log; do
                [ -f "$f" ] || continue
                echo "--- $(basename "$f" .log) ---" >> "$out"
                cat "$f" >> "$out"
                echo "" >> "$out"
            done
            ;;
        *)
            echo "Unknown format: $fmt (use json, csv, or txt)"
            return 1
            ;;
    esac
    echo "Exported to $out ($(wc -c < "$out" 2>/dev/null || echo 0) bytes)"
}

cmd_search() {
    local term="${1:-}"
    [ -z "$term" ] && { echo "Usage: trace search <term>"; return 1; }
    echo "=== Search: $term ==="
    local found=0
    for f in "$DATA_DIR"/*.log; do
        [ -f "$f" ] || continue
        local matches=$(grep -i "$term" "$f" 2>/dev/null || true)
        if [ -n "$matches" ]; then
            echo "--- $(basename "$f" .log) ---"
            echo "$matches"
            found=$((found + 1))
        fi
    done
    [ $found -eq 0 ] && echo "No matches found."
}

cmd_recent() {
    local n="${1:-10}"
    echo "=== Recent $n entries ==="
    for f in "$DATA_DIR"/*.log; do
        [ -f "$f" ] || continue
        tail -n "$n" "$f" 2>/dev/null
    done | sort -t'|' -k1 | tail -n "$n"
}

cmd_status() {
    echo "=== trace Status ==="
    echo "  Entries: $(cat "$DATA_DIR"/*.log 2>/dev/null | wc -l || echo 0)"
    echo "  Disk: $(du -sh "$DATA_DIR" 2>/dev/null | cut -f1 || echo 'N/A')"
    local last=$(tail -1 "$DATA_DIR/history.log" 2>/dev/null || echo "never")
    echo "  Last activity: $last"
}

# Main
CMD="${1:-help}"
shift 2>/dev/null || true

case "$CMD" in
    start)
        local ts=$(date '+%Y-%m-%d %H:%M')
        echo "$ts|start|${*}" >> "$DATA_DIR/start.log"
        local total=$(wc -l < "$DATA_DIR/start.log" 2>/dev/null || echo 0)
        echo "[trace] start recorded (entry #$total)"
        ;;
    stop)
        local ts=$(date '+%Y-%m-%d %H:%M')
        echo "$ts|stop|${*}" >> "$DATA_DIR/stop.log"
        local total=$(wc -l < "$DATA_DIR/stop.log" 2>/dev/null || echo 0)
        echo "[trace] stop recorded (entry #$total)"
        ;;
    search)
        local ts=$(date '+%Y-%m-%d %H:%M')
        echo "$ts|search|${*}" >> "$DATA_DIR/search.log"
        local total=$(wc -l < "$DATA_DIR/search.log" 2>/dev/null || echo 0)
        echo "[trace] search recorded (entry #$total)"
        ;;
    filter)
        local ts=$(date '+%Y-%m-%d %H:%M')
        echo "$ts|filter|${*}" >> "$DATA_DIR/filter.log"
        local total=$(wc -l < "$DATA_DIR/filter.log" 2>/dev/null || echo 0)
        echo "[trace] filter recorded (entry #$total)"
        ;;
    tail)
        local ts=$(date '+%Y-%m-%d %H:%M')
        echo "$ts|tail|${*}" >> "$DATA_DIR/tail.log"
        local total=$(wc -l < "$DATA_DIR/tail.log" 2>/dev/null || echo 0)
        echo "[trace] tail recorded (entry #$total)"
        ;;
    export)
        local ts=$(date '+%Y-%m-%d %H:%M')
        echo "$ts|export|${*}" >> "$DATA_DIR/export.log"
        local total=$(wc -l < "$DATA_DIR/export.log" 2>/dev/null || echo 0)
        echo "[trace] export recorded (entry #$total)"
        ;;
    stats)
        local ts=$(date '+%Y-%m-%d %H:%M')
        echo "$ts|stats|${*}" >> "$DATA_DIR/stats.log"
        local total=$(wc -l < "$DATA_DIR/stats.log" 2>/dev/null || echo 0)
        echo "[trace] stats recorded (entry #$total)"
        ;;
    span)
        local ts=$(date '+%Y-%m-%d %H:%M')
        echo "$ts|span|${*}" >> "$DATA_DIR/span.log"
        local total=$(wc -l < "$DATA_DIR/span.log" 2>/dev/null || echo 0)
        echo "[trace] span recorded (entry #$total)"
        ;;
    context)
        local ts=$(date '+%Y-%m-%d %H:%M')
        echo "$ts|context|${*}" >> "$DATA_DIR/context.log"
        local total=$(wc -l < "$DATA_DIR/context.log" 2>/dev/null || echo 0)
        echo "[trace] context recorded (entry #$total)"
        ;;
    config)
        local ts=$(date '+%Y-%m-%d %H:%M')
        echo "$ts|config|${*}" >> "$DATA_DIR/config.log"
        local total=$(wc -l < "$DATA_DIR/config.log" 2>/dev/null || echo 0)
        echo "[trace] config recorded (entry #$total)"
        ;;
    stats)
        cmd_stats
        ;;
    export)
        cmd_export "$@"
        ;;
    search)
        cmd_search "$@"
        ;;
    recent)
        cmd_recent "$@"
        ;;
    status)
        cmd_status
        ;;
    help|--help|-h)
        show_help
        ;;
    version|--version|-v)
        show_version
        ;;
    *)
        echo "Unknown command: $CMD"
        echo "Run 'trace help' for usage."
        exit 1
        ;;
esac
