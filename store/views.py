from decimal import Decimal
import json
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Max, Min, Q, Avg, Count, Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView

from .cart import Cart
from .models import (
    Banner,
    Brand,
    Category,
    Coupon,
    NewsletterSubscriber,
    Order,
    OrderItem,
    Product,
    Review,
    UserProfile,
    Wishlist,
    ProductImage,
)

# ─────────────────────────────────────────────────────────────────────────────
# HOME
# ─────────────────────────────────────────────────────────────────────────────


class HomeView(TemplateView):
    template_name = "store/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(
            {
                "featured_products": (
                    Product.objects.filter(status="published", is_featured=True)
                    .select_related("category")
                    .prefetch_related(
                        Prefetch(
                            "images",
                            queryset=ProductImage.objects.order_by("ordering"),
                            to_attr="prefetched_images",
                        )
                    )
                    .annotate(
                        avg_rating=Avg(
                            "reviews__rating", filter=Q(reviews__is_approved=True)
                        ),
                        review_total=Count(
                            "reviews", filter=Q(reviews__is_approved=True)
                        ),
                    )[:8]
                ),
                "new_arrivals": (
                    Product.objects.filter(status="published", is_new_arrival=True)
                    .select_related("category")
                    .prefetch_related(
                        Prefetch(
                            "images",
                            queryset=ProductImage.objects.order_by("ordering"),
                            to_attr="prefetched_images",
                        )
                    )
                    .annotate(
                        avg_rating=Avg(
                            "reviews__rating", filter=Q(reviews__is_approved=True)
                        ),
                        review_total=Count(
                            "reviews", filter=Q(reviews__is_approved=True)
                        ),
                    )[:8]
                ),
                "on_sale_products": (
                    Product.objects.filter(status="published", is_on_sale=True)
                    .select_related("category")
                    .prefetch_related(
                        Prefetch(
                            "images",
                            queryset=ProductImage.objects.order_by("ordering"),
                            to_attr="prefetched_images",
                        )
                    )
                    .annotate(
                        avg_rating=Avg(
                            "reviews__rating", filter=Q(reviews__is_approved=True)
                        ),
                        review_total=Count(
                            "reviews", filter=Q(reviews__is_approved=True)
                        ),
                    )[:8]
                ),
                "banners": Banner.objects.filter(
                    is_active=True, position="main_slider"
                ).order_by("ordering"),
                "category_banners": Banner.objects.filter(
                    is_active=True, position="category_banner"
                ).order_by("ordering")[:3],
                "brands": Brand.objects.filter(is_active=True),
            }
        )
        return ctx


# ─────────────────────────────────────────────────────────────────────────────
# SHOP / PRODUCT LIST
# ─────────────────────────────────────────────────────────────────────────────


class ShopView(ListView):
    template_name = "store/shop.html"
    context_object_name = "products"

    SORT_MAP = {
        "newest": "-created_at",
        "oldest": "created_at",
        "price_asc": "price",
        "price_desc": "-price",
        "name_asc": "name",
        "name_desc": "-name",
        "popular": "-sales_count",
    }

    GENDER_CHOICES = [
        ("men", "Men"),
        ("women", "Women"),
        ("kids", "Kids"),
        ("unisex", "Unisex"),
    ]

    def get_queryset(self):
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
            .annotate(
                avg_rating=Avg("reviews__rating", filter=Q(reviews__is_approved=True)),
                review_total=Count("reviews", filter=Q(reviews__is_approved=True)),
            )
        )
        p = self.request.GET

        # Category filter (includes children)
        self._selected_category = None
        category_slug = p.get("category")
        if category_slug:
            self._selected_category = get_object_or_404(
                Category, slug=category_slug, is_active=True
            )
            cat_ids = [self._selected_category.id] + list(
                self._selected_category.children.values_list("id", flat=True)
            )
            qs = qs.filter(category__id__in=cat_ids)

        if p.get("brand"):
            qs = qs.filter(brand__slug=p["brand"])

        if p.get("gender"):
            qs = qs.filter(category__gender=p["gender"])

        if p.get("q"):
            qs = qs.filter(
                Q(name__icontains=p["q"])
                | Q(description__icontains=p["q"])
                | Q(brand__name__icontains=p["q"])
                | Q(tags__name__icontains=p["q"])
            ).distinct()

        if p.get("tag"):
            qs = qs.filter(tags__slug=p["tag"])

        for param, lookup in (("min_price", "price__gte"), ("max_price", "price__lte")):
            if p.get(param):
                try:
                    qs = qs.filter(**{lookup: Decimal(p[param])})
                except Exception:
                    pass

        if p.get("sale"):
            qs = qs.filter(is_on_sale=True)
        if p.get("new"):
            qs = qs.filter(is_new_arrival=True)

        sort = p.get("sort", "newest")
        self._current_sort = sort
        return qs.order_by(self.SORT_MAP.get(sort, "-created_at"))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(
            {
                "categories": Category.objects.filter(is_active=True, parent=None),
                "brands": Brand.objects.filter(is_active=True),
                "selected_category": getattr(self, "_selected_category", None),
                "current_sort": getattr(self, "_current_sort", "newest"),
                "price_range": Product.objects.filter(status="published").aggregate(
                    min_p=Min("price"), max_p=Max("price")
                ),
                "search_q": self.request.GET.get("q", ""),
                "total_products": self.get_queryset().count(),
                "gender_choices": self.GENDER_CHOICES,
            }
        )
        return ctx


