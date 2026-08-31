from django.conf import settings
from django.db import models
from django.utils import timezone

from workorder.models import WorkOrder


class PumpingReport(models.Model):
    class ReportStatus(models.TextChoices):
        DRAFT = "borrador", "Borrador"
        COMPLETED = "terminado", "Terminado"

    class TemperatureStatus(models.TextChoices):
        NORMAL = "normal", "Normal"
        OVERHEATED = "recalentada", "Recalentada"

    class NoiseStatus(models.TextChoices):
        NORMAL = "normal", "Normal"
        FAILURES = "fallas", "Fallas"

    class HumidityStatus(models.TextChoices):
        YES = "si", "Sí"
        NO = "no", "No"

    class ElectricalConnectionStatus(models.TextChoices):
        NORMAL = "normal", "Normal"
        FAILURES = "fallas", "Fallas"

    EQUIPMENT_FIELDS = (
        "pressure",
        "submersibles",
        "hp_measure",
        "hp_plate",
        "amperage_measure",
        "amperage_plate",
        "temperature",
        "noises",
        "humidity",
        "electrical_connections",
    )

    work_order = models.OneToOneField(
        WorkOrder,
        on_delete=models.PROTECT,
        related_name="pumping_report",
        verbose_name="orden de trabajo",
    )
    report_date = models.DateField("fecha", default=timezone.localdate)
    attention = models.CharField("atención", max_length=150, blank=True)
    equipment_rows = models.JSONField("equipos en H.P.", default=list)
    hydropneumatic_tank_brand = models.CharField("marca tanque hidroneumático", max_length=100, blank=True)
    hydropneumatic_tank_determined_charge = models.CharField("carga determinada", max_length=50, blank=True)
    hydropneumatic_tank_measured_charge = models.CharField("carga medida", max_length=50, blank=True)
    speed_controller_brand = models.CharField("marca controlador de velocidad", max_length=100, blank=True)
    observations = models.TextField("observaciones", blank=True)
    technician_name = models.CharField("técnico", max_length=150)
    technician_signature = models.TextField("firma digital del técnico", blank=True)
    status = models.CharField(
        "estado del informe",
        max_length=15,
        choices=ReportStatus.choices,
        default=ReportStatus.DRAFT,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_pumping_reports",
        verbose_name="creado por",
    )
    created_at = models.DateTimeField("fecha de creación", auto_now_add=True)
    updated_at = models.DateTimeField("última actualización", auto_now=True)

    class Meta:
        verbose_name = "informe de bombeo"
        verbose_name_plural = "informes de bombeo"
        ordering = ["-report_date", "-created_at"]

    def __str__(self):
        return f"Informe de bombeo - {self.work_order.code}"
