"""Base settings for Django project shared across environments."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

"""Secret key for Django project, should be overridden in production."""
SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-default-secret-for-dev")

"""Installed Django apps and third-party packages."""
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.sites",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    'widget_tweaks',
    'crispy_bootstrap5',
    "allauth",
    "allauth.account",
    "allauth.socialaccount",

    "apps.core",
    "apps.users",
    "apps.posts",
    "apps.comments",
    "apps.likes",
    "apps.subscriptions",
]

"""Middleware stack for request processing."""
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

"""Template configuration for Django Templates."""
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

"""Custom user model for authentication."""
AUTH_USER_MODEL = "users.User"

"""Internationalization settings."""
LANGUAGE_CODE = "en-us"
LANGUAGES = [
    ("en", "English"),
    ("de", "Deutsch"),
]
TIME_ZONE = os.getenv("TIME_ZONE", "UTC")
USE_I18N = True
USE_L10N = True
USE_TZ = True

"""Static files (CSS, JavaScript, Images) configuration."""
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

"""Media files (user uploads) configuration."""
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

"""Default database configuration (overridden in dev/prod)."""
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

"""Django REST Framework base configuration."""
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

"""Email backend configuration (console by default)."""
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

"""Security settings (can be overridden in production)."""
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

"""Logging configuration."""
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": os.getenv("LOG_LEVEL", "INFO")},
}

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

SITE_ID = 1

ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = "username"
ACCOUNT_UNIQUE_EMAIL = True
LOGIN_REDIRECT_URL = "/"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "webmaster@localhost"

ACCOUNT_FORMS = {
    'login': 'apps.users.forms.CustomLoginForm',
    'signup': 'apps.users.forms.CustomSignupForm',
}

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"



