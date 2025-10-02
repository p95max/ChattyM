"""App config for the users application."""
from django.apps import AppConfig

class UsersConfig(AppConfig):
    """Configuration for the users app."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"