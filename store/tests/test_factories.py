import pytest
from store.models import Category
from store.tests.factories import CategoryFactory, ProductFactory, ReviewFactory

@pytest.mark.django_db
def test_category_factory_creates_valid_category():
    category = CategoryFactory()
    assert category.pk is not None
    assert category.name.startswith("Category")

@pytest.mark.django_db
def test_product_factory_creates_valid_product():
    product = ProductFactory()
    assert product.pk is not None
    assert product.name.startswith("Product")
    assert product.price > 0
    assert product.category is not None

@pytest.mark.django_db
def test_products_can_share_same_category():
    
    category = CategoryFactory()
    p1 = ProductFactory(category=category)
    p2 = ProductFactory(category=category)
    p3 = ProductFactory(category=category)
    assert p1.category == category
    assert p2.category == category
    assert p3.category == category
    assert Category.objects.count() == 1

@pytest.mark.django_db
def test_review_factory_creates_valid_review():
    review = ReviewFactory()
    assert review.pk is not None
    assert 1 <= review.rating <= 5
    assert review.user is not None
    assert review.product is not None
@pytest.mark.django_db
def test_multiple_reviews_for_same_product():
    product = ProductFactory()
    review1 = ReviewFactory(product=product)
    review2 = ReviewFactory(product=product)
    review3 = ReviewFactory(product=product)
    assert review1.product == product
    assert review2.product == product
    assert review3.product == product
    product.refresh_from_db()
    assert product.reviews.count() == 3
    assert product.rating_count == 3