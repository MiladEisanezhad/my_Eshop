import pytest
from store.models import Review
from django.contrib.auth.models import User
from .factories import CategoryFactory, ProductFactory, UserFactory, ReviewFactory

@pytest.mark.django_db
def test_approved_review_updates_product_rating():
    product1 = ProductFactory()
    user1 = UserFactory()
    new_review = ReviewFactory(rating=5, product=product1, user=user1, is_approved=True)
    new_review.product.refresh_from_db()
    assert new_review.product.rating_avg == 5
    assert new_review.product.rating_count == 1
    
@pytest.mark.django_db
def test_query_numbers_is_fixed_number(django_assert_num_queries):
    product1 = ProductFactory()
    ReviewFactory(product=product1, is_approved=True)
    ReviewFactory(product=product1, is_approved=True)
    ReviewFactory(product=product1, is_approved=True)
    with django_assert_num_queries(1):
        reviews = list(product1.reviews.filter(is_approved=True).select_related("user"))
        for review in reviews:
            _ = review.user.username