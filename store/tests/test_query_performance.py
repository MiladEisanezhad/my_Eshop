from django.test.utils import CaptureQueriesContext
from django.db import connection
import pytest

from store.tests.factories import CategoryFactory, ProductFactory, ProductImageFactory, ProductImageFactory, ReviewFactory, UserFactory

@pytest.mark.django_db
def test_product_reviews_use_select_related(django_assert_num_queries):
    product = ProductFactory()
    ReviewFactory(product=product)
    ReviewFactory(product=product)

    with django_assert_num_queries(1):
        reviews = list(product.reviews.filter(is_approved=True).select_related("user"))
        for review in reviews:
            _ = review.user.username  # accessing user shouldn't trigger extra queries

        # qs = (
        #     Product.objects.filter(status="published")
        #     .select_related("category", "brand")
        #     .prefetch_related(
        #         Prefetch(
        #             "images",
        #             queryset=ProductImage.objects.order_by("ordering"),
        #             to_attr="prefetched_images",
        #         )
        #     )
        # )
@pytest.mark.django_db
def test_shop_view_product_list_query_count():
    c1 = CategoryFactory()
    c2 = CategoryFactory()
    c3 = CategoryFactory()
    user1 = UserFactory()
    user2 = UserFactory()
    user3 = UserFactory()
    
    p1 = ProductFactory(category=c1, Images=[ProductImageFactory(), ProductImageFactory()])
    p2 = ProductFactory(category=c2, Images=[ProductImageFactory()])
    p3 = ProductFactory(category=c3, Images=[ProductImageFactory()])
    
    ReviewFactory(product=p1, user=user1)
    ReviewFactory(product=p2, user=user2)
    ReviewFactory(product=p3, user=user3)