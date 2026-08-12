from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category, Brand, Tag, Product, ProductImage, ProductVariant,
    Review, Wishlist, Coupon, Order, OrderItem, UserProfile,
    NewsletterSubscriber, Banner
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'gender', 'is_active', 'ordering']
    list_filter = ['gender', 'is_active', 'parent']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['ordering', 'name']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ['image', 'alt_text', 'ordering', 'is_primary']


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 2
    fields = ['size', 'color', 'color_hex', 'sku', 'price_adjustment', 'stock', 'is_active']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'brand', 'price', 'compare_price',
                    'total_stock', 'status', 'is_featured', 'is_new_arrival', 'preview_image']
    list_filter = ['status', 'is_featured', 'is_new_arrival', 'is_on_sale', 'category', 'brand']
    search_fields = ['name', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['status', 'is_featured', 'is_new_arrival', 'price']
    readonly_fields = ['sku', 'discount_percent', 'average_rating', 'review_count',
                       'view_count', 'sales_count', 'created_at', 'updated_at']
    inlines = [ProductImageInline, ProductVariantInline]

    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'slug', 'sku', 'category', 'brand', 'tags', 'status')
        }),
        ('Description', {
            'fields': ('short_description', 'description', 'material', 'care_instructions')
        }),
        ('Pricing', {
            'fields': ('price', 'compare_price', 'cost_price', 'discount_percent')
        }),
        ('Inventory', {
            'fields': ('total_stock', 'track_stock', 'weight')
        }),
        ('Media', {
            'fields': ('main_image',)
        }),
        ('Visibility', {
            'fields': ('is_featured', 'is_new_arrival', 'is_on_sale')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Stats', {
            'fields': ('view_count', 'sales_count', 'average_rating', 'review_count',
                       'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def preview_image(self, obj):
        url = obj.get_main_image_url()
        return format_html('<img src="{}" style="height:50px;width:50px;object-fit:cover;border-radius:4px;" />', url)
    preview_image.short_description = 'Image'

    def discount_percent(self, obj):
        return f'{obj.discount_percent}%'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'is_approved', 'is_verified_purchase', 'created_at']
    list_filter = ['rating', 'is_approved', 'is_verified_purchase']
    list_editable = ['is_approved']
    search_fields = ['product__name', 'user__username', 'body']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'variant_info', 'sku', 'unit_price', 'quantity', 'total_price']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'email', 'total', 'status',
                    'payment_status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'first_name', 'last_name', 'email']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    list_editable = ['status', 'payment_status']
    inlines = [OrderItemInline]

    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'user', 'status', 'payment_status', 'payment_method',
                       'notes', 'tracking_number', 'created_at', 'updated_at')
        }),
        ('Customer', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Shipping Address', {
            'fields': ('shipping_address_line1', 'shipping_address_line2',
                       'shipping_city', 'shipping_state', 'shipping_zip', 'shipping_country')
        }),
        ('Billing Address', {
            'fields': ('billing_same_as_shipping', 'billing_address_line1',
                       'billing_city', 'billing_zip', 'billing_country'),
            'classes': ('collapse',)
        }),
        ('Pricing', {
            'fields': ('subtotal', 'shipping_cost', 'tax', 'discount', 'total', 'coupon')
        }),
    )


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'usage_count',
                    'usage_limit', 'is_active', 'valid_from', 'valid_until']
    list_filter = ['discount_type', 'is_active']
    search_fields = ['code']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'newsletter_subscribed', 'created_at']
    search_fields = ['user__username', 'user__email']


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active', 'subscribed_at']
    list_filter = ['is_active']
    search_fields = ['email']


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'position', 'ordering', 'is_active']
    list_filter = ['position', 'is_active']
    list_editable = ['ordering', 'is_active']
