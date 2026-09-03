"""
analytics.py
------------
Business analytics and summaries, built on dictionaries/lists.

The centrepiece is `build_category_tree` + `recursive_category_totals`,
which satisfies the "Recursive processing of ... transaction categories"
requirement directly: categories are nested (e.g. "Electronics/Mobiles"
is a child of "Electronics"), stored as a tree of dictionaries, and
totalled with a function that calls itself on every child node.
"""

from collections import defaultdict, Counter
from typing import List, Dict, Any
from modules.models import Transaction


# ---------------------------------------------------------------------------
# Simple (non-recursive) aggregate statistics - dictionaries & lists
# ---------------------------------------------------------------------------

def total_revenue(transactions: List[Transaction]) -> float:
    return round(sum(t.total for t in transactions), 2)


def total_units_sold(transactions: List[Transaction]) -> int:
    return sum(t.quantity for t in transactions)


def average_order_value(transactions: List[Transaction]) -> float:
    if not transactions:
        return 0.0
    return round(total_revenue(transactions) / len(transactions), 2)


def revenue_by_key(transactions: List[Transaction], key_func) -> Dict[str, float]:
    """Generic 'group by X, sum revenue' - used for product/customer/region breakdowns."""
    totals: Dict[str, float] = defaultdict(float)
    for t in transactions:
        totals[key_func(t)] += t.total
    return {k: round(v, 2) for k, v in totals.items()}


def top_n(totals: Dict[str, float], n: int = 5) -> List[tuple]:
    """Return the top-n (key, value) pairs sorted descending by value."""
    return sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:n]


def revenue_by_month(transactions: List[Transaction]) -> Dict[str, float]:
    totals: Dict[str, float] = defaultdict(float)
    for t in transactions:
        month_key = t.date.strftime("%Y-%m")
        totals[month_key] += t.total
    return dict(sorted({k: round(v, 2) for k, v in totals.items()}.items()))


def payment_method_breakdown(transactions: List[Transaction]) -> Dict[str, int]:
    return dict(Counter(t.payment_method for t in transactions))


# ---------------------------------------------------------------------------
# RECURSIVE category-tree processing
# ---------------------------------------------------------------------------
#
# A transaction's `category` field looks like "Electronics/Mobiles" or
# just "HomeAndFurniture" (no sub-category). We turn the flat list of
# transactions into a nested dictionary tree:
#
#   {
#       "Electronics": {
#           "__transactions__": [...],
#           "Mobiles": {"__transactions__": [...]},
#           "Laptops":  {"__transactions__": [...]},
#       },
#       "HomeAndFurniture": {"__transactions__": [...]},
#       ...
#   }
#
# and then RECURSIVELY total revenue/quantity down that tree: a node's
# total is its own direct transactions PLUS the (recursively computed)
# totals of every child node. This mirrors how a real business would
# want "Electronics" to report combined sales across all of its
# sub-categories.

TXN_KEY = "__transactions__"


def build_category_tree(transactions: List[Transaction]) -> Dict[str, Any]:
    """Build the nested category tree described above from a flat transaction list."""
    tree: Dict[str, Any] = {}

    for txn in transactions:
        parts = txn.category.split("/") if txn.category else ["Uncategorised"]
        node = tree
        for part in parts:
            node = node.setdefault(part, {})
        node.setdefault(TXN_KEY, []).append(txn)

    return tree


def recursive_category_totals(node: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively compute {revenue, units, transaction_count} for a category
    tree node, INCLUDING everything nested beneath it.

    Base case: a leaf node with only its own "__transactions__" list and
               no child dictionaries.
    Recursive case: sum this node's own transactions PLUS the recursively
               computed totals of every child category.

    Returns a new dict shaped like:
        {
            "revenue": 1234.56,
            "units": 42,
            "transaction_count": 17,
            "children": {
                "Mobiles": {revenue, units, transaction_count, children: {}},
                ...
            }
        }
    """
    own_transactions = node.get(TXN_KEY, [])
    revenue = total_revenue(own_transactions)
    units = total_units_sold(own_transactions)
    count = len(own_transactions)

    children_summary = {}
    for key, child_node in node.items():
        if key == TXN_KEY:
            continue
        # --- recursive call ---
        child_summary = recursive_category_totals(child_node)
        children_summary[key] = child_summary

        revenue += child_summary["revenue"]
        units += child_summary["units"]
        count += child_summary["transaction_count"]

    return {
        "revenue": round(revenue, 2),
        "units": units,
        "transaction_count": count,
        "children": children_summary,
    }


def print_category_summary(summary: Dict[str, Any], name: str = "ALL CATEGORIES", depth: int = 0) -> None:
    """Pretty-print a recursive_category_totals() result as an indented tree."""
    indent = "  " * depth
    print(f"{indent}- {name}: "
          f"Rs./$ {summary['revenue']:,.2f} revenue, "
          f"{summary['units']} units, "
          f"{summary['transaction_count']} transactions")
    for child_name, child_summary in sorted(summary["children"].items()):
        print_category_summary(child_summary, child_name, depth + 1)


def flatten_category_summary(summary: Dict[str, Any], name: str = "ALL",
                              depth: int = 0, rows=None) -> List[dict]:
    """
    Recursively flatten a category summary tree into a list of row-dicts
    (used to export the business summary to CSV / feed the bar chart).
    """
    if rows is None:
        rows = []
    rows.append({
        "category": name,
        "depth": depth,
        "revenue": summary["revenue"],
        "units": summary["units"],
        "transaction_count": summary["transaction_count"],
    })
    for child_name, child_summary in sorted(summary["children"].items()):
        flatten_category_summary(child_summary, f"{name}/{child_name}" if depth == 0 else child_name,
                                  depth + 1, rows)
    return rows


def generate_business_summary(transactions: List[Transaction]) -> Dict[str, Any]:
    """
    One-stop function that assembles everything main.py / the report
    needs: headline numbers, top products/customers, monthly trend,
    payment breakdown, and the recursive category tree totals.
    """
    tree = build_category_tree(transactions)
    category_totals = recursive_category_totals(tree)

    return {
        "total_revenue": total_revenue(transactions),
        "total_units_sold": total_units_sold(transactions),
        "total_transactions": len(transactions),
        "average_order_value": average_order_value(transactions),
        "top_products": top_n(revenue_by_key(transactions, lambda t: t.product), 5),
        "top_customers": top_n(revenue_by_key(transactions, lambda t: t.customer), 5),
        "revenue_by_region": revenue_by_key(transactions, lambda t: t.region),
        "revenue_by_month": revenue_by_month(transactions),
        "payment_methods": payment_method_breakdown(transactions),
        "category_totals": category_totals,
    }
