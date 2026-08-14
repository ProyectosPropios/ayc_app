from celery import shared_task
from django.utils import timezone

from notification.models import Notification
from notification.services import notify_user

from .models import WorkOrder


@shared_task
def enviar_recordatorio_trabajos_dia():
    """Notifica a los técnicos las órdenes pendientes del día actual."""

    today = timezone.localdate()
    orders = WorkOrder.objects.select_related("technician").filter(
        scheduled_date=today,
        technician__is_active=True,
        status__in=(WorkOrder.Status.PENDING, WorkOrder.Status.ASSIGNED),
    )
    sent = 0

    for order in orders:
        already_sent = Notification.objects.filter(
            recipient=order.technician,
            work_order=order,
            notification_type=Notification.Type.WORK_ORDER_ASSIGNED,
            created_at__date=today,
        ).exists()
        if already_sent:
            continue

        notify_user(
            recipient=order.technician,
            title="Recordatorio de trabajo para hoy",
            message=f"Recuerda la orden {order.code}: {order.title}.",
            notification_type=Notification.Type.WORK_ORDER_ASSIGNED,
            work_order=order,
            payload={"reminder": True},
        )
        sent += 1

    return sent
