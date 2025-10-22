from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id","recipient","actor","verb","unread","created_at")
    list_filter = ("unread","created_at")
    search_fields = ("recipient__email","actor__email","verb")
