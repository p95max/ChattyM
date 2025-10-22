from .models import Notification

def notifications_for_nav(request):
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return {"unread_notifications_count": 0, "recent_notifications_for_nav": []}
    try:
        unread_count = Notification.objects.filter(recipient=request.user, unread=True).count()
        recent = Notification.objects.filter(recipient=request.user).order_by("-created_at")[:6]
    except Exception:
        unread_count = 0
        recent = []
    return {"unread_notifications_count": unread_count, "recent_notifications_for_nav": recent}
