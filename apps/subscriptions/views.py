from django.views import View
from django.views.generic import ListView
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from .models import Subscription

User = get_user_model()


@method_decorator(login_required, name="dispatch")
class ToggleSubscriptionView(View):
    """
    Toggle subscription (follow/unfollow) to a user.
    Expects POST to /subscriptions/toggle/<int:user_pk>/.
    Returns JSON: {"status":"ok","following":bool,"followers_count":int}
    """
    def post(self, request, user_pk, *args, **kwargs):
        target = get_object_or_404(User, pk=user_pk, is_active=True)

        if target == request.user:
            return HttpResponseBadRequest("Cannot subscribe to yourself")

        try:
            sub, created = Subscription.objects.get_or_create(
                follower=request.user,
                following=target,
                defaults={"is_active": True}
            )
        except IntegrityError:

            try:
                sub_qs = Subscription.objects.filter(follower=request.user, following=target)
                if sub_qs.exists():
                    sub_qs.update(is_active=False)
                    following = False
                else:
                    following = False
            except Exception:
                return HttpResponseBadRequest("DB error")
        else:
            if not created:

                sub.is_active = not sub.is_active
                sub.save(update_fields=["is_active", "updated_at"])
            following = bool(sub.is_active)

        followers_count = Subscription.objects.filter(following=target, is_active=True).count()

        if following:
            try:
                from apps.notifications.services import create_notification
                create_notification(
                    recipient=target,
                    actor=request.user,
                    verb="started following you",
                    target=request.user,
                    data={"follower_id": request.user.pk, "follower_username": request.user.username}
                )
            except Exception:
                pass

        return JsonResponse({
            "status": "ok",
            "is_subscribed": following,
            "action": "subscribed" if following else "unsubscribed",
            "followers_count": followers_count,
        })


class FollowersListView(ListView):
    """
    Show followers of a user.
    URL: /subscriptions/followers/<int:user_pk>/
    """
    model = Subscription
    template_name = "apps/subscriptions/follower_list.html"
    context_object_name = "subscriptions"
    paginate_by = 30

    def get_queryset(self):
        user_pk = self.kwargs["user_pk"]
        return Subscription.objects.filter(following__pk=user_pk, is_active=True).select_related("follower").order_by("-created_at")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["profile_user"] = get_object_or_404(User, pk=self.kwargs["user_pk"])
        return ctx


class FollowingListView(ListView):
    """
    Show who the user is following.
    URL: /subscriptions/following/<int:user_pk>/
    """
    model = Subscription
    template_name = "apps/subscriptions/following_list.html"
    context_object_name = "subscriptions"
    paginate_by = 30

    def get_queryset(self):
        user_pk = self.kwargs["user_pk"]
        return Subscription.objects.filter(follower__pk=user_pk, is_active=True).select_related("following").order_by("-created_at")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["profile_user"] = get_object_or_404(User, pk=self.kwargs["user_pk"])
        return ctx
