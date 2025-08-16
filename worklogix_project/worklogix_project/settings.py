"""
Django settings for worklogix_project.

Notes:
- Designed to run locally and on Render.
- Uses dj-database-url to read DATABASE_URL in production, falls back to SQLite locally.
- WhiteNoise serves static assets in production (no extra service needed).
"""

from pathlib import Path
import os

from dotenv import load_dotenv
import dj_database_url
import certifi

# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# -------------------------------------------------------------------
# Core flags & hosts
# -------------------------------------------------------------------
SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "work-logix-v2.onrender.com"]
CSRF_TRUSTED_ORIGINS = ["https://work-logix-v2.onrender.com"]

# -------------------------------------------------------------------
# Applications
# -------------------------------------------------------------------
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third‑party
    "crispy_forms",
    "crispy_bootstrap5",

    # Local apps
    "core",
]

AUTH_USER_MODEL = "core.CustomUser"
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# -------------------------------------------------------------------
# Middleware
# WhiteNoise must be just after SecurityMiddleware.
# -------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # << move up here
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# -------------------------------------------------------------------
# Templates
# -------------------------------------------------------------------
ROOT_URLCONF = "worklogix_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # project-level templates
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "worklogix_project.wsgi.application"

# -------------------------------------------------------------------
# Database
# - Uses DATABASE_URL if set (Render sets this automatically)
# - Falls back to SQLite for local dev
# -------------------------------------------------------------------

# Use SQLite locally by default; Render will inject DATABASE_URL
default_sqlite_url = f"sqlite:///{BASE_DIR / 'db.sqlite3'}"

DATABASES = {
    "default": dj_database_url.config(
        default=default_sqlite_url,
        conn_max_age=600,
        ssl_require=False, 
    )
}



# -------------------------------------------------------------------
# Password validation
# -------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -------------------------------------------------------------------
# I18N / TZ
# -------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# -------------------------------------------------------------------
# Static & Media
# - WhiteNoise serves STATIC_ROOT
# - MEDIA_ROOT points to a persistent disk path on Render (via env)
# -------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# If you keep project static assets in core/static, include it here.
STATICFILES_DIRS = [BASE_DIR / "core" / "static"]

STORAGES = {
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
}

MEDIA_URL = "/media/"
MEDIA_ROOT = os.getenv("MEDIA_ROOT", BASE_DIR / "media")

# -------------------------------------------------------------------
# Security hardening in production
# Render terminates SSL; this header lets Django know the original scheme
# -------------------------------------------------------------------
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "Lax"  # safe default

# -------------------------------------------------------------------
# Auth redirects
# -------------------------------------------------------------------
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/redirect-after-login/"
LOGOUT_REDIRECT_URL = "/login/"

# -------------------------------------------------------------------
# Third‑party / misc
# -------------------------------------------------------------------
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")  # keep keys out of source
DATA_UPLOAD_MAX_NUMBER_FIELDS = 50000

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
