from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import F
from .models import Like
from apps.posts.models import Post


@receiver(post_save, sender=Like)
def inc_post_likes_count(sender, instance, created, **kwargs):
    if created:
        Post.objects.filter(pk=instance.post_id).update(likes_count=F("likes_count") + 1)

    try:
        from apps.notifications.services import create_notification
        post = Post.objects.filter(pk=instance.post_id).select_related('user').first()
        if post and post.user_id != instance.user_id:
            create_notification(
                recipient=post.user,
                actor=instance.user,
                verb="liked your post",
                target=post,
                data={"post_id": post.pk, "post_title": post.title}
            )
    except Exception:
        pass


@receiver(post_delete, sender=Like)
def dec_post_likes_count(sender, instance, **kwargs):
    Post.objects.filter(pk=instance.post_id).update(likes_count=F("likes_count") - 1)
