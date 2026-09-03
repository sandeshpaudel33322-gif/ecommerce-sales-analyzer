

from datetime import datetime
from modules.models import Transaction


def make_transaction(transaction_id="TXN00001", date="2026-01-15", product="Widget",
                      customer="Alice", quantity=2, unit_price=10.0,
                      category="Electronics/Mobiles", region="Kathmandu",
                      payment_method="Credit Card"):
    return Transaction(
        transaction_id=transaction_id,
        date=datetime.strptime(date, "%Y-%m-%d"),
        product=product,
        customer=customer,
        quantity=quantity,
        unit_price=unit_price,
        category=category,
        region=region,
        payment_method=payment_method,
    )


def sample_dataset():
    """A small, hand-crafted dataset with known/expected totals for assertions."""
    return [
        make_transaction("TXN00001", "2026-01-10", "iPhone 15", "Alice", 1, 1000.0, "Electronics/Mobiles"),
        make_transaction("TXN00002", "2026-01-12", "Galaxy S24", "Bob", 2, 900.0, "Electronics/Mobiles"),
        make_transaction("TXN00003", "2026-02-05", "MacBook Air", "Alice", 1, 1500.0, "Electronics/Laptops"),
        make_transaction("TXN00004", "2026-02-20", "Men's Jacket", "Carol", 3, 50.0, "Clothing/Men"),
        make_transaction("TXN00005", "2026-03-01", "Women's Dress", "Dave", 1, 80.0, "Clothing/Women"),
        make_transaction("TXN00006", "2026-03-15", "Office Chair", "Bob", 1, 200.0, "HomeAndFurniture"),
    ]
