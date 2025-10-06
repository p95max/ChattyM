from django.db import models
from django.conf import settings
from apps.posts.models import Post


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("user", "post"),)
        ordering = ("-created_at",)

    def __str__(self):
        return f"Like(user={self.user_id}, post={self.post_id})"
