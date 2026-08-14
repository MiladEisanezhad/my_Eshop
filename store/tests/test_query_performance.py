from django.db.models import Prefetch
from django.test.utils import CaptureQueriesContext
from django.db import connection
import pytest

from store.models import Product , ProductImage
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
def test_shop_view_product_list_query_count(django_assert_num_queries):
    categories = CategoryFactory.create_batch(3)
    users = UserFactory.create_batch(3)

    products = [
        ProductFactory(category=category)
        for category in categories
    ]

    image_counts = [2, 3, 2]

    for product, count in zip(products, image_counts):
        ProductImageFactory.create_batch(count, product=product)

    for product, user in zip(products, users):
        ReviewFactory(product=product, user=user)

    with django_assert_num_queries(2):
        qs = (
            Product.objects.filter(status="published")
            .select_related("category", "brand")
            .prefetch_related(
                Prefetch(
                    "images",
                    queryset=ProductImage.objects.order_by("ordering"),
                    to_attr="prefetched_images",
                )
            )
        )

        for product in qs:
            _ = product.category.name
            _ = product.brand.name if product.brand else None

            for image in product.prefetched_images:
                _ = image.image.url