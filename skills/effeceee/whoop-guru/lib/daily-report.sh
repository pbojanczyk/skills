#!/bin/bash
# Daily Report - Self-contained version

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SKILL_DIR")"

echo "🏥 Whoop Guru v6.0 - Starting..."

# Fetch data
echo "📥 Fetching WHOOP data..."
bash "$SKILL_DIR/lib/whoop-fetcher.sh" all 7

# Process data
echo "⚙️ Processing data..."
python3 "$SKILL_DIR/lib/data_processor.py"

# Show status
echo "📊 Status:"
python3 "$SKILL_DIR/lib/cli.py" status

echo "✅ Done!"
