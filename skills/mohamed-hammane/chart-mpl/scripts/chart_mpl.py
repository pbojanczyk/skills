#!/usr/bin/env python3
import argparse
import csv
import math
import os
import re
import sys
from datetime import datetime

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except Exception:
    print("Missing dependency: matplotlib. Install with: python3 -m pip install matplotlib", file=sys.stderr)
    raise SystemExit(3)


def parse_args():
    p = argparse.ArgumentParser(description="Generate clean BI chart PNG from a CSV file.")
    p.add_argument("--csv", required=True, help="Path to CSV file")
    p.add_argument("--xcol", required=True, help="Column name for X axis")
    p.add_argument("--ycol", required=True, help="Column name for Y axis (numeric)")
    p.add_argument("--kind", choices=["line", "bar"], default="line", help="Chart type")
    p.add_argument("--title", default="", help="Chart title")
    p.add_argument("--xlabel", default="", help="X axis label")
    p.add_argument("--ylabel", default="", help="Y axis label")
    p.add_argument("--delim", default="", help="CSV delimiter (auto-detect if omitted)")
    p.add_argument("--out", default="", help="Output PNG path (default: workspace/exports/images/...)")
    return p.parse_args()


def default_out(name_hint: str) -> str:
    base = os.path.expanduser("~/.openclaw/workspace/exports/images")
    os.makedirs(base, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in (name_hint or "chart"))
    return os.path.join(base, f"{safe}_{stamp}.png")


def detect_dialect(path: str, delim: str):
    if delim:
        dialect = csv.excel()
        dialect.delimiter = delim
        return dialect
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        sample = f.read(4096)
        try:
            return csv.Sniffer().sniff(sample, delimiters=";,\t|")
        except csv.Error:
            dialect = csv.excel()
            dialect.delimiter = ";"
            return dialect


def read_csv(path: str, delim: str):
    dialect = detect_dialect(path, delim)
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, dialect=dialect)
        rows = list(reader)
    return reader.fieldnames or [], rows


def to_float(raw):
    s = str(raw or "").strip()
    if not s:
        return float("nan")

    # Normalize spaces and decimal separators (supports 1 234,56 and 1,234.56)
    s = s.replace("\u202f", "").replace("\xa0", "").replace(" ", "")
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "")
            s = s.replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        s = s.replace(",", ".")

    # Keep numeric chars only where possible
    s = re.sub(r"[^0-9.+-eE]", "", s)
    return float(s)


def main():
    a = parse_args()
    cols, rows = read_csv(a.csv, a.delim)

    if not rows:
        raise SystemExit("Empty dataset: CSV has 0 rows")

    if a.xcol not in cols or a.ycol not in cols:
        raise SystemExit(f"Missing columns. Found: {cols}")

    x = [r.get(a.xcol, "") for r in rows]
    y = []
    bad_count = 0
    for r in rows:
        try:
            value = to_float(r.get(a.ycol, ""))
        except Exception:
            value = float("nan")
        if math.isnan(value):
            bad_count += 1
        y.append(value)

    if bad_count == len(y):
        raise SystemExit(f"All values in '{a.ycol}' are non-numeric")

    if bad_count > 0:
        print(f"Warning: {bad_count} non-numeric values converted to NaN", file=sys.stderr)

    out = a.out.strip() or default_out(a.title or f"{a.ycol}_by_{a.xcol}")
    os.makedirs(os.path.dirname(out), exist_ok=True)

    plt.rcParams["font.family"] = "DejaVu Sans"
    plt.figure(figsize=(10, 5), dpi=160)
    ax = plt.gca()

    if a.kind == "bar":
        ax.bar(x, y, color="#2E6F95")
    else:
        ax.plot(x, y, marker="o", linewidth=2.2, color="#2E6F95")

    if a.title:
        ax.set_title(a.title, fontsize=14, fontweight="bold")
    ax.set_xlabel(a.xlabel or a.xcol, fontsize=11)
    ax.set_ylabel(a.ylabel or a.ycol, fontsize=11)

    ax.grid(True, axis="y", linestyle="--", linewidth=0.6, alpha=0.5)
    ax.tick_params(axis="x", labelrotation=35)
    ax.margins(x=0.02)

    plt.tight_layout()
    plt.savefig(out, bbox_inches="tight")
    print(out)


if __name__ == "__main__":
    main()
