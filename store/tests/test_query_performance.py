from django.test.utils import CaptureQueriesContext
from django.db import connection
import pytest

from store.tests.factories import ProductFactory, ReviewFactory

@pytest.mark.django_db
def test_product_reviews_use_select_related(django_assert_num_queries):
    product = ProductFactory()
    ReviewFactory(product=product)
    ReviewFactory(product=product)

    with django_assert_num_queries(1):
        reviews = list(product.reviews.filter(is_approved=True).select_related("user"))
        for review in reviews:
            _ = review.user.username  # accessing user shouldn't trigger extra queries