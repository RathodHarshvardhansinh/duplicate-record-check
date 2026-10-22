# Audit Note - Duplicate Record Check

Generated: 22 Oct 2026, 05:41
Input file: `sample_test.csv`

## Method
- Trimmed leading/trailing whitespace in text columns before comparing.
- **Exact duplicates:** every column identical (ignored surrogate ID column(s): Row ID). First occurrence kept, later copies removed.
- **Key duplicates:** same key (Order ID, Product ID) but other values differ. Flagged for manual review, **not** removed automatically.

## Results
| Check | Count |
|---|---|
| Total rows (input) | 7 |
| Exact duplicate rows removed | 2 |
| Rows involved in exact-duplicate groups | 4 |
| Key-duplicate rows needing review | 2 |
| Total rows (cleaned) | 5 |

## Impact on totals
| Metric | Before | After | Overstated by | % |
|---|---|---|---|---|
| Sales | 642.00 | 342.00 | 300.00 | 46.73% |
| Quantity | 10.00 | 7.00 | 3.00 | 30.00% |
| Profit | 66.00 | 36.00 | 30.00 | 45.45% |

## Decision log
- Removed: exact copies only.
- Kept for review: key-only duplicates (may be legitimate, e.g. the same product on separate lines of one order).
- Original file untouched; cleaned copy saved as `output/cleaned_data.csv`.
