"""
sort_engine.py
--------------
Implements the "Sorting by date, sales value or quantity" requirement
using two hand-written comparison-sort algorithms (rather than relying
on Python's built-in `sorted()`), so the report can discuss algorithmic
complexity and design choices as required by the rubric.

    * merge_sort  - O(n log n) worst-case, stable, divide-and-conquer.
                    Used as the DEFAULT sort for the application because
                    it has predictable performance regardless of input
                    order (good for potentially large transaction logs).

    * quick_sort  - O(n log n) average-case, O(n^2) worst-case, in-place
                    partitioning. Included so the report can compare it
                    against merge_sort (e.g. quick_sort degrades on
                    already-sorted data with a naive pivot, which we
                    demonstrate and discuss in the test suite / report).

Both functions are GENERIC: they accept a `key_func` to extract the
sort key from a Transaction, and a `reverse` flag, so the same code
sorts by date, total sales value, or quantity without duplication.
"""

from typing import List, Callable, Any
from modules.models import Transaction


def merge_sort(items: List[Transaction], key_func: Callable[[Transaction], Any],
               reverse: bool = False) -> List[Transaction]:
    """
    Stable merge sort. Returns a NEW sorted list; does not mutate `items`.
    Base case: a list of 0 or 1 items is already sorted.
    """
    if len(items) <= 1:
        return list(items)

    mid = len(items) // 2
    left = merge_sort(items[:mid], key_func, reverse)
    right = merge_sort(items[mid:], key_func, reverse)
    return _merge(left, right, key_func, reverse)


def _merge(left: List[Transaction], right: List[Transaction],
           key_func: Callable[[Transaction], Any], reverse: bool) -> List[Transaction]:
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        left_key = key_func(left[i])
        right_key = key_func(right[j])
        take_left = (left_key <= right_key) if not reverse else (left_key >= right_key)
        if take_left:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def quick_sort(items: List[Transaction], key_func: Callable[[Transaction], Any],
               reverse: bool = False) -> List[Transaction]:
    """
    Classic Lomuto-partition quick sort. Returns a NEW sorted list.
    Included primarily for algorithmic comparison against merge_sort
    (see tests/test_sort_engine.py for a worst-case timing demonstration).
    """
    items = list(items)  # avoid mutating caller's list
    _quick_sort_in_place(items, 0, len(items) - 1, key_func, reverse)
    return items


def _quick_sort_in_place(items: List[Transaction], low: int, high: int,
                          key_func: Callable[[Transaction], Any], reverse: bool) -> None:
    if low < high:
        pivot_index = _partition(items, low, high, key_func, reverse)
        _quick_sort_in_place(items, low, pivot_index - 1, key_func, reverse)
        _quick_sort_in_place(items, pivot_index + 1, high, key_func, reverse)


def _partition(items: List[Transaction], low: int, high: int,
               key_func: Callable[[Transaction], Any], reverse: bool) -> int:
    pivot_key = key_func(items[high])
    i = low - 1
    for j in range(low, high):
        current_key = key_func(items[j])
        should_swap = (current_key <= pivot_key) if not reverse else (current_key >= pivot_key)
        if should_swap:
            i += 1
            items[i], items[j] = items[j], items[i]
    items[i + 1], items[high] = items[high], items[i + 1]
    return i + 1


# --- Convenience wrappers matching the app's menu options -------------------

def sort_by_date(transactions: List[Transaction], reverse: bool = False, algorithm: str = "merge") -> List[Transaction]:
    fn = merge_sort if algorithm == "merge" else quick_sort
    return fn(transactions, key_func=lambda t: t.date, reverse=reverse)


def sort_by_total_value(transactions: List[Transaction], reverse: bool = False, algorithm: str = "merge") -> List[Transaction]:
    fn = merge_sort if algorithm == "merge" else quick_sort
    return fn(transactions, key_func=lambda t: t.total, reverse=reverse)


def sort_by_quantity(transactions: List[Transaction], reverse: bool = False, algorithm: str = "merge") -> List[Transaction]:
    fn = merge_sort if algorithm == "merge" else quick_sort
    return fn(transactions, key_func=lambda t: t.quantity, reverse=reverse)
