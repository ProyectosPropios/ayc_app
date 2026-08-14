from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Type(models.TextChoices):
        WORK_ORDER_ASSIGNED = "work_order_assigned", "Orden asignada"
        WORK_ORDER_STATUS = "work_order_status", "Cambio de estado"
        GENERAL = "general", "General"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="destinatario",
    )
    work_order = models.ForeignKey(
        "workorder.WorkOrder",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
        verbose_name="orden de trabajo",
    )
    notification_type = models.CharField(
        "tipo",
        max_length=30,
        choices=Type.choices,
        default=Type.GENERAL,
    )
    title = models.CharField("título", max_length=150)
    message = models.TextField("mensaje")
    payload = models.JSONField("datos adicionales", default=dict, blank=True)
    is_read = models.BooleanField("leída", default=False)
    created_at = models.DateTimeField("fecha de creación", auto_now_add=True)

    class Meta:
        verbose_name = "notificación"
        verbose_name_plural = "notificaciones"
        ordering = ["is_read", "-created_at"]

    def __str__(self):
        return f"{self.recipient.email}: {self.title}"
