

import unittest
from modules import search_engine, sort_engine
from tests.test_helpers import sample_dataset


class TestLinearSearch(unittest.TestCase):

    def setUp(self):
        self.data = sample_dataset()

    def test_search_by_product_case_insensitive_substring(self):
        results = search_engine.search_by_product(self.data, "iphone")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].transaction_id, "TXN00001")

    def test_search_by_customer_multiple_matches(self):
        results = search_engine.search_by_customer(self.data, "Alice")
        ids = sorted(t.transaction_id for t in results)
        self.assertEqual(ids, ["TXN00001", "TXN00003"])

    def test_search_no_matches_returns_empty_list(self):
        results = search_engine.search_by_product(self.data, "Nonexistent Product XYZ")
        self.assertEqual(results, [])

    def test_search_empty_keyword_returns_empty_list(self):
        results = search_engine.search_by_product(self.data, "")
        self.assertEqual(results, [])

    def test_search_on_empty_dataset(self):
        results = search_engine.search_by_product([], "anything")
        self.assertEqual(results, [])

    def test_search_whitespace_only_keyword(self):
        results = search_engine.search_by_customer(self.data, "   ")
        self.assertEqual(results, [])


class TestBinarySearch(unittest.TestCase):

    def setUp(self):
        self.data = sample_dataset()
        self.sorted_data = sort_engine.merge_sort(self.data, key_func=lambda t: t.transaction_id)

    def test_finds_existing_id(self):
        result = search_engine.binary_search_exact(self.sorted_data, "TXN00004")
        self.assertIsNotNone(result)
        self.assertEqual(result.customer, "Carol")

    def test_returns_none_for_missing_id(self):
        result = search_engine.binary_search_exact(self.sorted_data, "TXN99999")
        self.assertIsNone(result)

    def test_returns_none_on_empty_list(self):
        result = search_engine.binary_search_exact([], "TXN00001")
        self.assertIsNone(result)

    def test_finds_first_and_last_elements(self):
        first = self.sorted_data[0].transaction_id
        last = self.sorted_data[-1].transaction_id
        self.assertIsNotNone(search_engine.binary_search_exact(self.sorted_data, first))
        self.assertIsNotNone(search_engine.binary_search_exact(self.sorted_data, last))

    def test_search_by_transaction_id_convenience_wrapper(self):
        # uses UNSORTED input directly - wrapper must sort internally
        result = search_engine.search_by_transaction_id(self.data, "TXN00002")
        self.assertIsNotNone(result)
        self.assertEqual(result.product, "Galaxy S24")

    def test_search_by_transaction_id_empty_target(self):
        self.assertIsNone(search_engine.search_by_transaction_id(self.data, ""))


class TestBuildIndex(unittest.TestCase):

    def test_index_groups_by_key(self):
        data = sample_dataset()
        index = search_engine.build_index(data, key_func=lambda t: t.customer)
        self.assertIn("Alice", index)
        self.assertEqual(len(index["Alice"]), 2)
        self.assertEqual(len(index["Bob"]), 2)

    def test_index_on_empty_dataset(self):
        index = search_engine.build_index([], key_func=lambda t: t.customer)
        self.assertEqual(index, {})


if __name__ == "__main__":
    unittest.main()
