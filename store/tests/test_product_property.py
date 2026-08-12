from decimal import Decimal

from store.models import Product

def test_discount_percent_with_compare_price():
    product = Product(name="Test Product", price=Decimal("80.00"), compare_price=Decimal("100.00"))
    assert product.discount_percent == 20.0
def test_discount_percent_with_no_compare_price():
    product = Product(name="Test Product", price=Decimal("100.00"))
    assert product.discount_percent == 0.0
def test_discount_percent_with_compare_price_greater_than_price():
    product = Product(name="Test Product", price=Decimal("120.00"), compare_price=Decimal("100.00"))
    assert product.discount_percent == 0.0
def test_discount_percent_with_compare_price_equal_to_price():
    product = Product(name="Test Product", price=Decimal("100.00"), compare_price=Decimal("100.00"))
    assert product.discount_percent == 0.0
def test_discount_percent_truncates_not_rounds():
    product = Product(name="Test Product", price=Decimal("66.50"), compare_price=Decimal("100.00"))
    assert product.discount_percent == 33  # fill in the correct expected value