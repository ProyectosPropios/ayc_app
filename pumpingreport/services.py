from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .pdf import generate_pumping_report_pdf


def send_pumping_report_email(report):
    """Envía el reporte y su PDF directamente desde memoria."""
    if not settings.EMAIL_DELIVERY_ENABLED:
        raise ValueError("El envío de correo no está configurado en este entorno.")
    customer = report.work_order.customer
    if not customer.email:
        raise ValueError("El cliente no tiene un correo electrónico registrado.")

    html_content = render_to_string(
        "pumpingreport/email_report.html",
        {
            "nombre": customer.name,
            "code": report.work_order.code,
            "frontend_url": settings.FRONTEND_URL,
        },
    )
    message = EmailMultiAlternatives(
        subject=f"Reporte de mantenimiento de bombeo - {report.work_order.code}",
        body=strip_tags(html_content),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[customer.email],
    )
    message.attach_alternative(html_content, "text/html")
    message.attach(
        f"{report.work_order.code}-bombeo.pdf",
        generate_pumping_report_pdf(report),
        "application/pdf",
    )
    message.send()
