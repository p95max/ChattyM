"""
Context processors for messaging UI.
"""
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import OuterRef, Subquery
from .models import Conversation, Message, Participant

User = get_user_model()


def unread_messages_count(request):
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return {"unread_messages_count": 0}
    try:
        total = 0
        parts = Participant.objects.filter(user=request.user, is_active=True).select_related("conversation")
        for p in parts:
            last_read = p.last_read or timezone.datetime(1970, 1, 1, tzinfo=timezone.utc)
            qs = Message.objects.filter(conversation=p.conversation, created_at__gt=last_read).exclude(sender=request.user)
            total += qs.count()
        total = int(total)
    except Exception:
        total = 0
    return {"unread_messages_count": total}


def messaging_notifications(request):
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return {"unread_messages_count": 0, "recent_conversations_for_nav": []}
    try:
        unread_count = 0
        parts = Participant.objects.filter(user=request.user, is_active=True).select_related("conversation")
        for p in parts:
            unread_count += p.conversation.unread_count_for(request.user) if hasattr(p.conversation, "unread_count_for") else 0
    except Exception:
        unread_count = 0
    last_msg_qs = Message.objects.filter(conversation=OuterRef("pk")).order_by("-created_at")
    convs = (
        Conversation.objects.filter(participants__user=request.user, participants__is_active=True)
        .distinct()
        .annotate(last_message_id=Subquery(last_msg_qs.values("id")[:1]))
        .order_by("-created_at")[:5]
    )
    last_ids = [c.last_message_id for c in convs if getattr(c, "last_message_id", None)]
    msg_qs = Message.objects.filter(pk__in=last_ids).select_related("sender") if last_ids else Message.objects.none()
    msg_map = {m.pk: m for m in msg_qs}
    recent = []
    for c in convs:
        last = msg_map.get(getattr(c, "last_message_id", None))
        other = c.participants.exclude(user=request.user).select_related("user").first()
        other_user = getattr(other, "user", None)
        recent.append({
            "conversation": c,
            "other_user": other_user,
            "last_message": last,
            "unread": c.unread_count_for(request.user) if hasattr(c, "unread_count_for") else 0,
        })
    return {"unread_messages_count": unread_count, "recent_conversations_for_nav": recent}
