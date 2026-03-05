# x-news-crawler flags

`./bin/x-news-crawler` wraps `abs` and emits structured JSON.

## Setup (Required)

Install and approve the global CLI build first:

```bash
pnpm add -g agent-browser-stealth
pnpm approve-builds -g
```

The JSON includes:

- `warnings`: non-fatal crawl issues (for example one eval iteration failed).
- `failed_sources`: failed source list in `hybrid` mode when partial fallback happens.

## Required

- `--query <text>`: search keyword, for example `openclaw`.

## Optional

- `--mode <hybrid|top|latest>`: default `hybrid`.
- `--since-hours <int>`: keep rows newer than this window, default `72`.
- `--limit <int>`: max output rows, default `30`.
- `--scrolls <int>`: page-down rounds before extraction, default `4`.
- `--output <file>`: write JSON to file; if omitted, print to stdout.
- `--session-prefix <text>`: default `xnews`.
- `--help`: print help.

## Debug

- `X_NEWS_FORCE_FAIL_SOURCE=top|latest`: force one source to fail for fallback testing.

## Example

```bash
./bin/x-news-crawler \
  --query "openclaw" \
  --mode hybrid \
  --since-hours 72 \
  --limit 30 \
  --output .tmp/openclaw-news.json
```
