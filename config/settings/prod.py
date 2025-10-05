"""Production settings with secure defaults, PostgreSQL, S3 storage, and enhanced security."""
from .base import *
import os

"""Disable debug mode for production."""
DEBUG = False

"""Allowed hosts configuration from environment variable."""
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",") if os.getenv("ALLOWED_HOSTS") else []

"""Database configuration using DATABASE_URL or individual environment variables."""
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    try:
        import dj_database_url
        DATABASES = {"default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)}
    except Exception:
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": os.getenv("POSTGRES_DB", "chatty"),
                "USER": os.getenv("POSTGRES_USER", "chatty"),
                "PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
                "HOST": os.getenv("DB_HOST", "db"),
                "PORT": os.getenv("DB_PORT", "5432"),
            }
        }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "chatty"),
            "USER": os.getenv("POSTGRES_USER", "chatty"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
            "HOST": os.getenv("DB_HOST", "db"),
            "PORT": os.getenv("DB_PORT", "5432"),
        }
    }

"""Security settings for production environment."""
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "1") == "1"
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "3600"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv("SECURE_HSTS_INCLUDE_SUBDOMAINS", "1") == "1"
SECURE_HSTS_PRELOAD = os.getenv("SECURE_HSTS_PRELOAD", "0") == "1"

"""File storage configuration (S3/MinIO or local filesystem)."""
USE_S3 = os.getenv("USE_S3", "0") == "1"
if USE_S3:
    AWS_ACCESS_KEY_ID = os.getenv("MINIO_ACCESS_KEY")
    AWS_SECRET_ACCESS_KEY = os.getenv("MINIO_SECRET_KEY")
    AWS_S3_ENDPOINT_URL = os.getenv("MINIO_ENDPOINT")
    AWS_STORAGE_BUCKET_NAME = os.getenv("MINIO_BUCKET", "chatty-media")
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
else:
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

"""Email backend configuration for production."""
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")

"""Logging level configuration."""
LOGGING["root"]["level"] = os.getenv("LOG_LEVEL", "INFO")

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
