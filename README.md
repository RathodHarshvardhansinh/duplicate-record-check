# Task 13 - Duplicate Record Check

**Internship:** Veda Technology - Data Analytics Track (Level 1, Day 13)
**Tools:** Python (Pandas), Excel
**Dataset:** Superstore / Retail Sales (any CSV or XLSX works)

## Objective
Understand duplicate detection: find duplicate records, document them, and show how they distort reported totals.

## Approach
1. **Load and standardise** - read the CSV/XLSX and trim stray whitespace in text columns so `"Desk "` and `"Desk"` match.
2. **Exact duplicates** - rows where every column is identical, ignoring a surrogate ID column such as `Row ID` (which is unique even for copied rows). The first occurrence is kept; later copies are removed.
3. **Key duplicates** - rows sharing the same business key (default `Order ID + Product ID`) but with different values. These are flagged for **manual review** and not auto-deleted, since they can be legitimate (e.g. separate order lines).
4. **Impact check** - compare Sales / Quantity / Profit before vs after cleaning to show how duplicates inflate totals.
5. **Audit note** - every decision is written to `audit_note.md`.

## Deliverables
| File | Description |
|---|---|
| `duplicate_check.py` | Reusable script |
| `output/duplicate_report.csv` / `.xlsx` | All rows in duplicate groups, with type and action taken |
| `output/cleaned_data.csv` | Cleaned copy (exact duplicates removed) |
| `output/audit_note.md` | Method, counts, impact on totals, decision log |

## How to run
```bash
pip install -r requirements.txt
python duplicate_check.py --input Sample-Superstore.csv
```
Options:
```bash
--key "Order ID,Product ID"   # choose your own key columns
--ignore "Row ID"             # surrogate ID columns to ignore in the exact check
--out output                  # output folder
```
A tiny demo file, `sample_test.csv`, is included so you can try it instantly:
```bash
python duplicate_check.py --input sample_test.csv
```

## Interview questions
**What is a duplicate row?**
A record that repeats another record's data. An exact duplicate matches on every field. A partial/key duplicate matches on the identifying fields (e.g. Order ID) but differs elsewhere.

**How can duplicates affect totals?**
They double-count. Sales, quantity and profit are overstated, averages and counts are skewed, and downstream KPIs, forecasts and customer metrics become unreliable. In the demo data, 2 duplicate rows overstated sales by ~46%.

## Key learnings
- Check **full rows and key columns** separately; they answer different questions.
- Ignore surrogate IDs (`Row ID`) or exact duplicates will never be detected.
- Don't blindly delete: flag ambiguous cases and keep an **audit note**.
- Always quantify the impact on totals before and after cleaning.

## Results on the demo file
Run on `sample_test.csv` (7 rows): 2 exact duplicates removed, 2 key-duplicate rows flagged for review, 5 rows in the cleaned copy.
