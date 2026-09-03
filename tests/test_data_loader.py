

import os
import shutil
import tempfile
import unittest

from modules.data_loader import (
    scan_directory_recursive,
    load_csv_file,
    load_all_transactions,
    DataLoadError,
)


class TestRecursiveScan(unittest.TestCase):

    def setUp(self):
        # Build a temporary nested folder tree for isolated, repeatable tests
        self.tmp_dir = tempfile.mkdtemp()
        self._write("A/file_a1.csv", "transaction_id,date\nTXN1,2026-01-01\n")
        self._write("A/Sub1/file_sub1.csv", "transaction_id,date\nTXN2,2026-01-02\n")
        self._write("A/Sub1/SubSub/file_deep.csv", "transaction_id,date\nTXN3,2026-01-03\n")
        self._write("B/file_b1.csv", "transaction_id,date\nTXN4,2026-01-04\n")
        self._write("B/notes.txt", "this is not a csv file and should be ignored\n")
        os.makedirs(os.path.join(self.tmp_dir, "C_empty_folder"), exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def _write(self, relative_path, content):
        full_path = os.path.join(self.tmp_dir, relative_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

    def test_finds_all_csv_files_at_every_depth(self):
        results = scan_directory_recursive(self.tmp_dir)
        found_files = sorted(os.path.basename(p) for p, _ in results)
        self.assertEqual(
            found_files,
            ["file_a1.csv", "file_b1.csv", "file_deep.csv", "file_sub1.csv"],
        )

    def test_ignores_non_csv_files(self):
        results = scan_directory_recursive(self.tmp_dir)
        for path, _ in results:
            self.assertTrue(path.endswith(".csv"))

    def test_category_derived_from_relative_path(self):
        results = scan_directory_recursive(self.tmp_dir)
        categories = {os.path.basename(p): cat for p, cat in results}
        self.assertEqual(categories["file_a1.csv"], "A")
        self.assertEqual(categories["file_sub1.csv"], "A/Sub1")
        self.assertEqual(categories["file_deep.csv"], "A/Sub1/SubSub")
        self.assertEqual(categories["file_b1.csv"], "B")

    def test_empty_folder_contributes_nothing(self):
        results = scan_directory_recursive(self.tmp_dir)
        for path, _ in results:
            self.assertNotIn("C_empty_folder", path)

    def test_nonexistent_root_raises(self):
        with self.assertRaises(DataLoadError):
            scan_directory_recursive(os.path.join(self.tmp_dir, "does_not_exist"))

    def test_file_given_instead_of_directory_raises(self):
        file_path = os.path.join(self.tmp_dir, "A", "file_a1.csv")
        with self.assertRaises(DataLoadError):
            scan_directory_recursive(file_path)


class TestLoadCsvFile(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def _write(self, name, content):
        path = os.path.join(self.tmp_dir, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def test_valid_rows_all_load(self):
        path = self._write("good.csv",
            "transaction_id,date,product,customer,quantity,unit_price,region,payment_method\n"
            "TXN001,2026-01-01,Widget,Alice,2,10.0,Kathmandu,Cash\n"
            "TXN002,2026-01-02,Gadget,Bob,1,25.5,Pokhara,Card\n"
        )
        txns, errors = load_csv_file(path, category="Test")
        self.assertEqual(len(txns), 2)
        self.assertEqual(len(errors), 0)

    def test_mixed_valid_and_invalid_rows(self):
        path = self._write("mixed.csv",
            "transaction_id,date,product,customer,quantity,unit_price,region,payment_method\n"
            "TXN001,2026-01-01,Widget,Alice,2,10.0,Kathmandu,Cash\n"
            "TXN002,2026-13-40,Gadget,Bob,1,25.5,Pokhara,Card\n"   # bad date
            "TXN003,2026-01-03,Gizmo,Carol,-1,5.0,Sydney,Cash\n"   # bad quantity
        )
        txns, errors = load_csv_file(path, category="Test")
        self.assertEqual(len(txns), 1)
        self.assertEqual(len(errors), 2)

    def test_completely_empty_file_with_only_header(self):
        path = self._write("empty.csv",
            "transaction_id,date,product,customer,quantity,unit_price,region,payment_method\n"
        )
        txns, errors = load_csv_file(path, category="Test")
        self.assertEqual(txns, [])
        self.assertEqual(errors, [])

    def test_blank_trailing_row_is_skipped_not_flagged(self):
        path = self._write("trailing_blank.csv",
            "transaction_id,date,product,customer,quantity,unit_price,region,payment_method\n"
            "TXN001,2026-01-01,Widget,Alice,2,10.0,Kathmandu,Cash\n"
            "\n"
        )
        txns, errors = load_csv_file(path, category="Test")
        self.assertEqual(len(txns), 1)
        self.assertEqual(len(errors), 0)

    def test_nonexistent_file_raises_data_load_error(self):
        with self.assertRaises(DataLoadError):
            load_csv_file(os.path.join(self.tmp_dir, "missing.csv"), category="Test")


class TestLoadAllTransactionsIntegration(unittest.TestCase):
    """Integration test against the real sample dataset shipped with the project."""

    def setUp(self):
        # project_root/tests/../data/transactions
        self.data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "transactions")

    def test_sample_dataset_loads_with_known_bad_rows_captured(self):
        transactions, error_report = load_all_transactions(self.data_dir, verbose=False)
        self.assertGreater(len(transactions), 0, "Sample dataset should contain valid transactions.")
        # The sample data generator intentionally injects bad rows into the
        # Electronics/Mobiles file - confirm they were caught, not silently lost.
        flagged_files = [e["file"] for e in error_report]
        self.assertTrue(
            any("Mobiles" in f for f in flagged_files),
            "Expected the intentionally-corrupted Mobiles file to be flagged in the error report.",
        )


if __name__ == "__main__":
    unittest.main()
