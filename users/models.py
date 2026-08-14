from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


name_validator = RegexValidator(
    regex=r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s'-]+$",
    message="Este campo solo puede contener letras, espacios, apóstrofes y guiones.",
)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El correo electrónico es obligatorio.")

        user = self.model(
            email=self.normalize_email(email).lower(),
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", User.Role.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("El superusuario debe tener is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("El superusuario debe tener is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ADMIN = "admin", "Administrador"
        TECHNICIAN = "tecnico", "Técnico"

    email = models.EmailField("correo electrónico", unique=True)
    first_name = models.CharField(
        "nombres",
        max_length=100,
        blank=True,
        validators=[name_validator],
    )
    last_name = models.CharField(
        "apellidos",
        max_length=100,
        blank=True,
        validators=[name_validator],
    )
    role = models.CharField(
        "rol",
        max_length=20,
        choices=Role.choices,
        default=Role.TECHNICIAN,
    )
    is_staff = models.BooleanField(
        "acceso al administrador",
        default=False,
    )
    is_active = models.BooleanField("activo", default=True)
    date_joined = models.DateTimeField("fecha de registro", default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"
        ordering = ["last_name", "first_name", "email"]

    def save(self, *args, **kwargs):
        # Todo administrador debe poder entrar al panel de Django.
        self.is_staff = self.role == self.Role.ADMIN or self.is_superuser
        super().save(*args, **kwargs)
