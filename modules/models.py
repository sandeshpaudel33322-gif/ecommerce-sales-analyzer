"""
models.py
---------
Defines the core `Transaction` data structure used throughout the
E-Commerce Sales Analyzer, plus the custom exceptions used for
validation and error handling.

Using a dataclass keeps the record structured (rather than a loose
dictionary everywhere) while `to_dict()` still gives us a plain
dictionary view whenever one is needed (e.g. for the analytics module).
"""

from dataclasses import dataclass, field
from datetime import datetime


class InvalidTransactionError(Exception):
    """Raised when a raw row of data cannot be turned into a valid Transaction."""
    pass


class DataLoadError(Exception):
    """Raised when a file or folder cannot be read at all (I/O level failure)."""
    pass


@dataclass
class Transaction:
    """
    Represents a single validated sales transaction.

    Attributes
    ----------
    transaction_id : str
    date           : datetime.date
    product        : str
    customer       : str
    quantity       : int
    unit_price     : float
    category       : str   (derived from the folder path, e.g. "Electronics/Mobiles")
    region         : str
    payment_method : str
    source_file    : str   (path the row was read from - useful for auditing)
    """
    transaction_id: str
    date: datetime
    product: str
    customer: str
    quantity: int
    unit_price: float
    category: str
    region: str = "Unknown"
    payment_method: str = "Unknown"
    source_file: str = field(default="", repr=False)

    @property
    def total(self) -> float:
        """Total value of this transaction (quantity * unit price)."""
        return round(self.quantity * self.unit_price, 2)

    def to_dict(self) -> dict:
        return {
            "transaction_id": self.transaction_id,
            "date": self.date.strftime("%Y-%m-%d"),
            "product": self.product,
            "customer": self.customer,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "total": self.total,
            "category": self.category,
            "region": self.region,
            "payment_method": self.payment_method,
        }

    @staticmethod
    def from_row(row: dict, category: str, source_file: str = "") -> "Transaction":
        """
        Build and validate a Transaction from a raw CSV row (dict of strings).

        Raises
        ------
        InvalidTransactionError
            If any required field is missing, malformed, or fails a
            business rule (e.g. negative quantity/price, bad date).
        """
        required = ["transaction_id", "date", "product", "customer", "quantity", "unit_price"]
        for field_name in required:
            if field_name not in row or row[field_name] in (None, ""):
                raise InvalidTransactionError(
                    f"Missing required field '{field_name}' in row: {row}"
                )

        transaction_id = row["transaction_id"].strip()
        if not transaction_id:
            raise InvalidTransactionError(f"Empty transaction_id in row: {row}")

        # --- date validation ---
        raw_date = row["date"].strip()
        try:
            parsed_date = datetime.strptime(raw_date, "%Y-%m-%d")
        except ValueError as exc:
            raise InvalidTransactionError(
                f"Invalid date '{raw_date}' for transaction {transaction_id}: {exc}"
            ) from exc

        # --- quantity validation ---
        try:
            quantity = int(row["quantity"])
        except (TypeError, ValueError) as exc:
            raise InvalidTransactionError(
                f"Invalid quantity '{row['quantity']}' for transaction {transaction_id}"
            ) from exc
        if quantity <= 0:
            raise InvalidTransactionError(
                f"Quantity must be positive for transaction {transaction_id}, got {quantity}"
            )

        # --- unit price validation ---
        try:
            unit_price = float(row["unit_price"])
        except (TypeError, ValueError) as exc:
            raise InvalidTransactionError(
                f"Invalid unit_price '{row['unit_price']}' for transaction {transaction_id}"
            ) from exc
        if unit_price < 0:
            raise InvalidTransactionError(
                f"unit_price cannot be negative for transaction {transaction_id}, got {unit_price}"
            )

        product = row["product"].strip()
        customer = row["customer"].strip()
        if not product or not customer:
            raise InvalidTransactionError(
                f"Product and customer must not be empty for transaction {transaction_id}"
            )

        region = (row.get("region") or "Unknown").strip() or "Unknown"
        payment_method = (row.get("payment_method") or "Unknown").strip() or "Unknown"

        return Transaction(
            transaction_id=transaction_id,
            date=parsed_date,
            product=product,
            customer=customer,
            quantity=quantity,
            unit_price=unit_price,
            category=category,
            region=region,
            payment_method=payment_method,
            source_file=source_file,
        )
