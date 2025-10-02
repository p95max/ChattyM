"""Serializers for User model (Django REST Framework)."""
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    """Basic serializer for User."""
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "bio", "avatar")
        read_only_fields = ("id",)