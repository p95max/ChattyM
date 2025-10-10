from django.conf import settings
from django.db import models
from django.utils import timezone


class Subscription(models.Model):
    """
    Represents that `follower` follows `following`.
    Unique per (follower, following). is_active allows soft-unsubscribe.
    """
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions_following"
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions_followers"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("follower", "following")
        indexes = [
            models.Index(fields=["follower"]),
            models.Index(fields=["following"]),
        ]

    def __str__(self):
        return f"{self.follower} → {self.following}"
