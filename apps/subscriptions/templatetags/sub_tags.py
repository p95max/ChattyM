from django import template
from apps.subscriptions.models import Subscription

register = template.Library()

@register.filter
def followers_count(user):
    """Return number of active followers for the given user."""
    try:
        return Subscription.objects.filter(following=user, is_active=True).count()
    except Exception:
        return 0
