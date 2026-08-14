import re

from django.core.exceptions import ValidationError


def validate_strong_password(password):
    """Exige una contraseña adecuada para las cuentas del sistema."""

    rules = (
        (len(password) >= 8, "La contraseña debe tener al menos 8 caracteres."),
        (re.search(r"[A-Z]", password), "Debe incluir al menos una letra mayúscula."),
        (re.search(r"[a-z]", password), "Debe incluir al menos una letra minúscula."),
        (re.search(r"\d", password), "Debe incluir al menos un número."),
        (re.search(r"[^A-Za-z0-9]", password), "Debe incluir al menos un carácter especial."),
    )

    errors = [message for valid, message in rules if not valid]
    if errors:
        raise ValidationError(errors)


class StrongPasswordValidator:
    """Adaptador para el sistema AUTH_PASSWORD_VALIDATORS de Django."""

    def validate(self, password, user=None):
        validate_strong_password(password)

    def get_help_text(self):
        return "La contraseña debe incluir mayúscula, minúscula, número y carácter especial."
