from django.conf import settings
from django.core.mail import send_mail


def send_technician_credentials(user, temporary_password):
    """Envía al técnico las credenciales iniciales de acceso."""

    send_mail(
        subject="Tus credenciales de acceso",
        message=(
            f"Hola {user.first_name or user.email},\n\n"
            "Se ha creado tu cuenta de técnico.\n\n"
            f"Correo: {user.email}\n"
            f"Contraseña temporal: {temporary_password}\n\n"
            "Inicia sesión y cambia esta contraseña lo antes posible.\n"
            f"Acceso: {getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')}"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
