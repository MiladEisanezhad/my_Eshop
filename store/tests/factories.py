import factory

from store.models import Category, Product, Review, User


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
    