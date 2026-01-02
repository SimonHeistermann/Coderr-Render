from pathlib import Path
import os

import dj_database_url
from corsheaders.defaults import default_headers, default_methods
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------------------------------------------------------
# Core config
# -----------------------------------------------------------------------------
SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = os.environ.get("DEBUG", "False") == "True"

ALLOWED_HOSTS = [h.strip() for h in os.environ.get("ALLOWED_HOSTS", "").split(",") if h.strip()]

# If you deploy under a subpath like /coderr, set in .env:
# FORCE_SCRIPT_NAME=/coderr
FORCE_SCRIPT_NAME = os.environ.get("FORCE_SCRIPT_NAME", "") or None

# -----------------------------------------------------------------------------
# Static / Media
# -----------------------------------------------------------------------------
STATIC_URL = os.environ.get("STATIC_URL", "static/")
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = os.environ.get("MEDIA_URL", "/media/")
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# -----------------------------------------------------------------------------
# Database
# -----------------------------------------------------------------------------
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

# -----------------------------------------------------------------------------
# Applications
# -----------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "django_filters",
    "core",
    "sales_app",
    "user_auth_app",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# -----------------------------------------------------------------------------
# CORS / CSRF
# -----------------------------------------------------------------------------
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://192.168.1.45:5500",
    "http://localhost:5501",
    "http://127.0.0.1:5501",
    "http://192.168.1.45:5501",
    "https://coderr.projects.simon-heistermann.de",
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://192.168.1.45:5500",
    "http://localhost:5501",
    "http://127.0.0.1:5501",
    "http://192.168.1.45:5501",
    "https://coderr.projects.simon-heistermann.de",
]

CORS_ALLOW_HEADERS = list(default_headers) + [
    "authorization",
    "content-type",
]

CORS_ALLOW_METHODS = list(default_methods) + [
    "PATCH",
]

CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "core.wsgi.application"

# -----------------------------------------------------------------------------
# Auth / Password validation
# -----------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -----------------------------------------------------------------------------
# Internationalization
# -----------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -----------------------------------------------------------------------------
# Django REST framework
# -----------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%SZ",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/day",
        "user": "1000/day",
        "login": "5/min",
        "registration": "3/min",
        "order_create": "20/hour",
    },
}