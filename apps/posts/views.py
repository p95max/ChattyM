from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.templatetags.static import static
from django.views.generic import ListView, DetailView
from django.http import Http404
from .models import Post
from apps.likes.models import Like
from django.db.models import Q
from taggit.models import Tag


class PostListView(ListView):
    model = Post
    template_name = "apps/posts/posts_list.html"
    context_object_name = "posts"
    paginate_by = 9

    def get_queryset(self):
        qs = (
            Post.objects.filter(is_active=True)
            .select_related("user")
            .prefetch_related("tags")
            .order_by("-created_at")
        )

        q = self.request.GET.get('q', '')
        if q:
            q = q.strip()
            qs = qs.filter(Q(title__icontains=q) | Q(text__icontains=q))

        tag = self.request.GET.get('tag')
        if tag:
            qs = qs.filter(tags__slug__iexact=tag)

        return qs

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
        object_list = getattr(self, "object_list", None) or ctx.get("object_list", None)

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

        ctx["q"] = self.request.GET.get('q', '').strip()
        ctx["tag"] = self.request.GET.get('tag', '').strip()
        return ctx


class PostDetailView(DetailView):
    model = Post
    template_name = "apps/posts/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return Post.objects.filter(is_active=True).select_related("user").prefetch_related("tags")

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

        from apps.comments.forms import CommentForm
        ctx["form"] = CommentForm()

        ctx["comments"] = (
            post.comments
            .filter(is_active=True)
            .select_related("user")
            .order_by("created_at")
        )

        ctx["comments_count"] = ctx["comments"].count()

        return ctx


class UserPostsView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "apps/posts/user_posts.html"
    context_object_name = "posts"
    ordering = ["-created_at"]
    paginate_by = 9

    def get_queryset(self):
        return (
            Post.objects.filter(user=self.request.user)
            .select_related("user")
            .prefetch_related("tags")
            .order_by("-created_at")
        )

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


class TagPostListView(ListView):
    template_name = 'apps/posts/posts_list.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        value = self.kwargs.get('slug', '').strip()
        if not value:
            return Post.objects.none()

        tag_fields = [f.name for f in Tag._meta.get_fields()]
        if 'slug' in tag_fields:
            filter_kwargs = {'tags__slug__iexact': value}
            self.tag = Tag.objects.filter(slug__iexact=value).first()
        else:
            filter_kwargs = {'tags__name__iexact': value}
            self.tag = Tag.objects.filter(name__iexact=value).first()

        return (
            Post.objects.filter(is_active=True, **filter_kwargs)
                        .select_related('user')
                        .prefetch_related('tags')
                        .order_by('-created_at')
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['tag'] = self.tag or self.kwargs.get('slug')
        return ctx
