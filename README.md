# TailStore — Django E-Commerce

A full Django e-commerce site with PostgreSQL backend, built on the TailStore frontend template.

---

## 🚀 Quick Setup

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Create PostgreSQL database

```sql
-- Run in psql
CREATE DATABASE tailstore;
CREATE USER tailstore_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE tailstore TO tailstore_user;
```

### 3. Configure environment (optional)

Set these environment variables, or edit `tailstore/settings.py` directly:

```bash
export DB_NAME=tailstore
export DB_USER=tailstore_user
export DB_PASSWORD=yourpassword
export DB_HOST=localhost
export DB_PORT=5432
```

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Create a superuser (for admin panel)

```bash
python manage.py createsuperuser
```

### 6. Collect static files

```bash
python manage.py collectstatic --noinput
```

### 7. Run the development server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000  
Admin: http://127.0.0.1:8000/admin

---

## 📁 Project Structure

```
tailstore/
├── manage.py
├── requirements.txt
├── tailstore/              # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── store/                  # Main app
│   ├── models.py           # All database models
│   ├── views.py            # All views
│   ├── urls.py             # URL routing
│   ├── admin.py            # Admin panel
│   ├── cart.py             # Session cart logic
│   ├── context_processors.py
│   ├── migrations/
│   ├── templatetags/
│   │   └── store_tags.py
│   └── templates/store/
│       ├── base.html
│       ├── index.html
│       ├── shop.html
│       ├── single_product.html
│       ├── cart.html
│       ├── checkout.html
│       ├── order_confirmation.html
│       ├── register.html
│       ├── login.html
│       ├── account.html
│       ├── wishlist.html
│       ├── 404.html
│       └── partials/
│           └── product_card.html
├── static/
│   └── assets/             # CSS, JS, images from TailStore template
└── media/                  # Uploaded product images
```

---

## 🗄️ Database Models

| Model | Description |
|---|---|
| `Category` | Hierarchical (parent/child), gender filter, active flag |
| `Brand` | Brand with logo and slug |
| `Tag` | Product tags (many-to-many) |
| `Product` | Full product: pricing, stock, SEO, flags (featured/new/sale) |
| `ProductImage` | Multiple gallery images per product |
| `ProductVariant` | Size × Color variants with per-variant stock and price adjustment |
| `Review` | Star ratings with approval workflow |
| `Wishlist` | Per-user saved products |
| `Coupon` | Percentage / fixed / free-shipping discount codes with expiry |
| `Order` | Full order with shipping & billing addresses |
| `OrderItem` | Line items with snapshots of product name/price at purchase time |
| `UserProfile` | Extended user data + default shipping address |
| `NewsletterSubscriber` | Email list |
| `Banner` | Slider and category banner images managed via admin |

---

## ➕ Adding Products

1. Go to **Admin → Store → Categories** and create at least one category
2. Go to **Admin → Store → Products** → click **Add Product**
3. Fill in: Name, Category, Price, Status = **Published**, upload Main Image
4. Optionally add gallery images and size/color variants via the inline sections
5. Check **Is Featured**, **Is New Arrival**, or **Is On Sale** as needed
6. Save — the product immediately appears on the site

---

## 🔧 Key URLs

| URL | Page |
|---|---|
| `/` | Home |
| `/shop/` | Product listing with filters |
| `/product/<slug>/` | Product detail |
| `/cart/` | Shopping cart |
| `/checkout/` | Checkout |
| `/register/` | Register + Login |
| `/account/` | User dashboard |
| `/wishlist/` | Saved products |
| `/admin/` | Django admin |

---

## 🔌 API Endpoints (AJAX/JSON)

| Endpoint | Method | Description |
|---|---|---|
| `/cart/add/<id>/` | POST | Add product to cart |
| `/cart/remove/<key>/` | POST | Remove cart item |
| `/cart/update/<key>/` | POST | Update quantity |
| `/wishlist/toggle/<id>/` | POST | Toggle wishlist |
| `/search/suggestions/?q=` | GET | Live search results |
| `/newsletter/subscribe/` | POST | Subscribe email |
