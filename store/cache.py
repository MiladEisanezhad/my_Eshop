from django.core.cache import cache

# ── Serialization ────────────────────────────────────────────────────

# Converts Product model instances into plain dicts (cache-safe, no pickle
# fragility, no risk of breaking after a model change).

def serialize_products(products):
    """
    products: an iterable of Product instances (already fetched with
    select_related/prefetch_related for category + images).!
    Returns: a list of plain dicts — safe to store in Redis.
    """
    result = []
    for p in products:
        result.append(
            {
                "id": p.id,
                "name": p.name,
                "slug": p.slug,
                "price": str(p.price),
                "compare_price": str(p.compare_price) if p.compare_price else None,
                "discount_percent": p.discount_percent,
                "is_on_sale": p.is_on_sale,
                "is_new_arrival": p.is_new_arrival,
                "rating_avg": str(p.rating_avg),
                "rating_count": p.rating_count,
                "category_name": p.category.name if p.category_id else "",
                "image_url": p.get_main_image_url(),
                "absolute_url": p.get_absolute_url(),
            }
        )
    return result

# ── Cache orchestration (cache-aside pattern) ────────────────────────

# ONE generic function, reused for featured/new_arrivals/on_sale/etc.
# What varies per call: cache_key, the queryset, and the timeout.

def get_cached_products(cache_key, queryset, timeout=3600):
    """
    cache_key: unique string identifying this specific list, e.g. "home:featured"
    queryset: a Product queryset, NOT yet evaluated (so it only runs on cache miss)
    timeout: seconds before this cache entry expires (default 1 hour)

    Returns: a list of plain dicts (from serialize_products), either from
    cache or freshly queried + stored.
    """
    data = cache.get(cache_key)  # Step 1: check Redis first

    if data is None:  # Step 2: cache miss — nothing there, or it expired
        data = serialize_products(queryset)  # evaluate the queryset NOW, turn into dicts
        cache.set(cache_key, data, timeout=timeout)  # Step 3: store for next time

    return data  # Step 4: return either the cached or freshly-built data