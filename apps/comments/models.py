from django.conf import settings
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

    edited_at = models.DateTimeField(null=True, blank=True, help_text="When the comment was last edited.")
    edited_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                  related_name='edited_comments', help_text="User who last edited this comment.")

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return f"Comment #{self.pk} by {self.user}"

    def mark_edited(self, editor):
        """
        Mark this comment as edited by `editor`.

        Save timestamp and set `edited_by`. Call this after making changes
        in views that perform edits. `editor` may be the original author
        or a staff/moderator.
        """
        self.edited_at = timezone.now()
        self.edited_by = editor