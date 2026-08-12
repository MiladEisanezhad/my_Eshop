from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.HomeView.as_view(), name='home'),

    # Shop / Products
    path('shop/', views.ShopView.as_view(), name='shop'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),

    # Cart
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/<int:product_id>/', views.CartAddView.as_view(), name='cart_add'),
    path('cart/remove/<str:key>/', views.CartRemoveView.as_view(), name='cart_remove'),
    path('cart/update/<str:key>/', views.CartUpdateView.as_view(), name='cart_update'),

    # Checkout
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('checkout/coupon/', views.ApplyCouponView.as_view(), name='apply_coupon'),
    path(
        'order/<str:order_number>/confirmation/',
        views.OrderConfirmationView.as_view(),
        name='order_confirmation'
    ),

    # Auth
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # Account
    path('account/', views.AccountView.as_view(), name='account'),

    # Wishlist
    path('wishlist/', views.WishlistView.as_view(), name='wishlist'),
    path(
        'wishlist/toggle/<int:product_id>/',
        views.WishlistToggleView.as_view(),
        name='wishlist_toggle'
    ),

    # Newsletter
    path(
        'newsletter/subscribe/',
        views.NewsletterSubscribeView.as_view(),
        name='newsletter_subscribe'
    ),

    # Search
    path(
        'search/suggestions/',
        views.SearchSuggestionsView.as_view(),
        name='search_suggestions'
    ),
]