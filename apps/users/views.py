from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views import View
from apps.posts.models import Post
from django.db.models import Sum
from .forms import ProfileForm

class ProfileView(LoginRequiredMixin, View):
    template_name = "users/profile.html"

    def get_context(self, request, form=None):
        user = request.user
        posts_qs = Post.objects.filter(user=user).only("id", "likes_count")
        return {
            "form": form or ProfileForm(instance=user),
            "posts_count": posts_qs.count(),
            "likes_sum": posts_qs.aggregate(Sum("likes_count"))["likes_count__sum"] or 0,
        }

    def get(self, request):
        return render(request, self.template_name, self.get_context(request))

    def post(self, request):
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("users:profile")
        return render(request, self.template_name, self.get_context(request, form=form))
