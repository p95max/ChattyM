from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from apps.posts.models import Post
from .forms import ProfileForm

User = get_user_model()


class BaseProfileView(LoginRequiredMixin, View):

    template_name = "apps/users/profile.html"

    def get_context(self, request, target_user, form=None):
        posts_qs = Post.objects.filter(user=target_user).only(
            "id", "likes_count", "title", "created_at", "image"
        )
        is_owner = (target_user == request.user)

        recent_posts = posts_qs.order_by("-created_at")[:4]

        ctx = {
            "profile_user": target_user,
            "is_owner": is_owner,
            "posts_count": posts_qs.count(),
            "likes_sum": posts_qs.aggregate(Sum("likes_count"))["likes_count__sum"] or 0,
            "recent_posts": recent_posts,
        }

        if is_owner:
            ctx["form"] = form or ProfileForm(instance=target_user)

        return ctx


class MyProfileView(BaseProfileView):

    def get(self, request, *args, **kwargs):
        target = request.user
        return render(request, self.template_name, self.get_context(request, target))

    def post(self, request, *args, **kwargs):
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("users:my_profile")
        return render(request, self.template_name, self.get_context(request, request.user, form=form))


class ProfileView(BaseProfileView):

    def get(self, request, username, *args, **kwargs):
        target = get_object_or_404(User, username=username)
        return render(request, self.template_name, self.get_context(request, target))
