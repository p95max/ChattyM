from django.views.generic import TemplateView
from apps.posts.models import Post

class MainView(TemplateView):
    template_name = "main.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["latest_posts"] = (
            Post.objects.filter(is_active=True)
            .select_related("user")
            .order_by("-created_at")[:6]
        )
        return ctx