# ─────────────────────────────────────────────────────────────────────────────
# PRODUCT DETAIL
# ─────────────────────────────────────────────────────────────────────────────


class ProductDetailView(View):
    template_name = "store/single_product.html"

    def _get_product(self, slug):
        return get_object_or_404(Product, slug=slug, status="published")

    def _build_context(self, product):
        variants = product.variants.filter(is_active=True)
        return {
            "product": product,
            "images": product.images.all(),
            "variants": variants,
            "sizes": list(
                variants.values_list("size", flat=True).distinct().exclude(size="")
            ),
            "colors": list(
                variants.values_list("color", "color_hex").distinct().exclude(color="")
            ),
            "reviews": product.reviews.filter(is_approved=True).select_related("user"),
            "related_products": Product.objects.filter(
                category=product.category, status="published"
            ).exclude(id=product.id)[:4],
            "variants_json": json.dumps(
                [
                    {
                        "id": v.id,
                        "size": v.size,
                        "color": v.color,
                        "stock": v.stock,
                        "price": str(v.final_price),
                    }
                    for v in variants
                ]
            ),
        }

    def get(self, request, slug):
        product = self._get_product(slug)
        product.view_count += 1
        product.save(update_fields=["view_count"])

        ctx = self._build_context(product)
        ctx["user_review"] = (
            Review.objects.filter(product=product, user=request.user).first()
            if request.user.is_authenticated
            else None
        )
        return render(request, self.template_name, ctx)

    def post(self, request, slug):
        product = self._get_product(slug)
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to submit a review.")
            return redirect("login")

        rating = request.POST.get("rating")
        body = request.POST.get("body", "")
        if rating and body:
            Review.objects.update_or_create(
                product=product,
                user=request.user,
                defaults={
                    "rating": int(rating),
                    "title": request.POST.get("title", ""),
                    "body": body,
                    "is_approved": False,
                },
            )
            messages.success(
                request, "Your review has been submitted and is pending approval."
            )
        return redirect("product_detail", slug=slug)


# ─────────────────────────────────────────────────────────────────────────────
# CART
# ─────────────────────────────────────────────────────────────────────────────


class CartView(TemplateView):
    template_name = "store/cart.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["cart_items"] = Cart(self.request).get_items_list()
        return ctx


class CartAddView(View):
    def post(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id, status="published")
        try:
            data = json.loads(request.body)
        except Exception:
            data = {}
        quantity = int(data.get("quantity", request.POST.get("quantity", 1)))
        variant_id = data.get("variant_id") or request.POST.get("variant_id")
        if variant_id:
            variant_id = int(variant_id)
        cart.add(product, quantity=quantity, variant_id=variant_id)
        return JsonResponse(
            {
                "success": True,
                "cart_count": len(cart),
                "cart_total": str(cart.get_total_price()),
                "message": f'"{product.name}" added to cart.',
            }
        )


class CartRemoveView(View):
    def post(self, request, key):
        cart = Cart(request)
        cart.remove(key)
        return JsonResponse(
            {
                "success": True,
                "cart_count": len(cart),
                "cart_total": str(cart.get_total_price()),
            }
        )


class CartUpdateView(View):
    def post(self, request, key):
        cart = Cart(request)
        try:
            data = json.loads(request.body)
        except Exception:
            data = {}
        quantity = int(data.get("quantity", 1))
        cart.update_quantity(key, quantity)
        return JsonResponse(
            {
                "success": True,
                "cart_count": len(cart),
                "cart_total": str(cart.get_total_price()),
            }
        )


# ─────────────────────────────────────────────────────────────────────────────
# CHECKOUT
# ─────────────────────────────────────────────────────────────────────────────


