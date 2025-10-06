from django.core.management.base import BaseCommand
from apps.posts.models import Post

class Command(BaseCommand):
    help = "Recount likes_count for posts based on Like rows."

    def handle(self, *args, **options):
        from apps.likes.models import Like
        for p in Post.objects.all():
            cnt = Like.objects.filter(post=p).count()
            p.likes_count = cnt
            p.save(update_fields=['likes_count'])
            self.stdout.write(f"Post {p.pk}: {cnt}")
