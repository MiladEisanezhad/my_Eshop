import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = os.environ.get("DEBUG", "False") == "True"

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "storages",
    "store",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

CSRF_TRUSTED_ORIGINS = [
    origin for origin in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") 
    if origin
]

ROOT_URLCONF = "tailstore.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "store" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "store.context_processors.cart_context",
                "store.context_processors.categories_context",
                "store.context_processors.profile_context",
            ],
        },
    },
]

WSGI_APPLICATION = "tailstore.wsgi.application"

# ─── PostgreSQL Database ───────────────────────────────────────────────────────
DATABASES = {
    "default": dj_database_url.config(
        default=os.environ.get("DATABASE_URL"),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# ─── Auth ─────────────────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# ─── Static & Media ───────────────────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

if DEBUG:
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"
else:
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

    AWS_ACCESS_KEY_ID = os.environ.get("SUPABASE_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("SUPABASE_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.environ.get("SUPABASE_BUCKET_NAME")
    AWS_S3_ENDPOINT_URL = os.environ.get("SUPABASE_ENDPOINT_URL")
    AWS_S3_REGION_NAME = os.environ.get("SUPABASE_REGION")

    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = "public-read"
    AWS_S3_SIGNATURE_VERSION = "s3v4"

    MEDIA_URL = f"{os.environ.get('SUPABASE_PROJECT_URL', '')}/storage/v1/object/public/media/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {
        'handlers': ['console'],
        'level': 'ERROR',
    },
}