class CheckoutView(View):
    template_name = "store/checkout.html"

    # ── helpers ──────────────────────────────────────────────────────────────

    def _get_initial(self, request):
        """Pre-fill form fields from the logged-in user's profile."""
        if not request.user.is_authenticated:
            return {}
        base = {
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email,
        }
        try:
            p = request.user.profile
            base.update(
                {
                    "phone": p.phone,
                    "address_line1": p.default_address_line1,
                    "city": p.default_city,
                    "zip": p.default_zip,
                    "country": p.default_country,
                }
            )
        except UserProfile.DoesNotExist:
            pass
        return base

    def _get_coupon_discount(self, request, subtotal):
        """Validate session coupon and return (coupon_obj, discount_amount)."""
        code = request.session.get("coupon_code")
        if not code:
            return None, Decimal("0.00")
        try:
            coupon = Coupon.objects.get(code=code)
            if not coupon.is_valid():
                raise ValueError
            if coupon.discount_type == "percentage":
                discount = (subtotal * coupon.discount_value / 100).quantize(
                    Decimal("0.01")
                )
            elif coupon.discount_type == "fixed":
                discount = min(coupon.discount_value, subtotal)
            else:
                discount = Decimal("0.00")
            return coupon, discount
        except (Coupon.DoesNotExist, ValueError):
            del request.session["coupon_code"]
            return None, Decimal("0.00")

    def _compute_totals(self, subtotal, coupon_discount):
        shipping_cost = Decimal("5.99") if subtotal < Decimal("50") else Decimal("0.00")
        tax = (subtotal * Decimal("0.08")).quantize(Decimal("0.01"))
        total = subtotal + shipping_cost + tax - coupon_discount
        return shipping_cost, tax, total

    def _build_context(self, request, cart, cart_items, coupon_obj, coupon_discount):
        subtotal = cart.get_total_price()
        shipping_cost, tax, total = self._compute_totals(subtotal, coupon_discount)
        return {
            "cart_items": cart_items,
            "subtotal": subtotal,
            "shipping_cost": shipping_cost,
            "tax": tax,
            "coupon_discount": coupon_discount,
            "total": total,
            "coupon_code": request.session.get("coupon_code"),
            "initial": self._get_initial(request),
        }

    # ── GET ──────────────────────────────────────────────────────────────────

    def get(self, request):
        cart = Cart(request)
        cart_items = cart.get_items_list()
        if not cart_items:
            messages.warning(request, "Your cart is empty.")
            return redirect("cart")
        subtotal = cart.get_total_price()
        coupon_obj, coupon_discount = self._get_coupon_discount(request, subtotal)
        ctx = self._build_context(
            request, cart, cart_items, coupon_obj, coupon_discount
        )
        return render(request, self.template_name, ctx)

    # ── POST ─────────────────────────────────────────────────────────────────

    def post(self, request):
        cart = Cart(request)
        cart_items = cart.get_items_list()
        if not cart_items:
            messages.warning(request, "Your cart is empty.")
            return redirect("cart")

        subtotal = cart.get_total_price()
        coupon_obj, coupon_discount = self._get_coupon_discount(request, subtotal)
        shipping_cost, tax, total = self._compute_totals(subtotal, coupon_discount)

        p = request.POST
        order = Order(
            first_name=p.get("first_name", ""),
            last_name=p.get("last_name", ""),
            email=p.get("email", ""),
            phone=p.get("phone", ""),
            shipping_address_line1=p.get("address_line1", ""),
            shipping_address_line2=p.get("address_line2", ""),
            shipping_city=p.get("city", ""),
            shipping_state=p.get("state", ""),
            shipping_zip=p.get("zip", ""),
            shipping_country=p.get("country", ""),
            payment_method=p.get("payment_method", "cod"),
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            tax=tax,
            discount=coupon_discount,
            total=total,
            coupon=coupon_obj,
        )
        if request.user.is_authenticated:
            order.user = request.user
        order.save()

        for item in cart_items:
            product = item["product"]
            OrderItem.objects.create(
                order=order,
                product=product,
                variant_id=item.get("variant_id"),
                product_name=item["name"],
                variant_info=item.get("variant_info", ""),
                sku=product.sku,
                unit_price=item["price"],
                quantity=item["quantity"],
                total_price=item["total_price"],
                image_url=item.get("image", ""),
            )
            if product.track_stock:
                product.total_stock = max(0, product.total_stock - item["quantity"])
                product.sales_count += item["quantity"]
                product.save(update_fields=["total_stock", "sales_count"])

        if coupon_obj:
            coupon_obj.usage_count += 1
            coupon_obj.save(update_fields=["usage_count"])
            del request.session["coupon_code"]

        cart.clear()
        messages.success(request, f"Order #{order.order_number} placed successfully!")
        return redirect("order_confirmation", order_number=order.order_number)


class ApplyCouponView(View):
    def post(self, request):
        code = request.POST.get("coupon_code", "").strip().upper()
        try:
            coupon = Coupon.objects.get(code=code)
            if coupon.is_valid():
                request.session["coupon_code"] = code
                messages.success(request, f'Coupon "{code}" applied!')
            else:
                messages.error(request, "This coupon is expired or invalid.")
        except Coupon.DoesNotExist:
            messages.error(request, "Coupon code not found.")
        return redirect("checkout")


