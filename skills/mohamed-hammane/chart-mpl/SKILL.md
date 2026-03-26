---
name: chart-mpl
version: 1.0.0
description: Generate clear PNG charts from CSV data using matplotlib. Use when the user asks to visualize tabular data, turn SQL/CSV output into line or bar charts, or produce quick BI-ready chart images.
metadata: { "openclaw": { "emoji": "CH", "requires": { "bins": ["python3"] } } }
---

# Chart MPL

Generate chart images from CSV files with `scripts/chart_mpl.py`.

## Quick start

Run from workspace root:

```bash
~/.openclaw/workspace/.venv_chart/bin/python skills/chart-mpl/scripts/chart_mpl.py \
  --csv /path/to/data.csv \
  --xcol Mois \
  --ycol Valeur \
  --kind line \
  --title "Monthly trend" \
  --xlabel "Month" \
  --ylabel "Value"
```

Output defaults to:
`~/.openclaw/workspace/exports/images`

## Inputs

- `--csv` path to CSV file
- `--xcol` column for X axis
- `--ycol` numeric column for Y axis
- `--kind` `line` or `bar`
- Optional: `--delim` if auto-detection fails (`;`, `,`, `\t`, `|`)
- Optional: `--out` custom output path
- Optional: `--title`, `--xlabel`, `--ylabel`

## Notes

- Script auto-detects delimiters when possible.
- Script tolerates European and US numeric formats (`1 234,56`, `1,234.56`).
- Non-numeric values in `ycol` are converted to `NaN` with a warning.
- Handles BOM-encoded CSV files (`utf-8-sig`).

## End-to-end flow with SQL skill

1. Export query result to CSV using the `mssql` skill.
2. Run this script on that CSV.
3. Share the generated PNG path.
