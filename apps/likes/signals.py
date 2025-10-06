from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import F
from .models import Like
from apps.posts.models import Post


@receiver(post_save, sender=Like)
def inc_post_likes_count(sender, instance, created, **kwargs):
    if created:
        Post.objects.filter(pk=instance.post_id).update(likes_count=F("likes_count") + 1)


@receiver(post_delete, sender=Like)
def dec_post_likes_count(sender, instance, **kwargs):
    Post.objects.filter(pk=instance.post_id).update(likes_count=F("likes_count") - 1)
