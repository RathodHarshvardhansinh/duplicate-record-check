"""
Task 13 - Duplicate Record Check (Data Analytics)

Finds duplicate records in a dataset (e.g. Superstore / Retail Sales),
documents them, and writes a cleaned copy plus an audit note.

Usage:
    python duplicate_check.py --input Sample-Superstore.csv
    python duplicate_check.py --input Sample-Superstore.csv --key "Order ID,Product ID"
    python duplicate_check.py --input data.xlsx --ignore "Row ID"

Outputs (in ./output):
    duplicate_report.csv   every row that belongs to a duplicate group
    duplicate_report.xlsx  same report in Excel
    cleaned_data.csv       dataset with exact duplicates removed (first kept)
    audit_note.md          counts, impact on totals, method used
"""
import argparse
import os
import sys
from datetime import datetime

import pandas as pd


def load(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in (".xlsx", ".xls"):
        return pd.read_excel(path)
    for enc in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return pd.read_csv(path, encoding=enc)
        except UnicodeDecodeError:
            continue
    raise ValueError("Could not decode file")


def trim_text(df):
    """Strip whitespace so 'A ' and 'A' are treated as the same value."""
    df = df.copy()
    for c in df.select_dtypes(include=["object", "string"]).columns:
        df[c] = df[c].where(df[c].isna(), df[c].astype(str).str.strip())
    return df


def pick_key(df, requested):
    if requested:
        cols = [c.strip() for c in requested.split(",")]
        missing = [c for c in cols if c not in df.columns]
        if missing:
            sys.exit(f"Key column(s) not found: {missing}\nAvailable: {list(df.columns)}")
        return cols
    for cand in (["Order ID", "Product ID"], ["Order ID"], ["Transaction ID"], ["Invoice"]):
        if all(c in df.columns for c in cand):
            return cand
    return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--key", default=None, help="comma-separated key columns")
    ap.add_argument("--ignore", default="Row ID",
                    help="comma-separated surrogate-ID columns ignored in the full-row check")
    ap.add_argument("--out", default="output")
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    raw = load(a.input)
    df = trim_text(raw)
    n = len(df)

    ignore = [c.strip() for c in a.ignore.split(",") if c.strip() in df.columns]
    compare_cols = [c for c in df.columns if c not in ignore]
    key_cols = pick_key(df, a.key)

    # 1) Exact duplicates: all columns identical (except ignored surrogate IDs)
    exact_extra = df.duplicated(subset=compare_cols, keep="first")   # copies to remove
    exact_any = df.duplicated(subset=compare_cols, keep=False)       # every row in a group

    # 2) Key duplicates: same key but values differ -> manual review
    if key_cols:
        key_any = df.duplicated(subset=key_cols, keep=False)
        key_only = key_any & ~exact_any
    else:
        key_any = pd.Series(False, index=df.index)
        key_only = key_any

    # Duplicate report
    flagged = exact_any | key_only
    report = df[flagged].copy()
    report.insert(0, "Source Row (Excel)", report.index + 2)  # header row + 1-based
    report["Duplicate Type"] = "Key duplicate (review)"
    report.loc[exact_any[flagged] , "Duplicate Type"] = "Exact duplicate"
    report["Action"] = "Kept - review"
    report.loc[exact_extra[flagged], "Action"] = "Removed (exact copy)"
    report.loc[exact_any[flagged] & ~exact_extra[flagged], "Action"] = "Kept (first occurrence)"
    sort_cols = (key_cols if key_cols else compare_cols[:1]) + ["Source Row (Excel)"]
    report = report.sort_values(sort_cols)

    report.to_csv(os.path.join(a.out, "duplicate_report.csv"), index=False)
    report.to_excel(os.path.join(a.out, "duplicate_report.xlsx"), index=False)

    # Cleaned copy: remove exact duplicates only (original, untrimmed values kept)
    cleaned = raw.loc[~exact_extra]
    cleaned.to_csv(os.path.join(a.out, "cleaned_data.csv"), index=False)

    # Impact on totals
    impact = []
    for col in ("Sales", "Quantity", "Profit", "Amount", "Revenue"):
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            before, after = df[col].sum(), cleaned[col].sum()
            diff = before - after
            pct = diff / before * 100 if before else 0
            impact.append(f"| {col} | {before:,.2f} | {after:,.2f} | {diff:,.2f} | {pct:.2f}% |")
    impact_txt = "\n".join(impact) if impact else "| (no numeric metric columns found) | | | | |"

    key_txt = ", ".join(key_cols) if key_cols else "none defined"
    ign_txt = f" (ignored surrogate ID column(s): {', '.join(ignore)})" if ignore else ""
    note = f"""# Audit Note - Duplicate Record Check

Generated: {datetime.now().strftime('%d %b %Y, %H:%M')}
Input file: `{os.path.basename(a.input)}`

## Method
- Trimmed leading/trailing whitespace in text columns before comparing.
- **Exact duplicates:** every column identical{ign_txt}. First occurrence kept, later copies removed.
- **Key duplicates:** same key ({key_txt}) but other values differ. Flagged for manual review, **not** removed automatically.

## Results
| Check | Count |
|---|---|
| Total rows (input) | {n:,} |
| Exact duplicate rows removed | {int(exact_extra.sum()):,} |
| Rows involved in exact-duplicate groups | {int(exact_any.sum()):,} |
| Key-duplicate rows needing review | {int(key_only.sum()):,} |
| Total rows (cleaned) | {len(cleaned):,} |

## Impact on totals
| Metric | Before | After | Overstated by | % |
|---|---|---|---|---|
{impact_txt}

## Decision log
- Removed: exact copies only.
- Kept for review: key-only duplicates (may be legitimate, e.g. the same product on separate lines of one order).
- Original file untouched; cleaned copy saved as `output/cleaned_data.csv`.
"""
    with open(os.path.join(a.out, "audit_note.md"), "w", encoding="utf-8") as f:
        f.write(note)
    print(note)


if __name__ == "__main__":
    main()
