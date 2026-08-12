import pytest

def test_sanity():
    assert 1 + 1 == 2
@pytest.mark.django_db
def test_can_query_products():
    from store.models import Product
    assert Product.objects.count() == 0