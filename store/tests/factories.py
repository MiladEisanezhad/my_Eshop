from datetime import timezone

import factory

from store.models import Category, Coupon, Product, ProductImage, Review, User


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Category {n}")
    slug = factory.Sequence(lambda n: f"category-{n}")


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product
    name = factory.Sequence(lambda n: f"Product {n}")
    slug = factory.Sequence(lambda n: f"product-{n}")
    price = factory.Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
    category = factory.SubFactory(CategoryFactory)
    status = "published"
    
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    password = factory.Sequence(lambda n: f"password")
    is_active = True
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")

class ReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Review
    user = factory.SubFactory(UserFactory)
    product = factory.SubFactory(ProductFactory)
    rating = factory.Faker("random_int", min=1, max=5)
    is_approved = True
    
class ProductImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductImage

    product = factory.SubFactory(ProductFactory)
    image = factory.django.ImageField(color="blue")
    ordering = factory.Sequence(lambda n: n)
    
class CouponFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Coupon

    code = factory.Sequence(lambda n: f"COUPON{n}")
    discount_type = "percentage"
    discount_value = factory.Faker("pydecimal", left_digits=2, right_digits=2, positive=True)
    minimum_order = factory.Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
    valid_from = factory.Faker("date_time_this_year", before_now=True, after_now=False, tzinfo=timezone.utc)
    valid_until = factory.Faker("date_time_this_year", before_now=False, after_now=True, tzinfo=timezone.utc)
    is_active = True