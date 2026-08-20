from .factories import CategoryFactory, ProductFactory
from store.cache import serialize_products
import pytest
@pytest.mark.django_db
def test_serialize_products():
    category = CategoryFactory()
    product = ProductFactory(category=category)
    result = serialize_products([product])
    data = result[0]
    expected_compare_price = (
        str(product.compare_price)
        if product.compare_price
        else None
    )

    assert data["compare_price"] == expected_compare_price

    assert data["id"] == product.id
    assert data["name"] == product.name
    assert data["is_in_stock"] == product.is_in_stock
    assert data["category"]["name"] == product.category.name
    assert data["get_absolute_url"] == product.get_absolute_url()
    assert data["get_main_image_url"] == product.get_main_image_url()
    assert data["is_new_arrival"] == product.is_new_arrival
    assert data["discount_percent"] == product.discount_percent
    assert data["rating_count"] == product.rating_count
    assert data["rating_avg"] == str(product.rating_avg)
    assert data["is_on_sale"] == product.is_on_sale
    assert data["price"] == str(product.price)
    assert data["compare_price"] == expected_compare_price