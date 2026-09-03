"""
search_engine.py
-----------------
Implements the "Searching by product, customer or transaction" requirement
using two classic search algorithms, plus a dictionary-index approach for
comparison:

    * linear_search        - O(n), works on unsorted data, case-insensitive
                              substring match (used for product/customer
                              name search, since users rarely type exact,
                              fully-cased names).
    * binary_search_exact   - O(log n), requires the data to be pre-sorted
                              on the search key; used for exact
                              transaction_id lookups where a fast exact
                              match matters.
    * build_index           - O(n) one-off dictionary build, then O(1)
                              average-case lookups; shown so the report
                              can compare algorithmic trade-offs
                              (Part B: "solution design and algorithmic
                              approach").
"""

from typing import List, Callable, Optional
from modules.models import Transaction


def linear_search(transactions: List[Transaction], keyword: str,
                   key_func: Callable[[Transaction], str]) -> List[Transaction]:
    """
    Case-insensitive substring search over `transactions` using `key_func`
    to extract the field to compare (e.g. lambda t: t.product).

    Returns all matching transactions (there can be many, e.g. all
    "iPhone 15" purchases). Returns an empty list - never None - if
    nothing matches, so callers don't need extra None-checks.
    """
    if keyword is None or str(keyword).strip() == "":
        return []

    needle = str(keyword).strip().lower()
    matches = []
    for txn in transactions:
        haystack = str(key_func(txn)).lower()
        if needle in haystack:
            matches.append(txn)
    return matches


def search_by_product(transactions: List[Transaction], product_name: str) -> List[Transaction]:
    return linear_search(transactions, product_name, key_func=lambda t: t.product)


def search_by_customer(transactions: List[Transaction], customer_name: str) -> List[Transaction]:
    return linear_search(transactions, customer_name, key_func=lambda t: t.customer)


def binary_search_exact(sorted_transactions: List[Transaction], target_id: str) -> Optional[Transaction]:
    """
    Classic iterative binary search for an EXACT transaction_id match.

    Preconditions
    -------------
    `sorted_transactions` MUST already be sorted ascending by
    transaction_id (use sort_engine.merge_sort with key=lambda t: t.transaction_id
    first) - this function does not sort for you, to keep the O(log n)
    contract explicit and testable on its own.

    Returns the matching Transaction, or None if not found.
    """
    if not target_id:
        return None

    low, high = 0, len(sorted_transactions) - 1
    target_id = target_id.strip()

    while low <= high:
        mid = (low + high) // 2
        mid_id = sorted_transactions[mid].transaction_id
        if mid_id == target_id:
            return sorted_transactions[mid]
        elif mid_id < target_id:
            low = mid + 1
        else:
            high = mid - 1

    return None  # edge case: not found


def search_by_transaction_id(transactions: List[Transaction], target_id: str) -> Optional[Transaction]:
    """
    Convenience wrapper: sorts a COPY of the list by transaction_id then
    runs binary search, so callers don't have to manage sort order
    themselves. For a single lookup this is O(n log n); the app keeps a
    pre-sorted copy around where repeated lookups matter (see main.py).
    """
    from modules.sort_engine import merge_sort  # local import avoids a circular import
    if not transactions or not target_id:
        return None
    sorted_copy = merge_sort(transactions, key_func=lambda t: t.transaction_id)
    return binary_search_exact(sorted_copy, target_id)


def build_index(transactions: List[Transaction], key_func: Callable[[Transaction], str]) -> dict:
    """
    Build a dictionary index: key -> list of matching transactions.
    Demonstrates the "dictionaries" data-structure requirement and gives
    an O(1)-average alternative to linear_search for exact-key lookups
    (e.g. exact customer name rather than a partial/substring search).
    """
    index: dict = {}
    for txn in transactions:
        key = key_func(txn)
        index.setdefault(key, []).append(txn)
    return index
