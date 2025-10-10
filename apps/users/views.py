from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from apps.posts.models import Post
from .forms import ProfileForm
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from apps.subscriptions.models import Subscription

User = get_user_model()


class BaseProfileView(LoginRequiredMixin, View):

    template_name = "apps/users/profile.html"

    def get_context(self, request, target_user, form=None):
        posts_qs = Post.objects.filter(user=target_user).only(
            "id", "likes_count", "title", "created_at", "image"
        )
        is_owner = (target_user == request.user)

        recent_posts = posts_qs.order_by("-created_at")[:4]

        followers_count = Subscription.objects.filter(following=target_user, is_active=True).count()

        is_subscribed = False
        if request.user.is_authenticated and request.user != target_user:
            is_subscribed = Subscription.objects.filter(
                follower=request.user, following=target_user, is_active=True
            ).exists()

        toggle_url = reverse("subscriptions:toggle", args=[target_user.pk])

        followers_qs = Subscription.objects.filter(
            following=target_user, is_active=True
        ).select_related("follower").order_by("-created_at")[:10]

        ctx = {
            "profile_user": target_user,
            "is_owner": is_owner,
            "posts_count": posts_qs.count(),
            "likes_sum": posts_qs.aggregate(Sum("likes_count"))["likes_count__sum"] or 0,
            "recent_posts": recent_posts,
            "is_subscribed": is_subscribed,
            "followers_count": followers_count,
            "toggle_url": toggle_url,
            "followers": followers_qs,
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

    def _safe_redirect_back(self, request, fallback="core:main"):
        referer = request.META.get("HTTP_REFERER")
        if referer and url_has_allowed_host_and_scheme(referer, allowed_hosts={request.get_host()}):
            return redirect(referer)
        return redirect(reverse(fallback))

    def get(self, request, username, *args, **kwargs):
        try:
            target = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.warning(request, "User does not exist.")
            return self._safe_redirect_back(request)

        return render(request, self.template_name, self.get_context(request, target))

    def post(self, request, username, *args, **kwargs):

        try:
            target = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.warning(request, "User does not exist.")
            return self._safe_redirect_back(request)

        if target != request.user:
            messages.error(request, "Your have not permission to edit another profile.")
            return self._safe_redirect_back(request)

        form = ProfileForm(request.POST, request.FILES, instance=target)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("users:author_profile", username=target.username)
        return render(request, self.template_name, self.get_context(request, target, form=form))

