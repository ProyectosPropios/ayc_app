from django.conf import settings
from django.template.loader import render_to_string
from weasyprint import HTML

from .models import ElectricalReport


def generate_electrical_report_pdf(report: ElectricalReport) -> bytes:
    """Renderiza el informe en memoria y devuelve los bytes del PDF.

    No se crea ningun archivo temporal ni permanente en el servidor. Esto
    permite descargar el PDF desde la API o adjuntarlo a un correo.
    """
    report = (
        ElectricalReport.objects.select_related(
            "work_order__customer",
            "work_order__technician",
            "created_by",
        )
        .get(pk=report.pk)
    )
    inspection_items = [
        {
            "key": key,
            "label": label,
            "status": getattr(report, f"{key}_status"),
            "observation": getattr(report, f"{key}_observation"),
        }
        for key, label in ElectricalReport.INSPECTION_DEFINITIONS
    ]
    html = render_to_string(
        "electricalreport/electrical_report.html",
        {
            "report": report,
            "customer": report.work_order.customer,
            "inspection_items": inspection_items,
            "company_logo_url": settings.CLOUDINARY_LOGO_URL,
        },
    )
    return HTML(string=html, base_url=str(settings.BASE_DIR)).write_pdf()
