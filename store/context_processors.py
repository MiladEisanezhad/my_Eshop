from .models import Category, UserProfile
from .cart import Cart


def cart_context(request):
    cart = Cart(request)
    return {
        'cart': cart,
        'cart_count': len(cart),
        'cart_total': cart.get_total_price(),
    }


def categories_context(request):
    top_level = Category.objects.filter(is_active=True, parent=None).prefetch_related('children')
    men_cats = Category.objects.filter(is_active=True, gender='men')
    women_cats = Category.objects.filter(is_active=True, gender='women')
    return {
        'nav_categories': top_level,
        'men_categories': men_cats,
        'women_categories': women_cats,
    }


def profile_context(request):
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            profile = None
    else:
        profile = None
    return {'profile': profile}