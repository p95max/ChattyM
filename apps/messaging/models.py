from django.conf import settings
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL

class Conversation(models.Model):
    """
    Simple conversation container. Can be used for 1:1 DM or group chats.
    For a 1:1 chat we create exactly one Conversation with two Participants.
    """
    title = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Conversation {self.pk} ({self.title or 'dm'})"

    def last_message(self):
        return self.messages.order_by("-created_at").first()

    def unread_count_for(self, user):
        """
        Count messages with created_at > participant.last_read for given user.
        If no participant found - return 0.
        """
        try:
            p = self.participants.get(user=user)
        except Participant.DoesNotExist:
            return 0
        if p.last_read:
            return self.messages.filter(created_at__gt=p.last_read).exclude(sender=p.user).count()
        return self.messages.exclude(sender=p.user).count()


class Participant(models.Model):
    """
    Through model connecting users to a Conversation.
    last_read used to compute unread counts efficiently.
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="participants")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conversations")
    last_read = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)  # soft leave
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("conversation", "user")
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["conversation", "user"]),
        ]

    def __str__(self):
        return f"{self.user} in {self.conversation.pk}"


class Message(models.Model):
    """
    Single message in a conversation.
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    content = models.TextField(max_length=4000)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ("created_at",)
        indexes = [
            models.Index(fields=["conversation", "created_at"]),
            models.Index(fields=["sender", "created_at"]),
        ]

    @property
    def text(self):
        for name in ("content", "body", "text", "message", "message_text"):
            if hasattr(self, name):
                val = getattr(self, name)
                if val:
                    return val
        return ""

    def __str__(self):
        return f"Message {self.pk} by {self.sender}"

    def mark_deleted(self):
        self.is_deleted = True
        self.save(update_fields=["is_deleted"])
