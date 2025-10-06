from django.contrib import admin
from .models import Comment

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'post', 'user', 'is_active', 'created_at', 'edited_at', 'edited_by')
    readonly_fields = ('created_at', 'updated_at', 'edited_at')
