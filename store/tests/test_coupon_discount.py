from datetime import timedelta
from decimal import Decimal

from django.utils import timezone
import pytest
from store.tests.factories import CouponFactory

from store.views import CheckoutView

class FakeRequest:
    
    def __init__(self, session=None):
        self.session = session or {}

@pytest.mark.django_db
def test_no_coupon_in_session_returns_zero_discount():
    request = FakeRequest(session={})
    view = CheckoutView()
    coupon, discount = view._get_coupon_discount(request, subtotal=Decimal("100.00"))
    # assert what?
    assert coupon is None
    assert discount == Decimal("0.00")

@pytest.mark.django_db
def test_valid_percentage_coupon_applies_discount():
    

    coupon = CouponFactory(
        code="TEST10",
        discount_type="percentage",
        discount_value=Decimal("10.00"),
        minimum_order=Decimal("50.00"),
        is_active=True,
    )
    request = FakeRequest(session={"coupon_code": "TEST10"})
    view = CheckoutView()
    subtotal = Decimal("100.00")
    applied_coupon, discount = view._get_coupon_discount(request, subtotal=subtotal)
    assert applied_coupon == coupon
    assert discount == Decimal("10.00")  # 10% of 100.00


@pytest.mark.django_db
def test_discount_greater_than_subtotal_returns_zero_discount():
    coupon = CouponFactory(
        code="TEST50",
        discount_type="percentage",
        discount_value=Decimal("50.00"),
        minimum_order=Decimal("50.00"),
        is_active=True,
    )
    request = FakeRequest(session={"coupon_code": "TEST50"})
    view = CheckoutView()
    subtotal = Decimal("30.00")  # less than minimum_order
    applied_coupon, discount = view._get_coupon_discount(request, subtotal=subtotal)
    assert applied_coupon is None
    assert discount == Decimal("0.00")
    
@pytest.mark.django_db
def test_expired_coupon_returns_zero_discount():
    coupon = CouponFactory(
        code="EXPIRED",
        discount_type="percentage",
        discount_value=Decimal("10.00"),
        minimum_order=Decimal("50.00"),
        valid_until=timezone.now() - timedelta(days=1),  # Simulate expired coupon
    )
    request = FakeRequest(session={"coupon_code": "EXPIRED"})
    view = CheckoutView()
    subtotal = Decimal("100.00")
    applied_coupon, discount = view._get_coupon_discount(request, subtotal=subtotal)
    assert "coupon_code" not in request.session  # Ensure the coupon code is removed from session
    assert applied_coupon is None
    assert discount == Decimal("0.00")
@pytest.mark.django_db
def test_coupon_not_in_DB():
    request = FakeRequest(session={"coupon_code": "NONEXISTENT"})
    view = CheckoutView()
    subtotal = Decimal("100.00")
    applied_coupon, discount = view._get_coupon_discount(request, subtotal=subtotal)
    assert "coupon_code" not in request.session  # Ensure the coupon code is removed from session
    assert applied_coupon is None
    assert discount == Decimal("0.00")