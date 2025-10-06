from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from apps.posts.models import Post
from .models import Like


@method_decorator(login_required, name="dispatch")
class ToggleLikeView(View):

    def post(self, request, pk, *args, **kwargs):
        post = get_object_or_404(Post, pk=pk, is_active=True)

        try:
            like, created = Like.objects.get_or_create(user=request.user, post=post)
        except IntegrityError:
            try:
                Like.objects.filter(user=request.user, post=post).delete()
                action = "unliked"
            except Exception:
                return HttpResponseBadRequest("DB error")
        else:
            if created:
                action = "liked"
            else:
                like.delete()
                action = "unliked"

        post.refresh_from_db(fields=["likes_count"])

        if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.content_type == "application/json":
            return JsonResponse({"status": "ok", "action": action, "likes_count": post.likes_count})

        return redirect(request.META.get("HTTP_REFERER", "posts:list"))
