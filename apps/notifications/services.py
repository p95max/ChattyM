from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from .models import Notification

def create_notification(recipient, verb, actor=None, target=None, data=None):
    """
    Create a notification safely. Non-fatal on failure.
    `target` can be any model instance.
    """
    try:
        with transaction.atomic():
            kwargs = {
                "recipient": recipient,
                "verb": verb,
                "actor": actor,
                "data": data or {}
            }
            if target is not None:
                kwargs["target_ct"] = ContentType.objects.get_for_model(target)
                kwargs["target_id"] = str(getattr(target, "pk", target))
            Notification.objects.create(**kwargs)
    except Exception:

        import logging
        logging.getLogger(__name__).exception("Failed to create notification")
