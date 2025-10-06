from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.templatetags.static import static
from django.views.generic import ListView, DetailView
from django.http import Http404
from .models import Post
from apps.likes.models import Like
from ..comments.forms import CommentForm


class PostListView(ListView):
    """
    List all active posts with pagination.

    Context additions:
      - liked_post_ids: set of post PKs liked by the current user (if authenticated)
      - no_posts, empty_message preserved as before
    """
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
        if object_list is None:
            object_list = ctx.get("object_list", None)

        ctx["no_posts"] = (object_list is None) or (len(object_list) == 0)
        if ctx["no_posts"]:
            ctx.setdefault("empty_message", "No posts yet. Be the first to create one.")

        user = self.request.user
        ctx["liked_post_ids"] = set()
        if user.is_authenticated and object_list:
            try:
                post_pks = [p.pk for p in object_list]
            except Exception:
                post_pks = []
            if post_pks:
                liked_qs = Like.objects.filter(user=user, post_id__in=post_pks).values_list("post_id", flat=True)
                ctx["liked_post_ids"] = set(liked_qs)

        return ctx


class PostDetailView(DetailView):
    """
    Display a single post with comment form and comment list context.

    Context provided:
      - post (from DetailView)
      - user_liked: bool
      - form: CommentForm() instance for posting new comments
      - comments_count: int (count of active comments)
      - root_comments: queryset of top-level active comments (prefetched replies)
    """
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

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        post = self.object

        ctx["user_liked"] = False
        if user.is_authenticated:
            ctx["user_liked"] = Like.objects.filter(user=user, post=post).exists()

        from apps.comments.forms import CommentForm  #
        ctx["form"] = CommentForm()

        ctx["comments_count"] = post.comments.filter(is_active=True).count()

        ctx["root_comments"] = (
            post.comments
            .filter(parent__isnull=True, is_active=True)
            .select_related("user")
            .prefetch_related("replies__user", "replies__replies")
        )

        def _avatar_for_user(u):
            try:
                return u.profile.avatar.url
            except Exception:
                return static('images/avatars/default.png')

        def _annotate_comment(cmt):

            try:
                cmt.avatar_url = _avatar_for_user(cmt.user)
            except Exception:
                cmt.avatar_url = static('images/avatars/default.png')
            try:
                for r in cmt.replies.all():
                    _annotate_comment(r)
            except Exception:
                pass

        for c in ctx["root_comments"]:
            _annotate_comment(c)

        return ctx


class UserPostsView(LoginRequiredMixin, ListView):
    """
    List of posts created by the currently logged-in user.

    Adds liked_post_ids to the context (for consistency with other lists).
    """
    model = Post
    template_name = "apps/posts/user_posts.html"
    context_object_name = "posts"
    ordering = ["-created_at"]
    paginate_by = 9

    def get_queryset(self):
        """Filter posts belonging to the current user only."""
        return Post.objects.filter(user=self.request.user).order_by("-created_at")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        object_list = getattr(self, "object_list", None) or ctx.get("object_list", None)

        user = self.request.user
        ctx["liked_post_ids"] = set()
        if user.is_authenticated and object_list:
            try:
                post_pks = [p.pk for p in object_list]
            except Exception:
                post_pks = []
            if post_pks:
                liked_qs = Like.objects.filter(user=user, post_id__in=post_pks).values_list("post_id", flat=True)
                ctx["liked_post_ids"] = set(liked_qs)

        return ctx
