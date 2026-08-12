import pytest
from store.models import Review
from django.contrib.auth.models import User
from .factories import CategoryFactory, ProductFactory, UserFactory, ReviewFactory
@pytest.mark.django_db
def test_approved_review_updates_product_rating():
    new_review = ReviewFactory(rating=5)
    new_review.product.refresh_from_db()
    assert new_review.product.rating_avg == 5
    assert new_review.product.rating_count == 1

@pytest.mark.django_db
def test_unapproved_review_does_not_update_product_rating():

    new_review = ReviewFactory(is_approved=False)
    new_review.product.refresh_from_db()
    assert new_review.product.rating_avg == 0
    assert new_review.product.rating_count == 0
@pytest.mark.django_db
def test_deleting_approved_review_updates_product_rating():
    new_product = ProductFactory()
    new_review = ReviewFactory(rating=5, product=new_product)
    new_review1 = ReviewFactory(rating=4, product=new_product)
    new_review.product.refresh_from_db()
    assert new_review.product.rating_avg == 4.5
    assert new_review.product.rating_count == 2
    new_review.delete()
    new_review.product.refresh_from_db()
    assert new_review.product.rating_avg == 4
    assert new_review.product.rating_count == 1
    
@pytest.mark.django_db
def test_deleting_product_deletes_reviews():
    new_product = ProductFactory()
    new_review = ReviewFactory(product=new_product)
    new_review1 = ReviewFactory(product=new_product)
    pid = new_product.id
    assert Review.objects.filter(product=pid).count() == 2
    new_product.delete()
    assert Review.objects.filter(product_id=pid).count() == 0