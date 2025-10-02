"""Admin registration for custom User model."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Admin for User model, extends default UserAdmin."""
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Additional", {"fields": ("birthday", "avatar", "created_at")}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ("Additional", {"fields": ("birthday", "avatar")}),
    )
    readonly_fields = ("created_at",)