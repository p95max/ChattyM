from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, DetailView
from django.http import Http404
from .models import Post



class PostListView(ListView):
    model = Post
    template_name = "apps/posts/posts_list.html"
    context_object_name = "posts"
    paginate_by = 9

    def get_queryset(self):
        return (
            Post.objects.filter(is_active=True)
            .select_related("user")
            .order_by("-created_at")
        )

    def paginate_queryset(self, queryset, page_size):
        paginator = Paginator(queryset, page_size)
        page_number = self.request.GET.get("page") or 1
        try:
            page_obj = paginator.page(page_number)
        except (PageNotAnInteger, EmptyPage):
            page_obj = paginator.page(paginator.num_pages or 1)
        return paginator, page_obj, page_obj.object_list, page_obj.has_other_pages()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        object_list = getattr(self, "object_list", None)
        ctx["no_posts"] = (object_list is None) or (len(object_list) == 0)
        if ctx["no_posts"]:
            ctx.setdefault("empty_message", "No posts yet. Be the first to create one.")
        return ctx



class PostDetailView(DetailView):
    model = Post
    template_name = "apps/posts/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return Post.objects.filter(is_active=True).select_related("user")

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            messages.warning(request, "Requested post not found. It may have been deleted.")
            return redirect("posts:list")









class UserPostsView(LoginRequiredMixin, ListView):
    """List of posts created by the currently logged-in user."""
    model = Post
    template_name = "apps/posts/user_posts.html"
    context_object_name = "posts"
    ordering = ["-created_at"]
    paginate_by = 9

    def get_queryset(self):
        """Filter posts belonging to the current user only."""
        return Post.objects.filter(user=self.request.user).order_by("-created_at")


