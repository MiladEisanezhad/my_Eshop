from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver    
# ─────────────────────────────────────────────────────────────────────────────
# CATEGORY
# ─────────────────────────────────────────────────────────────────────────────


class Category(models.Model):
    GENDER_CHOICES = [
        ("men", "Men"),
        ("women", "Women"),
        ("kids", "Kids"),
        ("unisex", "Unisex"),
    ]

    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.SET_NULL,
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    ordering = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["ordering", "name"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["gender"]),
        ]

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} → {self.name}"
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("shop") + f"?category={self.slug}"


# ─────────────────────────────────────────────────────────────────────────────
# BRAND
# ─────────────────────────────────────────────────────────────────────────────


class Brand(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    logo = models.ImageField(upload_to="brands/", blank=True, null=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# ─────────────────────────────────────────────────────────────────────────────
# TAG
# ─────────────────────────────────────────────────────────────────────────────


class Tag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# ─────────────────────────────────────────────────────────────────────────────
# PRODUCT
# ─────────────────────────────────────────────────────────────────────────────


class Product(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("archived", "Archived"),
    ]

    # Core fields
    name = models.CharField(max_length=300, db_index=True)
    slug = models.SlugField(max_length=300, unique=True, db_index=True)
    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.PROTECT
    )
    brand = models.ForeignKey(
        Brand, related_name="products", null=True, blank=True, on_delete=models.SET_NULL
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="products")

    # Description
    short_description = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    material = models.CharField(max_length=200, blank=True)
    care_instructions = models.TextField(blank=True)

    # Pricing
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    compare_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Original / strike-through price",
    )
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Internal cost (not shown to customers)",
    )

    # Inventory
    sku = models.CharField(max_length=100, unique=True, blank=True)
    total_stock = models.PositiveIntegerField(default=0)
    track_stock = models.BooleanField(default=True)

    # Images
    main_image = models.ImageField(upload_to="products/", blank=True, null=True)

    # Meta
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="draft", db_index=True
    )
    is_featured = models.BooleanField(default=False, db_index=True)
    is_new_arrival = models.BooleanField(default=False, db_index=True)
    is_on_sale = models.BooleanField(default=False, db_index=True)
    weight = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True, help_text="kg"
    )

    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)

    # Stats (cached for performance)
    view_count = models.PositiveIntegerField(default=0)
    sales_count = models.PositiveIntegerField(default=0)
    
    rating_avg = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=0,
        help_text="Cached average rating — updated via signals",
    )
    rating_count = models.PositiveIntegerField(
        default=0, help_text="Cached approved review count — updated via signals"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "is_featured"]),
            models.Index(fields=["status", "is_new_arrival"]),
            models.Index(fields=["status", "is_on_sale"]),
            models.Index(fields=["category", "status"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.sku:
            import uuid

            self.sku = str(uuid.uuid4()).upper()[:12]
        # Auto-set is_on_sale
        if self.compare_price and self.compare_price > self.price:
            self.is_on_sale = True
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"slug": self.slug})

    @property
    def discount_percent(self):
        if self.compare_price and self.compare_price > self.price:
            discount = ((self.compare_price - self.price) / self.compare_price) * 100
            return int(discount)
        return 0

    @property
    def is_in_stock(self):
        if not self.track_stock:
            return True
        return self.total_stock > 0

    @property
    def average_rating(self):
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return round(reviews.aggregate(models.Avg("rating"))["rating__avg"], 1)
        return 0

    @property
    def review_count(self):
        return self.reviews.filter(is_approved=True).count()

    def get_main_image_url(self):
        if self.main_image:
            return self.main_image.url
        if hasattr(self, "prefetched_images"):
            image_list = self.prefetched_images
            if image_list and image_list[0].image:
                return image_list[0].image.url
            return "/static/images/products/1.jpg"
        else:
            images = self.images.all()
            first_image = images.first()
            if first_image and first_image.image:
                return first_image.image.url
            return "/static/images/products/1.jpg"
        
    def update_rating_cache(self):
        from django.db.models import Avg, Count
        result = self.reviews.filter(is_approved=True).aggregate(
            avg=Avg('rating'),
            count=Count('id')
        )
        self.rating_avg = round(result['avg'], 1) if result['avg'] else 0
        self.rating_count = result['count'] or 0
        self.save(update_fields=['rating_avg', 'rating_count'])

