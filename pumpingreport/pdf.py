from django.conf import settings
from django.template.loader import render_to_string
from weasyprint import HTML

from .models import PumpingReport


def generate_pumping_report_pdf(report: PumpingReport) -> bytes:
    """Renderiza el reporte en memoria, sin guardar archivos en el servidor."""
    report = (
        PumpingReport.objects.select_related(
            "work_order__customer",
            "work_order__technician",
            "created_by",
        )
        .get(pk=report.pk)
    )
    html = render_to_string(
        "pumpingreport/pumping_report.html",
        {
            "report": report,
            "customer": report.work_order.customer,
            "company_logo_url": settings.CLOUDINARY_LOGO_URL,
        },
    )
    return HTML(string=html, base_url=str(settings.BASE_DIR)).write_pdf()
