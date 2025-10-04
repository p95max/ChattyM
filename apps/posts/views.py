from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from apps.posts.models import Post
from django.urls import reverse_lazy

from utils.posts_utils import AuthorRequiredMixin


class PostListView(ListView):
    model = Post
    template_name = "apps/posts/posts_list.html"
    context_object_name = "posts"
    paginate_by = 10
    queryset = Post.objects.filter(is_active=True).select_related("user")



class PostDetailView(DetailView):
    model = Post
    template_name = "apps/posts/post_detail.html"
    context_object_name = "post"



class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ["title", "text", "image"]
    template_name = "apps/posts/post_form.html"
    success_url = reverse_lazy("posts:list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)



class PostUpdateView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
    model = Post
    fields = ["title", "text", "image"]
    template_name = "apps/posts/post_form.html"
    success_url = reverse_lazy("posts:list")



class PostDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    model = Post
    template_name = "apps/posts/post_confirm_delete.html"
    success_url = reverse_lazy("posts:list")


