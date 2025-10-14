from django.contrib import admin
from .models import Conversation, Participant, Message

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_at")
    search_fields = ("title",)

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "user", "is_active", "last_read")

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "sender", "created_at", "is_deleted")
    list_filter = ("is_deleted",)
    search_fields = ("content", "sender__email", "sender__username")
