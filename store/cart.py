from decimal import Decimal
from django.conf import settings
from .models import Product, ProductVariant

CART_SESSION_KEY = 'cart'


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if not cart:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart = cart

    def _save(self):
        self.session.modified = True

    def add(self, product, quantity=1, variant_id=None, override_quantity=False):
        key = f'{product.id}_{variant_id or ""}'
        if key not in self.cart:
            variant = None
            price = str(product.price)
            variant_info = ''
            if variant_id:
                try:
                    variant = ProductVariant.objects.get(id=variant_id, product=product)
                    price = str(variant.final_price)
                    parts = []
                    if variant.size:
                        parts.append(variant.size)
                    if variant.color:
                        parts.append(variant.color)
                    variant_info = ' / '.join(parts)
                except ProductVariant.DoesNotExist:
                    pass
            self.cart[key] = {
                'product_id': product.id,
                'variant_id': variant_id,
                'variant_info': variant_info,
                'quantity': 0,
                'price': price,
                'name': product.name,
                'image': product.get_main_image_url(),
                'slug': product.slug,
            }
        if override_quantity:
            self.cart[key]['quantity'] = quantity
        else:
            self.cart[key]['quantity'] += quantity
        self._save()

    def remove(self, key):
        if key in self.cart:
            del self.cart[key]
            self._save()

    def update_quantity(self, key, quantity):
        if key in self.cart:
            if quantity <= 0:
                self.remove(key)
            else:
                self.cart[key]['quantity'] = quantity
                self._save()

    def clear(self):
        del self.session[CART_SESSION_KEY]
        self.session.modified = True

    def __iter__(self):
        product_ids = [v['product_id'] for v in self.cart.values()]
        products = Product.objects.filter(id__in=product_ids)
        product_map = {p.id: p for p in products}
        cart = dict(self.cart)
        for key, item in cart.items():
            item = dict(item)
            item['key'] = key
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            product = product_map.get(item['product_id'])
            item['product'] = product
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )

    def get_items_list(self):
        """Return list of cart items for templates."""
        return list(self.__iter__())
