

import unittest
from modules import sort_engine
from tests.test_helpers import sample_dataset, make_transaction


class SortAlgorithmTestMixin:
    """Mixin so the exact same test cases run against BOTH merge_sort and quick_sort."""
    sort_func = None  # set by subclasses

    def test_sort_by_date_matches_builtin(self):
        data = sample_dataset()
        expected = sorted(data, key=lambda t: t.date)
        result = self.sort_func(data, key_func=lambda t: t.date)
        self.assertEqual([t.transaction_id for t in result], [t.transaction_id for t in expected])

    def test_sort_by_total_value_matches_builtin(self):
        data = sample_dataset()
        expected = sorted(data, key=lambda t: t.total)
        result = self.sort_func(data, key_func=lambda t: t.total)
        self.assertEqual([t.transaction_id for t in result], [t.transaction_id for t in expected])

    def test_sort_by_quantity_matches_builtin(self):
        data = sample_dataset()
        expected = sorted(data, key=lambda t: t.quantity)
        result = self.sort_func(data, key_func=lambda t: t.quantity)
        self.assertEqual([t.transaction_id for t in result], [t.transaction_id for t in expected])

    def test_reverse_sort_matches_builtin(self):
        data = sample_dataset()
        expected = sorted(data, key=lambda t: t.total, reverse=True)
        result = self.sort_func(data, key_func=lambda t: t.total, reverse=True)
        self.assertEqual([t.transaction_id for t in result], [t.transaction_id for t in expected])

    def test_empty_list(self):
        result = self.sort_func([], key_func=lambda t: t.total)
        self.assertEqual(result, [])

    def test_single_item_list(self):
        data = [make_transaction("TXN0001")]
        result = self.sort_func(data, key_func=lambda t: t.total)
        self.assertEqual(len(result), 1)

    def test_already_sorted_input(self):
        data = sorted(sample_dataset(), key=lambda t: t.total)
        result = self.sort_func(data, key_func=lambda t: t.total)
        self.assertEqual([t.transaction_id for t in result], [t.transaction_id for t in data])

    def test_reverse_sorted_input(self):
        # exercises quick_sort's known worst case for a naive last-element pivot
        data = sorted(sample_dataset(), key=lambda t: t.total, reverse=True)
        expected = sorted(data, key=lambda t: t.total)
        result = self.sort_func(data, key_func=lambda t: t.total)
        self.assertEqual([t.transaction_id for t in result], [t.transaction_id for t in expected])

    def test_does_not_mutate_original_list(self):
        data = sample_dataset()
        original_order = [t.transaction_id for t in data]
        self.sort_func(data, key_func=lambda t: t.total, reverse=True)
        self.assertEqual([t.transaction_id for t in data], original_order)

    def test_duplicate_keys_all_present_in_output(self):
        data = [
            make_transaction("A", unit_price=10.0, quantity=1),
            make_transaction("B", unit_price=10.0, quantity=1),
            make_transaction("C", unit_price=5.0, quantity=1),
        ]
        result = self.sort_func(data, key_func=lambda t: t.total)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].transaction_id, "C")
        self.assertEqual({result[1].transaction_id, result[2].transaction_id}, {"A", "B"})


class TestMergeSort(SortAlgorithmTestMixin, unittest.TestCase):
    sort_func = staticmethod(sort_engine.merge_sort)

    def test_merge_sort_is_stable(self):
        # merge_sort must preserve the relative order of equal-key items
        data = [
            make_transaction("A", unit_price=10.0, quantity=1),
            make_transaction("B", unit_price=10.0, quantity=1),
        ]
        result = sort_engine.merge_sort(data, key_func=lambda t: t.total)
        self.assertEqual([t.transaction_id for t in result], ["A", "B"])


class TestQuickSort(SortAlgorithmTestMixin, unittest.TestCase):
    sort_func = staticmethod(sort_engine.quick_sort)


class TestConvenienceWrappers(unittest.TestCase):

    def test_sort_by_date_wrapper(self):
        data = sample_dataset()
        result = sort_engine.sort_by_date(data)
        self.assertTrue(all(result[i].date <= result[i + 1].date for i in range(len(result) - 1)))

    def test_sort_by_total_value_wrapper_descending(self):
        data = sample_dataset()
        result = sort_engine.sort_by_total_value(data, reverse=True)
        self.assertTrue(all(result[i].total >= result[i + 1].total for i in range(len(result) - 1)))

    def test_sort_by_quantity_wrapper_with_quick_algorithm(self):
        data = sample_dataset()
        result = sort_engine.sort_by_quantity(data, algorithm="quick")
        self.assertTrue(all(result[i].quantity <= result[i + 1].quantity for i in range(len(result) - 1)))


if __name__ == "__main__":
    unittest.main()
