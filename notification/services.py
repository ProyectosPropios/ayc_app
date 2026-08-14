import logging

import pusher
from django.conf import settings

from .models import Notification

logger = logging.getLogger(__name__)


def publish_realtime_notification(notification):
    """Publica una notificación por Pusher si está habilitado."""

    if not getattr(settings, "PUSHER_ENABLED", False):
        return

    config = settings.PUSHER_CONFIG
    if not all(config.get(key) for key in ("app_id", "key", "secret", "cluster")):
        logger.warning("Pusher está habilitado, pero faltan credenciales.")
        return

    try:
        client = pusher.Pusher(**config)
        client.trigger(
            f"private-user-{notification.recipient_id}",
            "notification.created",
            {
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "notification_type": notification.notification_type,
                "work_order_id": notification.work_order_id,
                "created_at": notification.created_at.isoformat(),
            },
        )
    except Exception:
        logger.exception("No se pudo publicar la notificación en tiempo real.")


def notify_user(*, recipient, title, message, notification_type=Notification.Type.GENERAL, work_order=None, payload=None):
    notification = Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        notification_type=notification_type,
        work_order=work_order,
        payload=payload or {},
    )
    publish_realtime_notification(notification)
    return notification
