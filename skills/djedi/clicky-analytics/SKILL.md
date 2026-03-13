---
name: clicky-analytics
description: Fetch website analytics from Clicky (clicky.com) via their REST API. Use when the user asks about website traffic, visitors, pageviews, top pages, bounce rate, search rankings, traffic sources, countries, or any Clicky analytics data. Also use for scheduled analytics reports or comparing traffic across date ranges.
metadata: {"openclaw":{"emoji":"📊"}}
---

# Clicky Analytics

Fetch analytics from the Clicky API. Supports multiple sites.

## Site Registry

Sites are stored in `references/sites.json`. Read this file to look up site_id and sitekey by name.

## Usage

```bash
# By site name (looks up from sites.json)
scripts/clicky.sh envelopebudget visitors,actions-pageviews

# By explicit credentials
scripts/clicky.sh --id 101427673 --key c287a01cc00f70cb visitors,actions-pageviews

# With options
scripts/clicky.sh envelopebudget pages --date last-7-days --limit 20
scripts/clicky.sh envelopebudget visitors --date 2026-03-01,2026-03-13 --daily
```

### Options
- `--date DATE` — today, yesterday, last-7-days, last-30-days, YYYY-MM-DD, or range YYYY-MM-DD,YYYY-MM-DD
- `--limit N` — max results (default 50, max 1000)
- `--daily` — break results down by day
- `--page N` — paginate through results

### Combine types in one request
Use commas to batch: `visitors,visitors-unique,actions-pageviews,bounce-rate,time-average-pretty`

## Common Reports

| Report | Types |
|--------|-------|
| Overview | `visitors,visitors-unique,actions-pageviews,bounce-rate,time-average-pretty` |
| Content | `pages,pages-entrance,pages-exit` |
| Traffic | `traffic-sources,links-domains,searches,countries` |
| SEO | `searches,searches-rankings,searches-keywords` |

## Adding Sites

Edit `references/sites.json` to add new sites:
```json
{"name": "mysite", "site_id": "12345", "sitekey": "abc123def456", "domain": "mysite.com"}
```

## API Reference

See `references/api-types.md` for all available data types, date formats, and limits.