# ─────────────────────────────────────────────────────────────────────────────
# PRODUCT IMAGE
# ─────────────────────────────────────────────────────────────────────────────


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="products/gallery/")
    alt_text = models.CharField(max_length=200, blank=True)
    ordering = models.PositiveIntegerField(default=0)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ["ordering"]

    def __str__(self):
        return f"{self.product.name} — image {self.ordering}"


# ─────────────────────────────────────────────────────────────────────────────
# PRODUCT VARIANT (size/color combinations)
# ─────────────────────────────────────────────────────────────────────────────


class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product, related_name="variants", on_delete=models.CASCADE
    )
    size = models.CharField(max_length=20, blank=True)  # XS, S, M, L, XL, XXL, 38, 40…
    color = models.CharField(max_length=50, blank=True)
    color_hex = models.CharField(max_length=7, blank=True)  # e.g. #FF0042
    sku = models.CharField(max_length=100, unique=True, blank=True)
    price_adjustment = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Added to / subtracted from base price",
    )
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="products/variants/", blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("product", "size", "color")
        ordering = ["size", "color"]

    def __str__(self):
        parts = [self.product.name]
        if self.size:
            parts.append(self.size)
        if self.color:
            parts.append(self.color)
        return " / ".join(parts)

    def save(self, *args, **kwargs):
        if not self.sku:
            import uuid

            self.sku = f"{self.product.sku}-{str(uuid.uuid4()).upper()[:6]}"
        super().save(*args, **kwargs)

    @property
    def final_price(self):
        return self.product.price + self.price_adjustment

    @property
    def is_in_stock(self):
        return self.stock > 0


# ─────────────────────────────────────────────────────────────────────────────
# REVIEW
# ─────────────────────────────────────────────────────────────────────────────


class Review(models.Model):
    product = models.ForeignKey(
        Product, related_name="reviews", on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, related_name="reviews", on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=200, blank=True)
    body = models.TextField()
    is_approved = models.BooleanField(default=False)
    is_verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("product", "user")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} → {self.product.name} ({self.rating}★)"


# ─────────────────────────────────────────────────────────────────────────────
# WISHLIST
# ─────────────────────────────────────────────────────────────────────────────


class Wishlist(models.Model):
    user = models.OneToOneField(User, related_name="wishlist", on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, blank=True, related_name="wishlisted_by")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s wishlist"


# ─────────────────────────────────────────────────────────────────────────────
# COUPON
# ─────────────────────────────────────────────────────────────────────────────


class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ("percentage", "Percentage"),
        ("fixed", "Fixed Amount"),
        ("free_shipping", "Free Shipping"),
    ]

    code = models.CharField(max_length=50, unique=True, db_index=True)
    discount_type = models.CharField(max_length=15, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=8, decimal_places=2)
    minimum_order = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    usage_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    applicable_products = models.ManyToManyField(Product, blank=True)
    applicable_categories = models.ManyToManyField(Category, blank=True)

    def __str__(self):
        return self.code

    def is_valid(self):
        from django.utils import timezone

        now = timezone.now()
        if not self.is_active:
            return False
        if now < self.valid_from or now > self.valid_until:
            return False
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False
        return True


