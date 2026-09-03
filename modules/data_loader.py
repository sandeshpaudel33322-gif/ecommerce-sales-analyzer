"""
data_loader.py
---------------
Handles RECURSIVE traversal of the transaction-data folder tree and
loading of individual CSV files into validated Transaction objects.

The dataset is organised as nested "transaction category" folders, e.g.

    data/transactions/
        Electronics/
            Mobiles/
                jan_to_apr_2026.csv
                may_to_aug_2026.csv
            Laptops/
                ...
        Clothing/
            Men/
                ...
            Women/
                ...
        HomeAndFurniture/
            ...

`scan_directory_recursive()` walks this tree WITHOUT using os.walk, to
explicitly demonstrate the recursion required by the assignment brief:
it recurses into every sub-folder itself, and derives each file's
"category" from its path relative to the root
(e.g. "Electronics/Mobiles").
"""

import os
import csv
from typing import List, Tuple

from modules.models import Transaction, InvalidTransactionError, DataLoadError


def scan_directory_recursive(root_path: str) -> List[Tuple[str, str]]:
    """
    Recursively scan `root_path` for `.csv` files.

    Returns
    -------
    List of (file_path, category) tuples, where `category` is the
    folder path relative to `root_path` using "/" as a separator
    (e.g. "Electronics/Mobiles"). Top-level files get category "General".

    This function is intentionally recursive (calls itself on each
    sub-directory) rather than using os.walk, per the assignment
    requirement to demonstrate recursive folder processing.
    """
    if not os.path.isdir(root_path):
        raise DataLoadError(f"'{root_path}' is not a valid directory.")

    results: List[Tuple[str, str]] = []
    _scan_recursive_helper(root_path, root_path, results)
    return results


def _scan_recursive_helper(current_path: str, root_path: str, results: List[Tuple[str, str]]) -> None:
    """Recursive worker for scan_directory_recursive (base case = no sub-entries left)."""
    try:
        entries = sorted(os.listdir(current_path))
    except PermissionError:
        # Edge case: unreadable directory - skip it but don't crash the whole scan
        print(f"  [WARN] Permission denied reading '{current_path}', skipping.")
        return

    # Base case: an empty directory simply contributes nothing and the
    # recursion for this branch ends here.
    if not entries:
        return

    for entry in entries:
        full_path = os.path.join(current_path, entry)

        if os.path.isdir(full_path):
            # Recursive case: descend into the sub-folder
            _scan_recursive_helper(full_path, root_path, results)
        elif os.path.isfile(full_path) and entry.lower().endswith(".csv"):
            rel_dir = os.path.relpath(current_path, root_path)
            category = "General" if rel_dir == "." else rel_dir.replace(os.sep, "/")
            results.append((full_path, category))
        # any other file type is silently ignored (edge case: non-csv files present)


def load_csv_file(file_path: str, category: str):
    """
    Load a single CSV file into a list of validated Transaction objects.

    Malformed rows are NOT allowed to crash the whole load: each row is
    validated independently, bad rows are collected as (row_number, error)
    pairs and returned alongside the successfully parsed transactions, so
    the caller (and the test suite) can inspect exactly what failed.

    Returns
    -------
    (transactions, errors) : (List[Transaction], List[Tuple[int, str]])
    """
    transactions = []
    errors = []

    try:
        with open(file_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for line_number, row in enumerate(reader, start=2):  # header = line 1
                # Edge case: completely blank row (e.g. trailing newline, all-empty row)
                if row is None or all((v is None or str(v).strip() == "") for v in row.values()):
                    continue
                try:
                    txn = Transaction.from_row(row, category=category, source_file=file_path)
                    transactions.append(txn)
                except InvalidTransactionError as exc:
                    errors.append((line_number, str(exc)))
    except FileNotFoundError as exc:
        raise DataLoadError(f"File not found: {file_path}") from exc
    except UnicodeDecodeError as exc:
        raise DataLoadError(f"Could not decode file as UTF-8: {file_path} ({exc})") from exc
    except csv.Error as exc:
        raise DataLoadError(f"CSV parsing error in {file_path}: {exc}") from exc

    return transactions, errors


def load_all_transactions(root_path: str, verbose: bool = True):
    """
    Recursively scan `root_path` and load every transaction found.

    Returns
    -------
    (transactions, error_report) where:
      transactions  : List[Transaction]  -- all successfully validated rows
      error_report  : List[dict]         -- one entry per file with any
                                             rejected rows, for the
                                             "invalid input handling" report
    """
    files = scan_directory_recursive(root_path)
    if verbose:
        print(f"Recursive scan found {len(files)} CSV file(s) under '{root_path}'.")

    all_transactions = []
    error_report = []

    for file_path, category in files:
        txns, errors = load_csv_file(file_path, category)
        all_transactions.extend(txns)
        if errors:
            error_report.append({
                "file": file_path,
                "category": category,
                "rejected_rows": errors,
            })
        if verbose:
            print(f"  Loaded {len(txns):3d} valid row(s) "
                  f"({len(errors)} rejected) from {file_path}")

    if verbose:
        total_rejected = sum(len(e["rejected_rows"]) for e in error_report)
        print(f"Total: {len(all_transactions)} valid transactions, "
              f"{total_rejected} rejected rows across {len(error_report)} file(s) with issues.")

    return all_transactions, error_report