class OrderConfirmationView(DetailView):
    model = Order
    template_name = "store/order_confirmation.html"
    context_object_name = "order"
    slug_field = "order_number"
    slug_url_kwarg = "order_number"


# ─────────────────────────────────────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────────────────────────────────────


class RegisterView(View):
    template_name = "store/register.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home")
        return render(request, self.template_name)

    def post(self, request):
        if request.user.is_authenticated:
            return redirect("home")

        first_name = request.POST.get("first_name", "")
        last_name = request.POST.get("last_name", "")
        email = request.POST.get("email", "")
        username = request.POST.get("username", email)
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")

        if password != password2:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, f"Welcome, {first_name}! Account created.")
            return redirect("home")

        return render(request, self.template_name)


class LoginView(View):
    template_name = "store/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home")
        return render(request, self.template_name)

    def post(self, request):
        if request.user.is_authenticated:
            return redirect("home")

        user = authenticate(
            request,
            username=request.POST.get("username", ""),
            password=request.POST.get("password", ""),
        )
        if user:
            login(request, user)
            return redirect(request.GET.get("next", "home"))

        messages.error(request, "Invalid username or password.")
        return render(request, self.template_name)


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("home")

    # Also handle POST (more secure)
    def post(self, request):
        logout(request)
        return redirect("home")


# ─────────────────────────────────────────────────────────────────────────────
# ACCOUNT
# ─────────────────────────────────────────────────────────────────────────────


class AccountView(LoginRequiredMixin, View):
    template_name = "store/account.html"
    login_url = "/login/"

    def _get_profile(self, user):
        profile, _ = UserProfile.objects.get_or_create(user=user)
        return profile

    def get(self, request):
        ctx = {
            "orders": Order.objects.filter(user=request.user).order_by("-created_at"),
            "profile": self._get_profile(request.user),
        }
        return render(request, self.template_name, ctx)

    def post(self, request):
        profile = self._get_profile(request.user)
        p = request.POST

        # Update User fields
        request.user.first_name = p.get("first_name", request.user.first_name)
        request.user.last_name = p.get("last_name", request.user.last_name)
        request.user.email = p.get("email", request.user.email)
        request.user.save()

        # Update Profile fields
        profile.phone = p.get("phone", profile.phone)
        profile.default_address_line1 = p.get("address_line1", "")
        profile.default_city = p.get("city", "")
        profile.default_zip = p.get("zip", "")
        profile.default_country = p.get("country", "")
        profile.save()

        messages.success(request, "Profile updated.")
        return redirect("account")


# ─────────────────────────────────────────────────────────────────────────────
# WISHLIST
# ─────────────────────────────────────────────────────────────────────────────


class WishlistView(LoginRequiredMixin, TemplateView):
    template_name = "store/wishlist.html"
    login_url = "/login/"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        wishlist, _ = Wishlist.objects.get_or_create(user=self.request.user)
        ctx["wishlist"] = wishlist
        return ctx


class WishlistToggleView(LoginRequiredMixin, View):
    login_url = "/login/"

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id, status="published")
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        if product in wishlist.products.all():
            wishlist.products.remove(product)
            added = False
        else:
            wishlist.products.add(product)
            added = True
        return JsonResponse({"added": added, "count": wishlist.products.count()})


# ─────────────────────────────────────────────────────────────────────────────
# NEWSLETTER
# ─────────────────────────────────────────────────────────────────────────────


class NewsletterSubscribeView(View):
    def post(self, request):
        email = request.POST.get("email", "").strip()
        if email:
            _, created = NewsletterSubscriber.objects.get_or_create(email=email)
            if created:
                messages.success(request, "Thanks for subscribing!")
            else:
                messages.info(request, "You are already subscribed.")
        return redirect(request.META.get("HTTP_REFERER", "home"))


# ─────────────────────────────────────────────────────────────────────────────
# SEARCH (AJAX)
# ─────────────────────────────────────────────────────────────────────────────


class SearchSuggestionsView(View):
    def get(self, request):
        q = request.GET.get("q", "")
        results = []
        if len(q) >= 2:
            products = Product.objects.filter(
                name__icontains=q, status="published"
            ).values("name", "slug", "price")[:6]
            results = [{**p, "price": str(p["price"])} for p in products]
        return JsonResponse({"results": results})


# ─────────────────────────────────────────────────────────────────────────────
# 404
# ─────────────────────────────────────────────────────────────────────────────


def custom_404(request, exception):
    return render(request, "store/404.html", status=404)


def my_view(request):
    tech_stack = ["html", "js", "laravel", "php", "react", "tailwind", "typescript"]
    return render(request, "store/index.html", {"tech_stack": tech_stack})
