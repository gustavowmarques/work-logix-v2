"""
Django settings for worklogix_project

- Local dev (default): Read discrete Postgres vars from .env
  SECRET_KEY, DEBUG, DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT
- Production (Render): Use DATABASE_URL and require SSL automatically
  (set env on Render; no code changes needed)

Tip: never commit .env or SECRET_KEY.
"""

from pathlib import Path
import os

from dotenv import load_dotenv
import dj_database_url

# ---------------------------------------------------------------------
# Paths & .env
# ---------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
# Load variables from .env sitting at project root (BASE_DIR/.env)
load_dotenv(BASE_DIR / ".env")

# ---------------------------------------------------------------------
# Core flags
# ---------------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-for-dev-only")
DEBUG = os.getenv("DEBUG", "False").strip().lower() == "true"

# Hosts you allow the app to serve. On Render set:
# ALLOWED_HOSTS=work-logix-v2.onrender.com
_default_hosts = ["127.0.0.1", "localhost"] if DEBUG else []
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", ",".join(_default_hosts)).split(",") if h.strip()]

# CSRF trusted origins: on Render set, e.g.:
# CSRF_TRUSTED_ORIGINS=https://work-logix-v2.onrender.com,https://*.onrender.com
_default_csrf = ["http://127.0.0.1:8000", "http://localhost:8000"] if DEBUG else []
CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.getenv("CSRF_TRUSTED_ORIGINS", ",".join(_default_csrf)).split(",") if o.strip()]

# ---------------------------------------------------------------------
# Apps
# ---------------------------------------------------------------------
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "crispy_forms",
    "crispy_bootstrap5",

    # Local
    "core",
]

AUTH_USER_MODEL = "core.CustomUser"

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ---------------------------------------------------------------------
# Middleware
#   WhiteNoise must come right after SecurityMiddleware
# ---------------------------------------------------------------------
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

# ---------------------------------------------------------------------
# URLs / Templates / WSGI
# ---------------------------------------------------------------------
ROOT_URLCONF = "worklogix_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

# ---------------------------------------------------------------------
# Database
#
# Priority:
#   1) DATABASE_URL present  -> use it (Render/production) with SSL required
#   2) Discrete .env values  -> local Postgres
#   3) Fallback              -> SQLite (only if neither of the above is set)
#
# This avoids passing SSL params to SQLite (which caused errors earlier).
# ---------------------------------------------------------------------
DATABASES = {}

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

if DATABASE_URL:
    # Allow toggling SSL when using Render's internal URL
    ssl_required = os.getenv("DB_SSL_REQUIRED", "false").lower() == "true"
    DATABASES["default"] = dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        ssl_require=ssl_required,
    )
else:
    # Local Postgres via discrete .env values
    name = os.getenv("DATABASE_NAME", "").strip()
    host = os.getenv("DATABASE_HOST", "").strip()

    if name and host:
        DATABASES["default"] = {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": name,
            "USER": os.getenv("DATABASE_USER", "postgres"),
            "PASSWORD": os.getenv("DATABASE_PASSWORD", ""),
            "HOST": host,                  # e.g., "localhost"
            "PORT": os.getenv("DATABASE_PORT", "5432"),
            "CONN_MAX_AGE": 600,
        }
    else:
        # Safety fallback for quick local tinkering only
        DATABASES["default"] = {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
# ---------------------------------------------------------------------
# Password validation (kept default)
# ---------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------
# Static & media files
#   WhiteNoise serves static files on Render (no extra service needed)
# ---------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"  # collectstatic target
# Your app’s extra static dir(s); keep in sync with your project layout
STATICFILES_DIRS = [BASE_DIR / "core" / "static"]

# Django 5 storage API
STORAGES = {
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
}

MEDIA_URL = "/media/"
MEDIA_ROOT = os.getenv("MEDIA_ROOT", str(BASE_DIR / "media"))

# ---------------------------------------------------------------------
# Security (production)
# ---------------------------------------------------------------------
if not DEBUG:
    # Required behind Render’s proxy
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # Reasonable default; adjust if you embed cross-site
    SESSION_COOKIE_SAMESITE = "Lax"

# ---------------------------------------------------------------------
# Auth redirects
# NOTE: If you see a login redirect loop, confirm that the view at
# '/redirect-after-login/' is reachable to authenticated users and
# does NOT bounce back to LOGIN_URL.
# ---------------------------------------------------------------------
LOGIN_URL = "login" 
LOGIN_REDIRECT_URL = "redirect_after_login"
LOGOUT_REDIRECT_URL = "login"

# ---------------------------------------------------------------------
# Project-specific
# ---------------------------------------------------------------------
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
DATA_UPLOAD_MAX_NUMBER_FIELDS = 50_000
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
