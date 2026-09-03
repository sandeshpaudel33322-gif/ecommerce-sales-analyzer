

import unittest
from modules import analytics
from tests.test_helpers import sample_dataset, make_transaction


class TestBasicAggregates(unittest.TestCase):

    def setUp(self):
        self.data = sample_dataset()

    def test_total_revenue(self):
        # 1000 + 1800 + 1500 + 150 + 80 + 200 = 4730
        self.assertAlmostEqual(analytics.total_revenue(self.data), 4730.0, places=2)

    def test_total_units_sold(self):
        # 1 + 2 + 1 + 3 + 1 + 1 = 9
        self.assertEqual(analytics.total_units_sold(self.data), 9)

    def test_average_order_value(self):
        self.assertAlmostEqual(analytics.average_order_value(self.data), 4730.0 / 6, places=2)

    def test_average_order_value_empty_dataset(self):
        self.assertEqual(analytics.average_order_value([]), 0.0)

    def test_revenue_by_key_customer(self):
        totals = analytics.revenue_by_key(self.data, lambda t: t.customer)
        self.assertAlmostEqual(totals["Alice"], 2500.0, places=2)  # 1000 + 1500
        self.assertAlmostEqual(totals["Bob"], 2000.0, places=2)    # 1800 + 200

    def test_top_n_returns_correct_order(self):
        totals = {"A": 10, "B": 50, "C": 30}
        result = analytics.top_n(totals, n=2)
        self.assertEqual(result, [("B", 50), ("C", 30)])

    def test_revenue_by_month_grouping(self):
        totals = analytics.revenue_by_month(self.data)
        self.assertIn("2026-01", totals)
        self.assertIn("2026-02", totals)
        self.assertIn("2026-03", totals)

    def test_payment_method_breakdown(self):
        breakdown = analytics.payment_method_breakdown(self.data)
        self.assertEqual(sum(breakdown.values()), len(self.data))


class TestRecursiveCategoryTotals(unittest.TestCase):

    def setUp(self):
        self.data = sample_dataset()
        self.tree = analytics.build_category_tree(self.data)

    def test_tree_structure_has_top_level_categories(self):
        self.assertIn("Electronics", self.tree)
        self.assertIn("Clothing", self.tree)
        self.assertIn("HomeAndFurniture", self.tree)

    def test_tree_nests_subcategories(self):
        self.assertIn("Mobiles", self.tree["Electronics"])
        self.assertIn("Laptops", self.tree["Electronics"])

    def test_recursive_totals_leaf_node(self):
        summary = analytics.recursive_category_totals(self.tree)
        electronics = summary["children"]["Electronics"]
        mobiles = electronics["children"]["Mobiles"]
        # TXN00001 (1000) + TXN00002 (1800) = 2800
        self.assertAlmostEqual(mobiles["revenue"], 2800.0, places=2)
        self.assertEqual(mobiles["transaction_count"], 2)

    def test_recursive_totals_roll_up_to_parent(self):
        summary = analytics.recursive_category_totals(self.tree)
        electronics = summary["children"]["Electronics"]
        # Mobiles (2800) + Laptops (1500) = 4300
        self.assertAlmostEqual(electronics["revenue"], 4300.0, places=2)
        self.assertEqual(electronics["transaction_count"], 3)

    def test_recursive_totals_grand_total_matches_flat_sum(self):
        summary = analytics.recursive_category_totals(self.tree)
        self.assertAlmostEqual(summary["revenue"], analytics.total_revenue(self.data), places=2)
        self.assertEqual(summary["transaction_count"], len(self.data))

    def test_single_level_category_with_no_children(self):
        summary = analytics.recursive_category_totals(self.tree)
        home = summary["children"]["HomeAndFurniture"]
        self.assertAlmostEqual(home["revenue"], 200.0, places=2)
        self.assertEqual(home["children"], {})

    def test_empty_transaction_list_produces_empty_tree(self):
        tree = analytics.build_category_tree([])
        summary = analytics.recursive_category_totals(tree)
        self.assertEqual(summary["revenue"], 0.0)
        self.assertEqual(summary["transaction_count"], 0)
        self.assertEqual(summary["children"], {})

    def test_uncategorised_fallback_for_blank_category(self):
        txn = make_transaction("TXN9999", category="")
        tree = analytics.build_category_tree([txn])
        self.assertIn("Uncategorised", tree)

    def test_deeply_nested_category_three_levels(self):
        txn = make_transaction("TXN8888", category="A/B/C")
        tree = analytics.build_category_tree([txn])
        summary = analytics.recursive_category_totals(tree)
        level_a = summary["children"]["A"]
        level_b = level_a["children"]["B"]
        level_c = level_b["children"]["C"]
        self.assertEqual(level_c["transaction_count"], 1)
        # totals should roll all the way up
        self.assertEqual(level_a["transaction_count"], 1)


class TestFlattenCategorySummary(unittest.TestCase):

    def test_flatten_produces_one_row_per_node(self):
        data = sample_dataset()
        tree = analytics.build_category_tree(data)
        summary = analytics.recursive_category_totals(tree)
        rows = analytics.flatten_category_summary(summary)
        categories = {row["category"] for row in rows}
        self.assertIn("ALL", categories)
        self.assertTrue(any("Electronics" in c for c in categories))


class TestGenerateBusinessSummary(unittest.TestCase):

    def test_full_summary_has_expected_keys(self):
        data = sample_dataset()
        summary = analytics.generate_business_summary(data)
        for key in ("total_revenue", "total_units_sold", "total_transactions",
                    "average_order_value", "top_products", "top_customers",
                    "revenue_by_region", "revenue_by_month", "payment_methods",
                    "category_totals"):
            self.assertIn(key, summary)

    def test_full_summary_on_empty_dataset_does_not_crash(self):
        summary = analytics.generate_business_summary([])
        self.assertEqual(summary["total_revenue"], 0.0)
        self.assertEqual(summary["total_transactions"], 0)


if __name__ == "__main__":
    unittest.main()
