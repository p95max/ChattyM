from .base import *
import os

"""Development settings for local environment."""

DEBUG = True

_raw_hosts = os.environ.get('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [h.strip() for h in _raw_hosts.split(',') if h.strip()]
if not ALLOWED_HOSTS and DEBUG:
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

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

EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")

# dev-only
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

INTERNAL_IPS = ["127.0.0.1", "localhost", "172.17.0.1"]

DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

if os.getenv("ENABLE_DEBUG_TOOLBAR", "0") == "1":
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE
