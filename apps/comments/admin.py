from django.contrib import admin
from .models import Comment

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "post", "is_active", "created_at", "updated_at")
    list_filter = ("is_active", "created_at", "user")
    search_fields = ("content", "user__username", "post__title")
    raw_id_fields = ("user", "post", "parent")
