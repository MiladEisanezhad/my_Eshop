import os
import django
from decimal import Decimal
import random

# 1. Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tailstore.settings')
django.setup()

# 2. Import Models & Faker
from django.contrib.auth.models import User
from django.utils import timezone
from faker import Faker

from store.models import (
    Category, Brand, Tag, Product, ProductImage, ProductVariant,
    Review, Wishlist, Coupon, Order, OrderItem, UserProfile,
    NewsletterSubscriber, Banner
)

fake = Faker()


def run_seeder():
    print("Clearing old data...")

    # IMPORTANT:
    # ProductImage و Banner عمداً حذف نمی‌شوند.
    # همچنین هیچ Image یا Banner جدیدی ایجاد نخواهد شد.

    Order.objects.all().delete()
    Review.objects.all().delete()
    Product.objects.all().delete()
    Category.objects.all().delete()
    Brand.objects.all().delete()
    Tag.objects.all().delete()
    Coupon.objects.all().delete()
    User.objects.exclude(is_superuser=True).delete()

    print("Creating Users...")
    users = []

    for _ in range(10):
        user = User.objects.create_user(
            username=fake.unique.user_name(),
            email=fake.unique.email(),
            password='password123',
            first_name=fake.first_name(),
            last_name=fake.last_name()
        )

        UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'phone': fake.phone_number()[:20],
                'default_address_line1': fake.street_address(),
                'default_city': fake.city(),
                'default_country': fake.country(),
            }
        )

        Wishlist.objects.get_or_create(user=user)
        users.append(user)

    print("Creating Categories...")

    parent_categories = []

    for _ in range(3):
        cat = Category.objects.create(
            name=fake.unique.word().capitalize() + " Parent",
            gender=random.choice(['men', 'women', 'kids', 'unisex']),
            description=fake.text()
        )

        parent_categories.append(cat)

    categories = []

    for parent in parent_categories:
        for _ in range(3):
            cat = Category.objects.create(
                name=fake.unique.word().capitalize(),
                parent=parent,
                gender=parent.gender
            )

            categories.append(cat)

    print("Creating Brands & Tags...")

    brands = [
        Brand.objects.create(
            name=fake.unique.company(),
            website=fake.url()
        )
        for _ in range(5)
    ]

    tags = [
        Tag.objects.create(
            name=fake.unique.word()
        )
        for _ in range(10)
    ]

    print("Creating Products & Variants...")

    products = []

    for _ in range(30):
        price = Decimal(
            random.uniform(10.0, 500.0)
        ).quantize(Decimal('0.01'))

        compare_price = (
            price + Decimal(
                random.uniform(5.0, 50.0)
            ).quantize(Decimal('0.01'))
            if random.choice([True, False])
            else None
        )

        product = Product.objects.create(
            name=fake.catch_phrase(),
            category=random.choice(categories),
            brand=random.choice(brands),
            short_description=fake.text(max_nb_chars=200),
            description=fake.paragraph(nb_sentences=5),
            price=price,
            compare_price=compare_price,
            total_stock=random.randint(0, 100),
            status='published',
            is_featured=random.choice([True, False])
        )

        product.tags.set(
            random.sample(
                tags,
                k=random.randint(1, 4)
            )
        )

        # IMPORTANT:
        # هیچ ProductImage ساخته نمی‌شود.
        #
        # ProductImage.objects.create(...) عمداً حذف شده است.

        # Variants
        for size in ['S', 'M', 'L']:
            ProductVariant.objects.create(
                product=product,
                size=size,
                color=fake.color_name(),
                stock=random.randint(5, 20)
            )

        products.append(product)

    print("Creating Reviews...")

    users = list(
        User.objects.exclude(is_superuser=True)
    )

    products = list(
        Product.objects.all()
    )

    for product in products:
        # برای هر محصول بین ۰ تا ۳ نظر
        num_reviews = random.randint(0, 3)

        # انتخاب کاربران یکتا برای هر محصول
        reviewers = random.sample(
            users,
            min(num_reviews, len(users))
        )

        for user in reviewers:
            Review.objects.create(
                product=product,
                user=user,
                rating=random.randint(1, 5),
                title=fake.sentence(),
                body=fake.paragraph(),
                is_approved=True,
                is_verified_purchase=random.choice(
                    [True, False]
                )
            )

    print("Creating Coupons...")

    Coupon.objects.create(
        code='SUMMER20',
        discount_type='percentage',
        discount_value=Decimal('20.00'),
        valid_from=timezone.now(),
        valid_until=timezone.now() + timezone.timedelta(days=30)
    )

    print("Creating Orders...")

    for _ in range(20):
        order_user = random.choice(users)

        order = Order.objects.create(
            user=order_user,
            status=random.choice([
                'pending',
                'processing',
                'shipped',
                'delivered'
            ]),
            first_name=order_user.first_name,
            last_name=order_user.last_name,
            email=order_user.email,
            shipping_address_line1=fake.street_address(),
            shipping_city=fake.city(),
            shipping_zip=fake.zipcode(),
            shipping_country=fake.country(),
            subtotal=Decimal('0.00'),
            total=Decimal('0.00')
        )

        # Order Items
        order_total = Decimal('0.00')

        for _ in range(random.randint(1, 4)):
            product = random.choice(products)
            variant = product.variants.first()

            qty = random.randint(1, 3)
            unit_price = product.price

            OrderItem.objects.create(
                order=order,
                product=product,
                variant=variant,
                product_name=product.name,
                unit_price=unit_price,
                quantity=qty
            )

            order_total += unit_price * qty

        order.subtotal = order_total
        order.total = order_total + order.shipping_cost
        order.save()

    print("Creating Newsletters...")

    for _ in range(5):
        NewsletterSubscriber.objects.get_or_create(
            email=fake.unique.email()
        )

    # IMPORTANT:
    # هیچ Banner جدیدی ساخته نمی‌شود.
    #
    # Banner.objects.create(...) عمداً حذف شده است.

    print(
        "Database seeding completed successfully! "
        "No ProductImage or Banner data was modified. ✅"
    )


if __name__ == '__main__':
    run_seeder()