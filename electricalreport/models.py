from django.conf import settings
from django.db import models
from django.utils import timezone

from workorder.models import WorkOrder


class ElectricalReport(models.Model):
    class ReportStatus(models.TextChoices):
        DRAFT = "borrador", "Borrador"
        COMPLETED = "terminado", "Terminado"

    class CheckResult(models.TextChoices):
        OK = "OK", "OK"
        NO = "NO", "NO"

    # Se conserva el orden del formato físico de referencia.
    INSPECTION_DEFINITIONS = (
        ("battery_terminals", "TERMINALES DE BATERÍA"),
        ("battery_water_level", "NIVEL DE AGUA DE BATERÍA"),
        ("battery_charger_load", "CARGA DE BATERÍA CARGADOR DE BATERÍA AC/DC"),
        ("alternator_charger", "CARGADOR DE ALTERNADOR"),
        ("oil_level", "NIVEL DE ACEITE"),
        ("coolant_level", "NIVEL DE REFRIGERANTE"),
        ("radiator_physical_inspection", "REV. FÍSICA RADIADOR"),
        ("air_filter_inspection", "REV. FILTRO DE AIRE"),
        ("preheater_inspection", "REV. PRECALENTADOR"),
        ("belt_tension_inspection", "REV. TENSIÓN CORREAS"),
        ("fuel_tank_level", "NIVEL TANQUE COMBUSTIBLE"),
        ("hose_clamps_inspection", "REV. ABRAZADERAS MANGUERAS"),
        ("electrical_terminals", "TERMINALES ELÉCTRICOS"),
        ("equipment_cleaning", "LIMPIAR EQUIPO"),
        ("intake_exhaust_muffler_flexible", "ADMISIÓN ESCAPE, SILENCIADOR Y FLEXIBLE"),
        ("after_fire_inspection", "DESPUÉS DE INCENDIO"),
        ("oil_pressure", "PRESIÓN DE ACEITE"),
        ("oil_temperature", "TEMPERATURA DE ACEITE"),
        ("coolant_temperature", "TEMPERATURA REFRIGERANTE"),
        ("coolant_leaks", "FUGAS DE REFRIGERANTE"),
        ("oil_leaks", "FUGAS DE ACEITE"),
        ("fuel_leaks", "FUGAS DE COMBUSTIBLE"),
        ("frequency_rpm", "FRECUENCIA RPM"),
        ("output_voltage", "VOLTAJE DE SALIDA"),
    )

    work_order = models.OneToOneField(
        WorkOrder,
        on_delete=models.PROTECT,
        related_name="electrical_report",
        verbose_name="orden de trabajo",
    )
    report_date = models.DateField("fecha", default=timezone.localdate)
    responsible_name = models.CharField("encargado(a)", max_length=150, blank=True)
    generator = models.CharField("generador", max_length=100, blank=True)
    brand = models.CharField("marca", max_length=100, blank=True)
    kva = models.CharField("KVA", max_length=30, blank=True)
    motor = models.CharField("motor", max_length=100, blank=True)
    model_name = models.CharField("modelo", max_length=100, blank=True)
    serial_number = models.CharField("serie", max_length=100, blank=True)

    battery_terminals_status = models.CharField(max_length=2, choices=CheckResult.choices)
    battery_terminals_observation = models.TextField(blank=True)
    battery_water_level_status = models.CharField(max_length=2, choices=CheckResult.choices)
    battery_water_level_observation = models.TextField(blank=True)
    battery_charger_load_status = models.CharField(max_length=2, choices=CheckResult.choices)
    battery_charger_load_observation = models.TextField(blank=True)
    alternator_charger_status = models.CharField(max_length=2, choices=CheckResult.choices)
    alternator_charger_observation = models.TextField(blank=True)
    oil_level_status = models.CharField(max_length=2, choices=CheckResult.choices)
    oil_level_observation = models.TextField(blank=True)
    coolant_level_status = models.CharField(max_length=2, choices=CheckResult.choices)
    coolant_level_observation = models.TextField(blank=True)
    radiator_physical_inspection_status = models.CharField(max_length=2, choices=CheckResult.choices)
    radiator_physical_inspection_observation = models.TextField(blank=True)
    air_filter_inspection_status = models.CharField(max_length=2, choices=CheckResult.choices)
    air_filter_inspection_observation = models.TextField(blank=True)
    preheater_inspection_status = models.CharField(max_length=2, choices=CheckResult.choices)
    preheater_inspection_observation = models.TextField(blank=True)
    belt_tension_inspection_status = models.CharField(max_length=2, choices=CheckResult.choices)
    belt_tension_inspection_observation = models.TextField(blank=True)
    fuel_tank_level_status = models.CharField(max_length=2, choices=CheckResult.choices)
    fuel_tank_level_observation = models.TextField(blank=True)
    hose_clamps_inspection_status = models.CharField(max_length=2, choices=CheckResult.choices)
    hose_clamps_inspection_observation = models.TextField(blank=True)
    electrical_terminals_status = models.CharField(max_length=2, choices=CheckResult.choices)
    electrical_terminals_observation = models.TextField(blank=True)
    equipment_cleaning_status = models.CharField(max_length=2, choices=CheckResult.choices)
    equipment_cleaning_observation = models.TextField(blank=True)
    intake_exhaust_muffler_flexible_status = models.CharField(max_length=2, choices=CheckResult.choices)
    intake_exhaust_muffler_flexible_observation = models.TextField(blank=True)
    after_fire_inspection_status = models.CharField(max_length=2, choices=CheckResult.choices)
    after_fire_inspection_observation = models.TextField(blank=True)
    oil_pressure_status = models.CharField(max_length=2, choices=CheckResult.choices)
    oil_pressure_observation = models.TextField(blank=True)
    oil_temperature_status = models.CharField(max_length=2, choices=CheckResult.choices)
    oil_temperature_observation = models.TextField(blank=True)
    coolant_temperature_status = models.CharField(max_length=2, choices=CheckResult.choices)
    coolant_temperature_observation = models.TextField(blank=True)
    coolant_leaks_status = models.CharField(max_length=2, choices=CheckResult.choices)
    coolant_leaks_observation = models.TextField(blank=True)
    oil_leaks_status = models.CharField(max_length=2, choices=CheckResult.choices)
    oil_leaks_observation = models.TextField(blank=True)
    fuel_leaks_status = models.CharField(max_length=2, choices=CheckResult.choices)
    fuel_leaks_observation = models.TextField(blank=True)
    frequency_rpm_status = models.CharField(max_length=2, choices=CheckResult.choices)
    frequency_rpm_observation = models.TextField(blank=True)
    output_voltage_status = models.CharField(max_length=2, choices=CheckResult.choices)
    output_voltage_observation = models.TextField(blank=True)

    general_observations = models.TextField("observaciones y recomendaciones", blank=True)
    technician_name = models.CharField("técnico", max_length=150)
    received_by = models.CharField("recibido por", max_length=150, blank=True)
    technician_signature = models.TextField("firma digital del técnico", blank=True)
    recipient_signature = models.TextField("firma digital del recibido", blank=True)
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
        related_name="created_electrical_reports",
        verbose_name="creado por",
    )
    created_at = models.DateTimeField("fecha de creación", auto_now_add=True)
    updated_at = models.DateTimeField("última actualización", auto_now=True)

    class Meta:
        verbose_name = "informe de planta eléctrica"
        verbose_name_plural = "informes de plantas eléctricas"
        ordering = ["-report_date", "-created_at"]

    @classmethod
    def inspection_field_names(cls):
        return tuple(
            field_name
            for field_name, _ in cls.INSPECTION_DEFINITIONS
            for field_name in (f"{field_name}_status", f"{field_name}_observation")
        )

    def __str__(self):
        return f"Informe eléctrico - {self.work_order.code}"
