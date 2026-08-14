import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url
import sys
import logging
from urllib.parse import urlparse

load_dotenv(override=False)

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

if DEBUG:
    # Local development
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"

    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

else:
    # Production (Supabase S3)
    AWS_ACCESS_KEY_ID = os.environ.get("SUPABASE_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("SUPABASE_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.environ.get("SUPABASE_BUCKET_NAME")
    AWS_S3_ENDPOINT_URL = os.environ.get("SUPABASE_ENDPOINT_URL")
    AWS_S3_REGION_NAME = os.environ.get("SUPABASE_REGION")

    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }

    AWS_S3_CUSTOM_DOMAIN = (
        f"{os.environ.get('SUPABASE_PROJECT_REF')}.supabase.co/storage/v1/object/public/"
        f"{AWS_STORAGE_BUCKET_NAME}"
    )

    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"

    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_SIGNATURE_VERSION = "s3v4"
    AWS_S3_ADDRESSING_STYLE = "path"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


FILE_UPLOAD_HANDLERS = [
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# ─── Deployment Diagnostics ──────────────────────────────────────────────────

logger = logging.getLogger("deployment")

logger.warning("========== DEPLOYMENT DIAGNOSTICS START ==========")

logger.warning("DEBUG = %s", DEBUG)
logger.warning("ALLOWED_HOSTS = %s", ALLOWED_HOSTS)
logger.warning("PORT = %s", os.environ.get("PORT"))

# Database ENV
database_url = os.environ.get("DATABASE_URL")

if database_url:
    try:
        parsed_db = urlparse(database_url)

        logger.warning("DATABASE_URL exists = True")
        logger.warning("DATABASE scheme = %s", parsed_db.scheme)
        logger.warning("DATABASE host = %s", parsed_db.hostname)
        logger.warning("DATABASE port = %s", parsed_db.port)
        logger.warning("DATABASE name = %s", parsed_db.path.lstrip("/"))
        logger.warning("DATABASE username = %s", parsed_db.username)

        # Do NOT print the actual password
        logger.warning(
            "DATABASE password exists = %s",
            bool(parsed_db.password),
        )

        logger.warning(
            "DATABASE query = %s",
            parsed_db.query,
        )

    except Exception:
        logger.exception("FAILED TO PARSE DATABASE_URL")

else:
    logger.error("DATABASE_URL exists = False")


# Django database configuration
db_config = DATABASES.get("default", {})

logger.warning(
    "DATABASE ENGINE = %s",
    db_config.get("ENGINE"),
)

logger.warning(
    "DATABASE HOST = %s",
    db_config.get("HOST"),
)

logger.warning(
    "DATABASE PORT = %s",
    db_config.get("PORT"),
)

logger.warning(
    "DATABASE NAME = %s",
    db_config.get("NAME"),
)

logger.warning(
    "DATABASE USER = %s",
    db_config.get("USER"),
)


# Supabase
logger.warning(
    "SUPABASE_ACCESS_KEY_ID exists = %s",
    bool(os.environ.get("SUPABASE_ACCESS_KEY_ID")),
)

logger.warning(
    "SUPABASE_SECRET_ACCESS_KEY exists = %s",
    bool(os.environ.get("SUPABASE_SECRET_ACCESS_KEY")),
)

logger.warning(
    "SUPABASE_BUCKET_NAME = %s",
    os.environ.get("SUPABASE_BUCKET_NAME"),
)

logger.warning(
    "SUPABASE_ENDPOINT_URL = %s",
    os.environ.get("SUPABASE_ENDPOINT_URL"),
)


logger.warning("========== TESTING DATABASE CONNECTION ==========")

try:
    from django.db import connection

    connection.ensure_connection()

    logger.warning("DATABASE CONNECTION = SUCCESS")

except Exception:
    logger.exception("DATABASE CONNECTION = FAILED")


logger.warning("========== DEPLOYMENT DIAGNOSTICS END ==========")