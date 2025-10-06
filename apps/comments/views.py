from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.template.loader import render_to_string
from .models import Comment
from .forms import CommentForm
from apps.posts.models import Post


class AddCommentView(LoginRequiredMixin, CreateView):
    """
    Create a new comment for a post. Supports AJAX (returns rendered html snippet).
    URL: /comments/add/<post_pk>/
    """
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

        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            html = render_to_string("apps/comments/_comment.html", {"comment": comment, "user": self.request.user}, request=self.request)
            return JsonResponse({"status": "ok", "html": html, "comment_id": comment.pk})

        return redirect(self.post_obj.get_absolute_url() if hasattr(self.post_obj, "get_absolute_url") else reverse_lazy("posts:detail", args=[self.post_obj.pk]))

    def form_invalid(self, form):
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"status": "error", "errors": form.errors}, status=400)
        return HttpResponseBadRequest("Invalid data")


class EditCommentView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Edit comment. Only author or staff can edit.
    Supports AJAX (returns updated rendered comment html).
    URL: /comments/edit/<pk>/
    """
    model = Comment
    form_class = CommentForm
    template_name = "apps/comments/comment_form.html"

    def test_func(self):
        obj = self.get_object()
        return self.request.user == obj.user or self.request.user.is_staff

    def form_valid(self, form):
        comment = form.save()
        comment.mark_edited()

        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            html = render_to_string("apps/comments/_comment.html", {"comment": comment, "user": self.request.user}, request=self.request)
            return JsonResponse({"status": "ok", "html": html, "comment_id": comment.pk})

        return redirect(comment.post.get_absolute_url() if hasattr(comment.post, "get_absolute_url") else reverse_lazy("posts:detail", args=[comment.post.pk]))


class DeleteCommentView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Soft-delete (deactivate) the comment by setting is_active to False.
    Only author or staff can delete.
    URL: /comments/delete/<pk>/
    """
    model = Comment

    def test_func(self):
        obj = self.get_object()
        return self.request.user == obj.user or self.request.user.is_staff

    def post(self, request, *args, **kwargs):
        comment = self.get_object()
        comment.is_active = False
        comment.save(update_fields=["is_active"])

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"status": "ok", "comment_id": comment.pk})

        return redirect(comment.post.get_absolute_url() if hasattr(comment.post, "get_absolute_url") else reverse_lazy("posts:detail", args=[comment.post.pk]))
