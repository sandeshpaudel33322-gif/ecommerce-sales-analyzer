# E-Commerce Sales Analyzer

A Python data-analysis application built for **Assessment 3 – Applied Python
Programming Project** (Part A: Python Implementation, 50%). It recursively
reads sales transaction records from a nested folder structure, lets users
search and sort the data, and produces business summaries and charts.

> **Reminder:** this is a **group assignment**. Before submission, add every
> group member's name to the report and presentation, agree on who explains
> which module in the presentation, and make sure the report's "Reflection on
> teamwork and individual contributions" section is written honestly and
> individually. A single-member submission scores zero regardless of code
> quality, per the assignment brief.

## 1. What this project demonstrates (mapped to the rubric)

| Rubric criterion | Where it's demonstrated |
|---|---|
| **Algorithm Design & Implementation** (recursion, searching, sorting) | `modules/data_loader.py` (recursive folder scan), `modules/analytics.py` (recursive category-tree totals), `modules/search_engine.py` (linear + binary search), `modules/sort_engine.py` (merge sort + quick sort, hand-written) |
| **Software Engineering Best Practices** | Modular package layout, docstrings on every module/function, custom exceptions, type hints, single-responsibility files |
| **Testing & Validation** | `tests/` — 106 automated `unittest` tests covering happy paths **and** edge cases |
| **Group Report Quality / Ethical & Professional Analysis** | See `docs/report_outline.md` for a ready-to-fill structure and talking points |

## 2. Project structure

```
ecommerce_sales_analyzer/
├── main.py                    # Interactive CLI entry point
├── requirements.txt
├── README.md
├── docs/
│   └── report_outline.md      # Scaffold for the 2,000-word Part B report
├── data/
│   └── transactions/          # Sample data, organised as nested category folders
│       ├── Electronics/
│       │   ├── Mobiles/*.csv
│       │   ├── Laptops/*.csv
│       │   └── Accessories/*.csv
│       ├── Clothing/{Men,Women,Kids}/*.csv
│       ├── Groceries/{Beverages,Snacks,Frozen}/*.csv
│       └── HomeAndFurniture/*.csv
├── modules/
│   ├── models.py               # Transaction dataclass + validation
│   ├── data_loader.py           # RECURSIVE folder scan + CSV loading
│   ├── search_engine.py         # Linear search + binary search + dict index
│   ├── sort_engine.py            # Merge sort + quick sort (generic, by key)
│   ├── analytics.py               # Business stats + RECURSIVE category totals
│   ├── visualizer.py               # matplotlib charts (bar/line/pie)
│   └── validators.py                # CLI input validation helpers
├── tests/                       # 106 unit tests (unittest)
│   ├── test_models.py
│   ├── test_data_loader.py
│   ├── test_search_engine.py
│   ├── test_sort_engine.py
│   ├── test_analytics.py
│   └── test_validators.py
├── reports/                     # Output folder for generated charts/CSV (created at runtime)
└── gen_data.py                  # Optional: regenerates the sample dataset
```

## 3. Setup

Requires Python 3.9+.

```bash
cd ecommerce_sales_analyzer
pip install -r requirements.txt
```

## 4. Running the application

```bash
python main.py
```

You will see a menu:

```
================ MAIN MENU ================
1. Search transactions
2. Sort transactions
3. Business summary & graphs
4. Reload data
5. Data quality / rejected rows report
0. Exit
```

On startup the app **recursively scans** `data/transactions/` (including
every nested sub-folder) for `.csv` files, validates every row, and reports
how many transactions loaded successfully vs. how many rows were rejected
and why (option 5).

### Search (option 1)
- Search by **product** or **customer** — case-insensitive, partial-match
  linear search across all loaded transactions.
- Search by **transaction ID** — exact match using **binary search** on a
  copy of the data sorted by ID (O(log n) lookup).

### Sort (option 2)
- Sort by **date**, **sales value (total)**, or **quantity**, ascending or
  descending, using a hand-written **merge sort** (the app's default —
  `modules/sort_engine.py` also includes an equivalent **quick sort** you can
  call directly for comparison/testing).

### Business summary & graphs (option 3)
- Headline numbers: total revenue, units sold, transaction count, average
  order value.
- Top 5 products and top 5 customers by revenue.
- Payment method breakdown.
- A **recursively computed** category revenue tree (e.g. "Electronics"
  automatically rolls up "Mobiles" + "Laptops" + "Accessories").
- Optional: generate 4 PNG charts into `reports/` (revenue by category,
  monthly trend, region share pie chart, top products) and/or export the
  summary to `reports/business_summary.csv`.

### Data quality report (option 5)
Lists every row that failed validation during loading, with the file, line
number, and reason (bad date, negative quantity, missing field, etc.) — this
is the evidence trail for the "invalid input & edge-case handling" rubric
criterion.

## 5. Running the automated tests

```bash
python -m unittest discover -s tests -v
```

All 106 tests should pass. They cover:
- **Recursion**: nested folder scanning at arbitrary depth, empty folders,
  non-existent paths, recursive category-tree totals (including a 3-level
  deep category and roll-up correctness).
- **Searching**: exact/partial matches, no-match, empty dataset, empty/whitespace
  search terms, binary search on first/last/missing elements.
- **Sorting**: both algorithms checked against Python's built-in `sorted()`
  for every business key, plus empty list, single item, already-sorted,
  and reverse-sorted (quick sort worst case) inputs, stability, and
  non-mutation of the input list.
- **Invalid input / edge cases**: missing fields, non-numeric quantity/price,
  negative values, impossible calendar dates, empty transaction IDs, empty
  files, blank trailing rows, and non-CSV files mixed into the data tree.

## 6. Regenerating sample data (optional)

The `data/transactions/` folder already ships with ~230 synthetic
transactions (including a handful of intentionally invalid rows for testing
purposes). To regenerate a fresh random set:

```bash
python gen_data.py
```

## 7. Suggested talking points for the group report / presentation

See `docs/report_outline.md` for a full section-by-section scaffold,
including specific things to say about:
- why merge sort was chosen as the default (stable, predictable O(n log n))
  vs. quick sort's O(n²) worst case on already-sorted/reverse-sorted input;
- why binary search requires pre-sorted data and the trade-off vs. a
  dictionary index (`search_engine.build_index`);
- how the recursive category tree mirrors a real business reporting
  hierarchy;
- ethical considerations: data privacy of customer names, honesty in
  reported figures, accessibility of the CLI, and responsible handling of
  malformed/untrusted input data.
