# Group Report Outline — E-Commerce Sales Analyzer

*(Part B of Assessment 3 — 30%, target ~2,000 words. This is a SCAFFOLD with
prompts and talking points drawn from the actual code — fill in your own
analysis, screenshots, and group voice. Do not submit this outline as-is.)*

---

## 1. Problem Statement and Objectives (~250 words)

Talking points:
- Small and mid-sized online retailers accumulate sales records across many
  product categories and files, making it hard to answer basic business
  questions (best sellers, revenue trends, regional performance) without
  manual spreadsheet work.
- Objective: build a Python tool that (a) ingests transaction data scattered
  across a **nested folder-per-category** structure, (b) lets staff quickly
  **search** and **sort** records, and (c) produces **recursive category
  summaries** and **visual reports** for decision-making.
- State your own group's chosen scenario/company name if you want to frame
  it narratively (optional but often scores well for "insight").

## 2. Solution Design and Algorithmic Approach (~450 words)

Cover, for each requirement, *what algorithm you used and why*:

- **Recursive folder/category processing** — `data_loader.py`'s
  `scan_directory_recursive()` walks the `data/transactions/` tree without
  `os.walk`, recursing into each sub-directory itself, so the exact required
  "recursive processing of folders/categories" is explicit and inspectable.
  A second, independent recursion (`analytics.recursive_category_totals()`)
  builds a nested dictionary of categories → sub-categories and sums revenue
  **bottom-up**, so "Electronics" automatically reports the combined total of
  "Mobiles", "Laptops" and "Accessories" beneath it. Discuss the base case
  (a leaf node with no children) and recursive case (sum own transactions +
  recursively-computed child totals).
- **Searching** — Two algorithms, chosen for different needs:
  - *Linear search* (`search_engine.linear_search`) for product/customer
    name search, because users type partial/lower-case text and the data is
    not naturally sorted by name — O(n) but simple and correct for this use case.
  - *Binary search* (`search_engine.binary_search_exact`) for exact
    transaction-ID lookup — O(log n), but requires the list to be pre-sorted
    first (discuss this trade-off: sorting costs O(n log n) once, but repeated
    lookups then become fast).
  - Mention `build_index()` as a third option (dictionary hash lookup, O(1)
    average) and compare all three approaches' Big-O and when you'd pick each.
- **Sorting** — Hand-written **merge sort** (default) and **quick sort**
  (`sort_engine.py`), both generic over a `key_func` so the same code sorts
  by date, total value, or quantity.
  - Merge sort: O(n log n) worst-case guaranteed, stable (equal-value rows
    keep their original relative order — demonstrated in
    `test_sort_engine.py::test_merge_sort_is_stable`).
  - Quick sort: O(n log n) average, but the Lomuto last-element-pivot
    implementation degrades to O(n²) on already-sorted or reverse-sorted
    input. Discuss `test_reverse_sorted_input` as your empirical evidence,
    and consider timing both algorithms on a larger generated dataset with
    `time.perf_counter()` for a chart in this section.
- **Dictionaries, lists and file processing** — CSV rows are parsed into a
  `Transaction` dataclass; aggregate functions in `analytics.py` use
  `dict`/`collections.defaultdict`/`Counter` for O(1)-amortised grouping
  (revenue by product, by customer, by region, by month, by payment method).

## 3. Data Structures and Coding Logic Used (~350 words)

- `Transaction` dataclass (`models.py`) as the single structured record type
  used everywhere — avoids "stringly-typed" bugs and centralises validation.
- Nested dictionary **tree** for categories (explain the `__transactions__`
  sentinel key design and why it avoids clashing with real category names).
- Custom exceptions (`InvalidTransactionError`, `DataLoadError`) to separate
  *data problems* from *I/O problems* — explain how `main.py` and the tests
  react differently to each.
- Modular package structure (`modules/` split into loader / search / sort /
  analytics / visualizer / validators) — discuss single-responsibility and
  how it made unit testing each piece in isolation possible.

## 4. Testing Procedures and Results (with screenshots) (~450 words)

- State the testing framework used: Python's built-in `unittest`, 106 tests
  across 6 test files, run via `python -m unittest discover -s tests -v`.
- **Take a screenshot** of the terminal showing `Ran 106 tests ... OK` and
  paste it here.
- Describe your test strategy: for each module, you tested (a) the "happy
  path", (b) boundary conditions (empty list, single item, first/last
  element), and (c) invalid/malformed input (bad dates, negative numbers,
  missing fields, non-existent paths).
- Call out 3–4 *specific* edge cases you're proud of catching, e.g.:
  - An impossible calendar date (`2026-13-40`) is rejected even though it
    "looks" like a valid date string.
  - A completely empty CSV (header only) loads as zero transactions with no
    error, rather than crashing.
  - Quick sort is proven correct even on reverse-sorted input, its
    theoretical worst case.
  - The recursive category totals for an empty transaction list return all
    zeros instead of raising an exception.
- **Run the app itself and take 2–3 screenshots**: the main menu, a search
  result, and the recursive category revenue tree printout (`option 3`).
  Include one of the generated PNG charts too (e.g. `revenue_by_category.png`).
- Mention the intentionally-corrupted sample rows shipped in
  `Electronics/Mobiles/may_to_aug_2026.csv` and how `option 5` (Data Quality
  Report) surfaces exactly which rows were rejected and why — this is your
  evidence of end-to-end invalid-input handling, not just unit-level.

## 5. Ethical and Professional Reflections (~250 words)

Suggested angles (pick 2–3 and go deep rather than listing all shallowly):
- **Data privacy**: the sample dataset uses fictional customer names; in a
  real deployment, customer-identifiable sales data would need
  access-controls, and any exported reports/CSVs should avoid leaking
  personally identifiable information (PII) to unauthorised staff.
- **Data integrity and honesty**: the app never silently "fixes" or drops
  invalid data without telling the user — every rejected row is logged with
  a reason (`error_report`), so business decisions are never based on
  silently-corrupted figures. Discuss why this matters for trust in
  automated business tools.
- **Transparency of algorithms**: because both sorts and both searches are
  hand-written (not a black box), the group could verify correctness against
  Python's own `sorted()` — discuss why "explainable" logic matters in
  business-critical software.
- **Accessibility**: the CLI validates every input and never crashes on bad
  user input (see `validators.py`), which is a basic but important
  professional-practice / robustness consideration for software that
  non-technical staff might use.
- **Environmental/resource angle** (optional): recursion depth and O(n²)
  worst cases matter more at scale — discuss what would need to change
  (e.g. switch to iterative merge sort, or index-based search) if the
  dataset grew to millions of rows.

## 6. Reflection on Teamwork and Individual Contributions (~250 words)

*(Each member should write their own paragraph — this cannot be templated.)*
For each member, cover:
- Which module(s)/file(s) they were primarily responsible for.
- One specific technical decision they made or problem they solved.
- One thing they learned or would do differently.
- How the group coordinated (e.g. version control, shared docs, meetings).

---

## Appendix ideas
- Full test output log.
- A short table comparing merge sort vs quick sort timing on a larger
  generated dataset (you can extend `gen_data.py`'s row counts to produce
  1,000+ rows and time both algorithms).
- Screenshot of the folder structure showing the nested categories.
