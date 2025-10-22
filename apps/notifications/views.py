from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from .models import Notification

class RecentNotificationsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        qs = Notification.objects.filter(recipient=request.user).order_by("-created_at")[:8]
        items = []
        for n in qs:
            items.append({
                "id": n.pk,
                "verb": n.verb,
                "actor": getattr(n.actor, "username", None) if n.actor else None,
                "created_at": n.created_at.isoformat(),
                "unread": n.unread,
                "target": {
                    "ct": n.target_ct.model if n.target_ct else None,
                    "id": n.target_id
                } if n.target_ct else None,
                "data": n.data or {}
            })
        unread = Notification.objects.filter(recipient=request.user, unread=True).count()
        return JsonResponse({"status":"ok","unread_count": unread, "items": items})

class MarkReadView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        n = get_object_or_404(Notification, pk=pk, recipient=request.user)
        n.mark_read()
        unread = Notification.objects.filter(recipient=request.user, unread=True).count()
        return JsonResponse({"status":"ok","unread_count": unread})

class MarkAllReadView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        Notification.objects.filter(recipient=request.user, unread=True).update(unread=False)
        return JsonResponse({"status":"ok","unread_count": 0})
