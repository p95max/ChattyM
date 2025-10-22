from django.conf import settings
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = settings.AUTH_USER_MODEL

class Notification(models.Model):
    """
    Simple notification model for site events.
    recipient: who receives the notification
    actor: optional user who triggered the event
    verb: short human-friendly action, e.g. "liked your post"
    unread: True by default
    optional generic target (post/comment/conversation/message) and extra JSON data
    """
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    actor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="actor_notifications")
    verb = models.CharField(max_length=200)
    unread = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    target_ct = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.CASCADE)
    target_id = models.CharField(max_length=255, null=True, blank=True)
    target = GenericForeignKey('target_ct', 'target_id')

    data = models.JSONField(null=True, blank=True, default=dict)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["recipient", "unread"]),
            models.Index(fields=["created_at"]),
        ]

    def mark_read(self):
        if self.unread:
            self.unread = False
            self.save(update_fields=["unread"])
