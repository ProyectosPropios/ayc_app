from django.db import models

# Create your models here.
from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models

from users.models import name_validator


phone_validator = RegexValidator(
    regex=r"^\+?[0-9 ()-]{7,20}$",
    message="Introduce un teléfono válido usando números, espacios, paréntesis o guiones.",
)


class Customer(models.Model):
    name = models.CharField(
        "nombre del cliente",
        max_length=150,
        validators=[name_validator],
    )
    identification = models.CharField("identificación/NIT", max_length=30, blank=True)
    email = models.EmailField("correo electrónico", blank=True)
    phone = models.CharField("teléfono", max_length=20, validators=[phone_validator])
    address = models.CharField("dirección", max_length=255)
    city = models.CharField("ciudad", max_length=100)
    notes = models.TextField("observaciones", blank=True)
    is_active = models.BooleanField("activo", default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_customers",
        verbose_name="creado por",
    )
    created_at = models.DateTimeField("fecha de creación", auto_now_add=True)
    updated_at = models.DateTimeField("última actualización", auto_now=True)

    class Meta:
        verbose_name = "cliente"
        verbose_name_plural = "clientes"
        ordering = ["name"]

    def __str__(self):
        return self.name
