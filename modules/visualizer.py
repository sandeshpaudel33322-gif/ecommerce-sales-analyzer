"""
visualizer.py
-------------
Generates the "Graphs and business summaries" charts using matplotlib
and saves them as PNG files into the reports/ folder. Kept isolated
from analytics.py so the calculation logic can be unit-tested without
needing a display / matplotlib backend.
"""

import os
import matplotlib
matplotlib.use("Agg")  # headless backend - safe for servers / CI / no display
import matplotlib.pyplot as plt

from typing import Dict, List, Tuple


def _ensure_reports_dir(reports_dir: str) -> None:
    os.makedirs(reports_dir, exist_ok=True)


def plot_revenue_by_category(flat_rows: List[dict], reports_dir: str, filename: str = "revenue_by_category.png") -> str:
    """
    Bar chart of revenue for each TOP-LEVEL category (depth == 1 rows from
    flatten_category_summary), demonstrating the recursive category totals
    visually.
    """
    _ensure_reports_dir(reports_dir)
    top_level = [r for r in flat_rows if r["depth"] == 1]
    top_level.sort(key=lambda r: r["revenue"], reverse=True)

    labels = [r["category"].split("/")[-1] for r in top_level]
    values = [r["revenue"] for r in top_level]

    plt.figure(figsize=(9, 5))
    bars = plt.bar(labels, values, color="#2563eb")
    plt.title("Revenue by Category")
    plt.ylabel("Revenue")
    plt.xticks(rotation=30, ha="right")
    for bar, value in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                  f"{value:,.0f}", ha="center", va="bottom", fontsize=8)
    plt.tight_layout()

    out_path = os.path.join(reports_dir, filename)
    plt.savefig(out_path, dpi=150)
    plt.close()
    return out_path


def plot_monthly_trend(revenue_by_month: Dict[str, float], reports_dir: str, filename: str = "monthly_trend.png") -> str:
    """Line chart of revenue over time (monthly)."""
    _ensure_reports_dir(reports_dir)
    months = list(revenue_by_month.keys())
    values = list(revenue_by_month.values())

    plt.figure(figsize=(9, 5))
    plt.plot(months, values, marker="o", color="#16a34a", linewidth=2)
    plt.title("Monthly Sales Trend")
    plt.ylabel("Revenue")
    plt.xlabel("Month")
    plt.xticks(rotation=30, ha="right")
    plt.grid(alpha=0.3)
    plt.tight_layout()

    out_path = os.path.join(reports_dir, filename)
    plt.savefig(out_path, dpi=150)
    plt.close()
    return out_path


def plot_region_share(revenue_by_region: Dict[str, float], reports_dir: str, filename: str = "region_share.png") -> str:
    """Pie chart of revenue share by region."""
    _ensure_reports_dir(reports_dir)
    labels = list(revenue_by_region.keys())
    values = list(revenue_by_region.values())

    plt.figure(figsize=(7, 7))
    plt.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    plt.title("Revenue Share by Region")
    plt.tight_layout()

    out_path = os.path.join(reports_dir, filename)
    plt.savefig(out_path, dpi=150)
    plt.close()
    return out_path


def plot_top_products(top_products: List[Tuple[str, float]], reports_dir: str, filename: str = "top_products.png") -> str:
    """Horizontal bar chart of the top-selling products by revenue."""
    _ensure_reports_dir(reports_dir)
    labels = [p for p, _ in top_products][::-1]
    values = [v for _, v in top_products][::-1]

    plt.figure(figsize=(9, 5))
    plt.barh(labels, values, color="#ea580c")
    plt.title("Top Products by Revenue")
    plt.xlabel("Revenue")
    plt.tight_layout()

    out_path = os.path.join(reports_dir, filename)
    plt.savefig(out_path, dpi=150)
    plt.close()
    return out_path


def generate_all_charts(summary: dict, flat_category_rows: List[dict], reports_dir: str) -> List[str]:
    """Generate every chart the app produces; returns list of file paths written."""
    paths = []
    paths.append(plot_revenue_by_category(flat_category_rows, reports_dir))
    paths.append(plot_monthly_trend(summary["revenue_by_month"], reports_dir))
    paths.append(plot_region_share(summary["revenue_by_region"], reports_dir))
    paths.append(plot_top_products(summary["top_products"], reports_dir))
    return paths
