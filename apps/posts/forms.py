from django.views.generic import CreateView, UpdateView, DeleteView
from apps.posts.models import Post
from django.urls import reverse_lazy
from utils.posts_utils import AuthorRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms



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




class SearchForm(forms.Form):
    q = forms.CharField(required=False, max_length=120)
