from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "likes_count", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("title", "text", "user__email", "user__username")
    autocomplete_fields = ("user",)
    ordering = ("-created_at",)
