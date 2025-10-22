from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.template.loader import render_to_string
from utils.posts_utils import AuthorRequiredMixin
from .models import Comment
from .forms import CommentForm
from apps.posts.models import Post
from django.utils import timezone
from django.urls import reverse



class AddCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(Post, pk=kwargs.get("post_pk"), is_active=True)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.user = self.request.user
        comment.post = self.post_obj
        comment.save()

        # --- notify post author ---
        try:
            from apps.notifications.services import create_notification
            post_author = getattr(comment.post, "user", None)
            if post_author and post_author != comment.user:
                post_url = None
                try:
                    if hasattr(comment.post, "get_absolute_url"):
                        post_url = comment.post.get_absolute_url()
                except Exception:
                    post_url = None
                if not post_url:
                    try:
                        post_url = reverse("posts:detail", args=[comment.post.pk])
                    except Exception:
                        post_url = None

                create_notification(
                    recipient=post_author,
                    actor=comment.user,
                    verb="commented on your post",
                    target=comment.post,
                    data={"post_id": comment.post.pk, "comment_id": comment.pk, "url": post_url},
                )
        except Exception:
            pass


        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            html = render_to_string("apps/comments/_comment.html",
                                    {"comment": comment, "user": self.request.user},
                                    request=self.request)
            return JsonResponse({"status": "ok", "html": html, "comment_id": comment.pk})
        return redirect(self.post_obj.get_absolute_url() if hasattr(self.post_obj, "get_absolute_url")
                        else reverse_lazy("posts:detail", args=[self.post_obj.pk]))

    def form_invalid(self, form):
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"status": "error", "errors": form.errors}, status=400)
        return HttpResponseBadRequest("Invalid data")


class EditCommentView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = "apps/comments/comment_form.html"

    def form_valid(self, form):
        comment = form.save(commit=False)

        if not (self.request.user == comment.user or self.request.user.is_staff):
            return self.handle_no_permission()

        comment.edited_at = timezone.now()
        comment.edited_by = self.request.user

        comment.save(update_fields=['content', 'edited_at', 'edited_by', 'updated_at'])

        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            html = render_to_string("apps/comments/_comment.html",
                                    {"comment": comment, "user": self.request.user},
                                    request=self.request)
            return JsonResponse({"status": "ok", "html": html, "comment_id": comment.pk})

        return redirect(comment.post.get_absolute_url() if hasattr(comment.post, "get_absolute_url") else reverse_lazy("posts:detail", args=[comment.post.pk]))


class DeleteCommentView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment

    def test_func(self):
        obj = self.get_object()
        return (self.request.user == obj.user) or self.request.user.is_staff

    def handle_no_permission(self):
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"status": "error", "detail": "forbidden"}, status=403)
        return HttpResponseForbidden("You don't have permission to delete this comment.")

    def post(self, request, *args, **kwargs):
        comment = self.get_object()
        if not ((request.user == comment.user) or request.user.is_staff):
            return self.handle_no_permission()
        comment.is_active = False
        comment.save(update_fields=["is_active"])
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"status": "ok", "comment_id": comment.pk})
        return redirect(comment.post.get_absolute_url() if hasattr(comment.post, "get_absolute_url")
                        else reverse_lazy("posts:detail", args=[comment.post.pk]))
