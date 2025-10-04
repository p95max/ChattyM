from django.db.models.signals import post_save, post_delete
from django.db.models import F
from django.dispatch import receiver
from .models import Like

@receiver(post_save, sender=Like)
def inc_like(sender, instance, created, **kwargs):
    if created:
        instance.post.likes_count = F('likes_count') + 1
        instance.post.save(update_fields=['likes_count'])

@receiver(post_delete, sender=Like)
def dec_like(sender, instance, **kwargs):
    instance.post.likes_count = F('likes_count') - 1
    instance.post.save(update_fields=['likes_count'])
