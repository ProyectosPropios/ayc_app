from django.db import models

# Create your models here.
import uuid

from django.conf import settings
from django.db import models

from customer.models import Customer


class WorkOrder(models.Model):
    class Status(models.TextChoices):
        PENDING = "pendiente", "Pendiente"
        ASSIGNED = "asignado", "Asignado"
        IN_PROGRESS = "en_labor", "En labor"
        COMPLETED = "realizado", "Realizado"
        CLOSED = "terminado", "Terminado"
        CANCELLED = "cancelado", "Cancelado"

    class Priority(models.TextChoices):
        LOW = "baja", "Baja"
        NORMAL = "normal", "Normal"
        HIGH = "alta", "Alta"
        URGENT = "urgente", "Urgente"

    code = models.CharField("número de orden", max_length=20, unique=True, editable=False)
    title = models.CharField("título", max_length=150)
    description = models.TextField("descripción")
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="work_orders",
        verbose_name="cliente",
    )
    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_work_orders",
        verbose_name="técnico asignado",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_work_orders",
        verbose_name="creada por",
    )
    scheduled_date = models.DateField("fecha programada")
    scheduled_time = models.TimeField("hora programada", null=True, blank=True)
    service_address = models.CharField("dirección del servicio", max_length=255, blank=True)
    priority = models.CharField(
        "prioridad",
        max_length=10,
        choices=Priority.choices,
        default=Priority.NORMAL,
    )
    status = models.CharField(
        "estado",
        max_length=15,
        choices=Status.choices,
        default=Status.PENDING,
    )
    notes = models.TextField("notas internas", blank=True)
    created_at = models.DateTimeField("fecha de creación", auto_now_add=True)
    updated_at = models.DateTimeField("última actualización", auto_now=True)

    class Meta:
        verbose_name = "orden de trabajo"
        verbose_name_plural = "órdenes de trabajo"
        ordering = ["-scheduled_date", "scheduled_time", "-created_at"]

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = f"OT-{uuid.uuid4().hex[:10].upper()}"
        if self.technician_id and self.status == self.Status.PENDING:
            self.status = self.Status.ASSIGNED
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} - {self.title}"
