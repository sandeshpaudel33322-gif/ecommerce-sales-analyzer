
import os
import sys
import csv

from modules.data_loader import load_all_transactions, DataLoadError
from modules.models import Transaction
from modules import search_engine, sort_engine, analytics, visualizer, validators

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "transactions")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")


class SalesAnalyzerApp:
    """Wraps application state (loaded transactions, error report) and the menu loop."""

    def __init__(self, data_dir: str = DATA_DIR, reports_dir: str = REPORTS_DIR):
        self.data_dir = data_dir
        self.reports_dir = reports_dir
        self.transactions = []
        self.error_report = []

  
    # Data loading
  

    def load_data(self):
        print(f"\nScanning '{self.data_dir}' recursively for transaction files...\n")
        try:
            self.transactions, self.error_report = load_all_transactions(self.data_dir)
        except DataLoadError as exc:
            print(f"[ERROR] Could not load data: {exc}")
            self.transactions, self.error_report = [], []

        if not self.transactions:
            print("\n[WARNING] No valid transactions were loaded. "
                  "Check that the data folder exists and contains CSV files.")

    # Menu: Search
    

    def menu_search(self):
        print("\n--- Search Transactions ---")
        print("1. Search by Product")
        print("2. Search by Customer")
        print("3. Search by Transaction ID (exact)")
        print("0. Back to main menu")
        choice = validators.validate_menu_choice(input("Choose an option: "), {"0", "1", "2", "3"})

        if choice is None:
            print("[INVALID] Please enter one of: 0, 1, 2, 3.")
            return

        if choice == "0":
            return

        if choice in ("1", "2"):
            keyword = validators.validate_non_empty_string(input("Enter search text: "))
            if keyword is None:
                print("[INVALID] Search text cannot be empty.")
                return
            if choice == "1":
                results = search_engine.search_by_product(self.transactions, keyword)
            else:
                results = search_engine.search_by_customer(self.transactions, keyword)
            self._print_transactions(results, header=f"{len(results)} result(s) for '{keyword}'")

        elif choice == "3":
            target_id = validators.validate_non_empty_string(input("Enter exact Transaction ID: "))
            if target_id is None:
                print("[INVALID] Transaction ID cannot be empty.")
                return
            result = search_engine.search_by_transaction_id(self.transactions, target_id)
            if result is None:
                print(f"No transaction found with ID '{target_id}'.")
            else:
                self._print_transactions([result], header="Match found")


    # Menu: Sort


    def menu_sort(self):
        print("\n--- Sort Transactions ---")
        print("1. Sort by Date")
        print("2. Sort by Sales Value (total)")
        print("3. Sort by Quantity")
        print("0. Back to main menu")
        choice = validators.validate_menu_choice(input("Choose an option: "), {"0", "1", "2", "3"})

        if choice is None:
            print("[INVALID] Please enter one of: 0, 1, 2, 3.")
            return
        if choice == "0":
            return

        order = validators.validate_yes_no(input("Descending order? (y/n): "))
        if order is None:
            print("[INVALID] Please answer y or n. Defaulting to ascending.")
            order = False

        if not self.transactions:
            print("No data loaded to sort.")
            return

        if choice == "1":
            sorted_txns = sort_engine.sort_by_date(self.transactions, reverse=order)
        elif choice == "2":
            sorted_txns = sort_engine.sort_by_total_value(self.transactions, reverse=order)
        else:
            sorted_txns = sort_engine.sort_by_quantity(self.transactions, reverse=order)

        n = validators.validate_positive_int(input("How many rows to display? (e.g. 10): ")) or 10
        self._print_transactions(sorted_txns[:n], header=f"Top {n} sorted result(s)")

   
    # Menu: Reports / Graphs


    def menu_reports(self):
        if not self.transactions:
            print("No data loaded - cannot generate reports.")
            return

        summary = analytics.generate_business_summary(self.transactions)

        print("\n=== BUSINESS SUMMARY ===")
        print(f"Total Revenue        : {summary['total_revenue']:,.2f}")
        print(f"Total Units Sold     : {summary['total_units_sold']}")
        print(f"Total Transactions   : {summary['total_transactions']}")
        print(f"Average Order Value  : {summary['average_order_value']:,.2f}")

        print("\nTop 5 Products by Revenue:")
        for name, value in summary["top_products"]:
            print(f"  {name:30s} {value:>12,.2f}")

        print("\nTop 5 Customers by Revenue:")
        for name, value in summary["top_customers"]:
            print(f"  {name:30s} {value:>12,.2f}")

        print("\nPayment Method Breakdown:")
        for method, count in summary["payment_methods"].items():
            print(f"  {method:20s} {count} transaction(s)")

        print("\nRecursive Category Revenue Tree:")
        analytics.print_category_summary(summary["category_totals"])

        if self.error_report:
            total_rejected = sum(len(e["rejected_rows"]) for e in self.error_report)
            print(f"\n[NOTE] {total_rejected} row(s) across {len(self.error_report)} "
                  f"file(s) were rejected during loading due to invalid data. "
                  f"Use option 5 (Data Quality Report) for details.")

        make_charts = validators.validate_yes_no(input("\nGenerate chart images (PNG)? (y/n): "))
        if make_charts:
            flat_rows = analytics.flatten_category_summary(summary["category_totals"])
            paths = visualizer.generate_all_charts(summary, flat_rows, self.reports_dir)
            print("\nCharts written to:")
            for p in paths:
                print(f"  {p}")

        export = validators.validate_yes_no(input("Export this summary to CSV? (y/n): "))
        if export:
            path = self._export_summary_csv(summary)
            print(f"Summary exported to: {path}")

    def _export_summary_csv(self, summary) -> str:
        os.makedirs(self.reports_dir, exist_ok=True)
        path = os.path.join(self.reports_dir, "business_summary.csv")
        flat_rows = analytics.flatten_category_summary(summary["category_totals"])
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["category", "depth", "revenue", "units", "transaction_count"])
            writer.writeheader()
            for row in flat_rows:
                writer.writerow(row)
        return path


    # Menu: Data quality / edge-case report
    

    def menu_data_quality(self):
        print("\n--- Data Quality / Rejected Rows Report ---")
        if not self.error_report:
            print("No invalid rows were encountered during loading. Data is clean.")
            return
        for entry in self.error_report:
            print(f"\nFile: {entry['file']}  (category: {entry['category']})")
            for line_number, message in entry["rejected_rows"]:
                print(f"  Line {line_number}: {message}")

 
    # Helpers
 

    @staticmethod
    def _print_transactions(transactions, header: str = ""):
        if header:
            print(f"\n{header}")
        if not transactions:
            print("  (no transactions to display)")
            return
        print(f"  {'ID':10s} {'Date':12s} {'Product':22s} {'Customer':18s} {'Qty':>4s} {'Total':>10s} {'Category':25s}")
        print("  " + "-" * 100)
        for t in transactions:
            print(f"  {t.transaction_id:10s} {t.date.strftime('%Y-%m-%d'):12s} "
                  f"{t.product[:22]:22s} {t.customer[:18]:18s} {t.quantity:>4d} "
                  f"{t.total:>10,.2f} {t.category:25s}")


    # Main loop


    def run(self):
        print("=" * 60)
        print("   E-COMMERCE SALES ANALYZER")
        print("=" * 60)
        self.load_data()

        menu_actions = {
            "1": self.menu_search,
            "2": self.menu_sort,
            "3": self.menu_reports,
            "4": self.load_data,
            "5": self.menu_data_quality,
        }

        while True:
            print("\n================ MAIN MENU ================")
            print("1. Search transactions")
            print("2. Sort transactions")
            print("3. Business summary & graphs")
            print("4. Reload data")
            print("5. Data quality / rejected rows report")
            print("0. Exit")
            choice = validators.validate_menu_choice(
                input("Choose an option: "), {"0", "1", "2", "3", "4", "5"}
            )

            if choice is None:
                print("[INVALID] Please enter a number between 0 and 5.")
                continue
            if choice == "0":
                print("Goodbye!")
                break

            menu_actions[choice]()


def main():
    app = SalesAnalyzerApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting cleanly.")
        sys.exit(0)


if __name__ == "__main__":
    main()
