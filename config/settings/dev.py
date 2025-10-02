from .base import *
import os

"""Development settings for local environment."""
DEBUG = True

_raw_hosts = os.environ.get('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [h.strip() for h in _raw_hosts.split(',') if h.strip()]
if not ALLOWED_HOSTS and DEBUG:
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

"""Database configuration using PostgreSQL with environment variables."""
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "chatty"),
        "USER": os.getenv("POSTGRES_USER", "chatty"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "chattypassword"),
        "HOST": os.getenv("DB_HOST", "db"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

"""Email backend for development (console output)."""
EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)

"""File storage backend for development (local filesystem)."""
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

INTERNAL_IPS = ["127.0.0.1"]

"""Enable Django Debug Toolbar if environment variable is set."""
if os.getenv("ENABLE_DEBUG_TOOLBAR", "0") == "1":
    INSTALLED_APPS += ["debug_toolbar"]  # noqa: PLW2901
    MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE