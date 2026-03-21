---
name: trace
version: "1.0.0"
description: "Track and debug application logs using CLI tracing tools. Use when you need to start trace sessions, search logs, filter by level, tail output,"
author: BytesAgain
homepage: https://bytesagain.com
source: https://github.com/bytesagain/ai-skills
tags:
  - logging
  - tracing
  - debug
  - observability
  - monitoring
---

# Trace — Log Tracing and Debugging Tool

A thorough CLI tool for application log tracing and debugging. Supports trace session management, log searching, filtering by level/time/source, real-time tailing, span tracking, context propagation, statistics, and export — all stored locally in JSONL format for easy analysis.

## Prerequisites

- Python 3.8+
- Bash shell

## Data Storage

All trace data is persisted in `~/.trace/data.jsonl`. Each line is a JSON object representing a log entry with timestamp, level, message, source, span ID, trace ID, and context metadata. Trace sessions and configuration are also stored here.

## Commands

Run all commands via the script at `scripts/script.sh`.

### `start`
Start a new trace session for capturing log entries.
```bash
bash scripts/script.sh start <session_name> [--source app-name] [--level debug|info|warn|error]
```

### `stop`
Stop an active trace session.
```bash
bash scripts/script.sh stop <session_name>
```

### `search`
Search log entries by text pattern, regex, or field values.
```bash
bash scripts/script.sh search <pattern> [--session session_name] [--level error] [--from "2024-01-01"] [--to "2024-12-31"] [--regex]
```

### `filter`
Filter log entries by level, source, time range, or custom fields.
```bash
bash scripts/script.sh filter [--level error|warn] [--source api-server] [--session session_name] [--from timestamp] [--to timestamp] [--limit 100]
```

### `tail`
Show the latest log entries in real-time-like display.
```bash
bash scripts/script.sh tail [--session session_name] [--count 20] [--level info] [--follow]
```

### `export`
Export trace data to JSON, CSV, or text format.
```bash
bash scripts/script.sh export [--session session_name] [--format json|csv|text] [--output trace-export.json] [--from timestamp] [--to timestamp]
```

### `stats`
Show statistics for trace sessions (entry counts, error rates, timeline).
```bash
bash scripts/script.sh stats [--session session_name] [--all]
```

### `span`
Create or query spans (logical groupings of related log entries).
```bash
bash scripts/script.sh span create <span_name> --session <session_name> [--parent parent_span]
bash scripts/script.sh span end <span_name> --session <session_name>
bash scripts/script.sh span list --session <session_name>
```

### `context`
Set or view context metadata for trace entries.
```bash
bash scripts/script.sh context set <key> <value> --session <session_name>
bash scripts/script.sh context get <key> --session <session_name>
bash scripts/script.sh context list --session <session_name>
```

### `config`
Configure trace settings (retention, default levels, output format).
```bash
bash scripts/script.sh config set <key> <value>
bash scripts/script.sh config get <key>
bash scripts/script.sh config list
```

### `help`
Show usage information and available commands.
```bash
bash scripts/script.sh help
```

### `version`
Show the current version of the trace tool.
```bash
bash scripts/script.sh version
```

## Workflow Example

```bash
# Start a trace session
bash scripts/script.sh start api-debug --source api-server --level debug

# Create a span for a specific operation
bash scripts/script.sh span create user-auth --session api-debug

# Set context
bash scripts/script.sh context set request_id "req-12345" --session api-debug

# View recent entries
bash scripts/script.sh tail --session api-debug --count 10

# Search for errors
bash scripts/script.sh search "connection refused" --level error

# Get statistics
bash scripts/script.sh stats --session api-debug

# Export for analysis
bash scripts/script.sh export --session api-debug --format csv --output debug-trace.csv
```

## Notes

- Trace sessions provide logical grouping for related debugging activities.
- Spans enable hierarchical structuring of trace entries (parent-child relationships).
- Context propagation allows attaching metadata (request IDs, user IDs) to entries.
- Statistics include entry counts by level, error rates, and temporal distribution.
- All data is local and can be exported for sharing or external analysis.

---

Powered by BytesAgain | bytesagain.com | hello@bytesagain.com
