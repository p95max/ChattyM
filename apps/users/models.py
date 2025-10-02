"""Custom User model (extends Django's AbstractUser)."""
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Application's custom user model.

    Extends AbstractUser so username/email/auth work as usual.
    Add extra fields here as needed.
    """
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    birthday = models.DateField(null=True, blank=True)
    avatar = models.ImageField("avatar", upload_to="avatars/", null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.get_username()