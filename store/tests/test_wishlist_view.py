from django.test import Client
from django.urls import reverse
import pytest

from store.tests.factories import ProductFactory, UserFactory

def test_anonymous_user_redirected_from_wishlist_toggle():
    client = Client()
    url = reverse('wishlist_toggle', args=[1])
    response = client.post(url)
    assert response.status_code == 302
@pytest.mark.django_db
def test_logged_in_user_can_toggle_wishlist():
    user = UserFactory()
    product = ProductFactory()
    client = Client()
    client.force_login(user)
    url = reverse("wishlist_toggle", args=[product.id])
    response = client.post(url)
    assert response.status_code == 200
    assert response.json()["added"] is True

@pytest.mark.django_db
def test_toggling_wishlist_twice_removes_product():
    user = UserFactory()
    product = ProductFactory()
    client = Client()
    client.force_login(user)
    url = reverse("wishlist_toggle", args=[product.id])
    client.post(url)  # first toggle - adds
    response = client.post(url)  # second toggle - removes
    assert response.status_code == 200
    assert response.json()["added"] is False