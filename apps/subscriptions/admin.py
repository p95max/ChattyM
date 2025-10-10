from django.contrib import admin
from apps.subscriptions.models import Subscription

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "follower", "following", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("follower__username", "following__username", "follower__email", "following__email", )
    ordering = ("created_at",)