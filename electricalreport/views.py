from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from users.models import User
from users.permissions import IsAdminRole

from .models import ElectricalReport
from .pdf import generate_electrical_report_pdf
from .serializers import ElectricalReportSerializer
from .services import send_electrical_report_email


class ElectricalReportViewSet(viewsets.ModelViewSet):
    queryset = ElectricalReport.objects.select_related(
        "work_order__customer",
        "work_order__technician",
        "created_by",
    ).all()
    serializer_class = ElectricalReportSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.role == User.Role.ADMIN or self.request.user.is_superuser:
            return queryset
        return queryset.filter(work_order__technician=self.request.user)

    def get_permissions(self):
        if self.action == "destroy":
            return [IsAdminRole()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        work_order = serializer.validated_data["work_order"]
        if (
            self.request.user.role != User.Role.ADMIN
            and not self.request.user.is_superuser
            and work_order.technician_id != self.request.user.id
        ):
            raise PermissionDenied("Solo puedes crear informes para tus órdenes asignadas.")
        serializer.save()

    def perform_update(self, serializer):
        if (
            self.request.user.role != User.Role.ADMIN
            and not self.request.user.is_superuser
            and serializer.instance.work_order.technician_id != self.request.user.id
        ):
            raise PermissionDenied("Solo puedes editar informes de tus órdenes asignadas.")
        serializer.save()

    @action(detail=True, methods=["get"], url_path="pdf")
    def pdf(self, request, pk=None):
        report = self.get_object()
        pdf_bytes = generate_electrical_report_pdf(report)
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="{report.work_order.code}-planta-electrica.pdf"'
        )
        return response

    @action(detail=True, methods=["post"], url_path="send-email")
    def send_email(self, request, pk=None):
        report = self.get_object()
        if report.status != ElectricalReport.ReportStatus.COMPLETED:
            return Response(
                {"detail": "Solo puedes enviar informes terminados y firmados."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            send_electrical_report_email(report)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Informe enviado al correo del cliente."})

# Create your views here.