# ─────────────────────────────────────────────────────────────────────────────
# ORDER
# ─────────────────────────────────────────────────────────────────────────────


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
    ]
    PAYMENT_STATUS_CHOICES = [
        ("unpaid", "Unpaid"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]
    PAYMENT_METHOD_CHOICES = [
        ("card", "Credit / Debit Card"),
        ("paypal", "PayPal"),
        ("cod", "Cash on Delivery"),
        ("stripe", "Stripe"),
    ]

    user = models.ForeignKey(
        User, related_name="orders", null=True, blank=True, on_delete=models.SET_NULL
    )
    order_number = models.CharField(max_length=32, unique=True, db_index=True)
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pending", db_index=True
    )
    payment_status = models.CharField(
        max_length=10, choices=PAYMENT_STATUS_CHOICES, default="unpaid"
    )
    payment_method = models.CharField(
        max_length=10, choices=PAYMENT_METHOD_CHOICES, blank=True
    )

    # Customer info (snapshot at time of order)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)

    # Shipping address
    shipping_address_line1 = models.CharField(max_length=255)
    shipping_address_line2 = models.CharField(max_length=255, blank=True)
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100, blank=True)
    shipping_zip = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100)

    # Billing address (optional, defaults to shipping)
    billing_same_as_shipping = models.BooleanField(default=True)
    billing_address_line1 = models.CharField(max_length=255, blank=True)
    billing_address_line2 = models.CharField(max_length=255, blank=True)
    billing_city = models.CharField(max_length=100, blank=True)
    billing_state = models.CharField(max_length=100, blank=True)
    billing_zip = models.CharField(max_length=20, blank=True)
    billing_country = models.CharField(max_length=100, blank=True)

    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal("0.00")
    )
    tax = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("0.00"))
    discount = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal("0.00")
    )
    total = models.DecimalField(max_digits=10, decimal_places=2)

    coupon = models.ForeignKey(
        Coupon, null=True, blank=True, on_delete=models.SET_NULL, related_name="orders"
    )
    notes = models.TextField(blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["order_number"]),
        ]

    def __str__(self):
        return f"Order #{self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            import uuid

            self.order_number = str(uuid.uuid4()).replace("-", "").upper()[:16]
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def shipping_address(self):
        parts = [self.shipping_address_line1]
        if self.shipping_address_line2:
            parts.append(self.shipping_address_line2)
        parts.extend([self.shipping_city, self.shipping_zip, self.shipping_country])
        return ", ".join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# ORDER ITEM
# ─────────────────────────────────────────────────────────────────────────────


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, related_name="order_items", on_delete=models.PROTECT
    )
    variant = models.ForeignKey(
        ProductVariant,
        null=True,
        blank=True,
        related_name="order_items",
        on_delete=models.SET_NULL,
    )

    # Snapshot at time of purchase
    product_name = models.CharField(max_length=300)
    variant_info = models.CharField(max_length=200, blank=True)  # e.g. "M / Black"
    sku = models.CharField(max_length=100, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return (
            f"{self.quantity}× {self.product_name} (Order #{self.order.order_number})"
        )

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)


# ─────────────────────────────────────────────────────────────────────────────
# USER PROFILE
# ─────────────────────────────────────────────────────────────────────────────


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    newsletter_subscribed = models.BooleanField(default=False)

    # Default shipping address
    default_address_line1 = models.CharField(max_length=255, blank=True)
    default_address_line2 = models.CharField(max_length=255, blank=True)
    default_city = models.CharField(max_length=100, blank=True)
    default_state = models.CharField(max_length=100, blank=True)
    default_zip = models.CharField(max_length=20, blank=True)
    default_country = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} profile"


# ─────────────────────────────────────────────────────────────────────────────
# NEWSLETTER SUBSCRIBER
# ─────────────────────────────────────────────────────────────────────────────


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True, db_index=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


# ─────────────────────────────────────────────────────────────────────────────
# BANNER / SLIDER
# ─────────────────────────────────────────────────────────────────────────────


class Banner(models.Model):
    POSITION_CHOICES = [
        ("main_slider", "Main Slider"),
        ("category_banner", "Category Banner"),
        ("promo_banner", "Promo Banner"),
    ]

    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to="banners/", blank=True)
    link_url = models.CharField(max_length=300, blank=True)
    link_text = models.CharField(max_length=100, blank=True)
    position = models.CharField(
        max_length=20, choices=POSITION_CHOICES, default="main_slider"
    )
    ordering = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position", "ordering"]

    def __str__(self):
        return f"{self.title} ({self.position})"


@receiver(post_save, sender=Review)
def update_product_rating_on_save(sender, instance, **kwargs):
    instance.product.update_rating_cache()

@receiver(post_delete, sender=Review)
def update_product_rating_on_delete(sender, instance, **kwargs):
    instance.product.update_rating_cache()