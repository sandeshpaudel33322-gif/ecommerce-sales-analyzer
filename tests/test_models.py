

import unittest
from modules.models import Transaction, InvalidTransactionError


class TestTransactionFromRow(unittest.TestCase):

    def valid_row(self, **overrides):
        row = {
            "transaction_id": "TXN00099",
            "date": "2026-05-10",
            "product": "USB-C Hub",
            "customer": "Aarav Sharma",
            "quantity": "3",
            "unit_price": "19.99",
            "region": "Biratnagar",
            "payment_method": "PayPal",
        }
        row.update(overrides)
        return row

    def test_valid_row_parses_correctly(self):
        txn = Transaction.from_row(self.valid_row(), category="Electronics/Accessories")
        self.assertEqual(txn.transaction_id, "TXN00099")
        self.assertEqual(txn.quantity, 3)
        self.assertAlmostEqual(txn.unit_price, 19.99)
        self.assertAlmostEqual(txn.total, 59.97, places=2)
        self.assertEqual(txn.category, "Electronics/Accessories")

    def test_missing_required_field_raises(self):
        row = self.valid_row()
        del row["product"]
        with self.assertRaises(InvalidTransactionError):
            Transaction.from_row(row, category="Electronics/Accessories")

    def test_empty_transaction_id_raises(self):
        row = self.valid_row(transaction_id="   ")
        with self.assertRaises(InvalidTransactionError):
            Transaction.from_row(row, category="Electronics/Accessories")

    def test_invalid_date_format_raises(self):
        row = self.valid_row(date="10-05-2026")  # wrong format
        with self.assertRaises(InvalidTransactionError):
            Transaction.from_row(row, category="Electronics/Accessories")

    def test_impossible_calendar_date_raises(self):
        row = self.valid_row(date="2026-13-40")  # month 13, day 40
        with self.assertRaises(InvalidTransactionError):
            Transaction.from_row(row, category="Electronics/Accessories")

    def test_negative_quantity_raises(self):
        row = self.valid_row(quantity="-5")
        with self.assertRaises(InvalidTransactionError):
            Transaction.from_row(row, category="Electronics/Accessories")

    def test_zero_quantity_raises(self):
        row = self.valid_row(quantity="0")
        with self.assertRaises(InvalidTransactionError):
            Transaction.from_row(row, category="Electronics/Accessories")

    def test_non_numeric_quantity_raises(self):
        row = self.valid_row(quantity="abc")
        with self.assertRaises(InvalidTransactionError):
            Transaction.from_row(row, category="Electronics/Accessories")

    def test_negative_unit_price_raises(self):
        row = self.valid_row(unit_price="-15.00")
        with self.assertRaises(InvalidTransactionError):
            Transaction.from_row(row, category="Electronics/Accessories")

    def test_non_numeric_unit_price_raises(self):
        row = self.valid_row(unit_price="free")
        with self.assertRaises(InvalidTransactionError):
            Transaction.from_row(row, category="Electronics/Accessories")

    def test_missing_region_defaults_to_unknown(self):
        row = self.valid_row()
        del row["region"]
        txn = Transaction.from_row(row, category="Electronics/Accessories")
        self.assertEqual(txn.region, "Unknown")

    def test_zero_price_is_allowed_as_valid_edge_case(self):
        # a free promotional item is a legitimate business scenario -
        # zero should be accepted, only NEGATIVE prices are rejected.
        row = self.valid_row(unit_price="0")
        txn = Transaction.from_row(row, category="Electronics/Accessories")
        self.assertEqual(txn.total, 0.0)


if __name__ == "__main__":
    unittest.main()
