from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.posts.models import Post

User = get_user_model()

class Comment(models.Model):
    """
    Comment placed by a user under a Post.
    Supports replies through parent FK and simple moderation via is_active.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies"
    )
    content = models.TextField(max_length=2000)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("created_at",)
        indexes = [
            models.Index(fields=["post", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"Comment #{self.pk} by {self.user}"

    def mark_edited(self) -> None:
        self.updated_at = timezone.now()
        self.save(update_fields=["updated_at"])
