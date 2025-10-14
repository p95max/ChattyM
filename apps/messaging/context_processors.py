from .models import Participant

def messaging_unread_count(request):
    """
    Adds unread_messages_count into template context for navbar.
    """
    if not request.user.is_authenticated:
        return {}
    cnt = Participant.objects.filter(user=request.user, is_active=True).count()
    total_unread = 0
    for p in Participant.objects.filter(user=request.user, is_active=True).select_related('conversation'):
        total_unread += p.conversation.unread_count_for(request.user)
    return {"messages_unread_count": total_unread}
