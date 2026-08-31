from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from notification.models import Notification
from notification.services import notify_user
from users.models import User
from users.permissions import IsAdminRole

from .models import PumpingReport
from .pdf import generate_pumping_report_pdf
from .serializers import PumpingReportSerializer
from .services import send_pumping_report_email


class PumpingReportViewSet(viewsets.ModelViewSet):
    queryset = PumpingReport.objects.select_related(
        "work_order__customer",
        "work_order__technician",
        "created_by",
    ).all()
    serializer_class = PumpingReportSerializer

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
        report = serializer.save()
        if report.work_order.technician:
            notify_user(
                recipient=report.work_order.technician,
                title="Nuevo informe de bombeo",
                message=f"Se creó el informe de bombeo de la orden {report.work_order.code}.",
                notification_type=Notification.Type.WORK_ORDER_STATUS,
                work_order=report.work_order,
            )

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
        response = HttpResponse(
            generate_pumping_report_pdf(report),
            content_type="application/pdf",
        )
        response["Content-Disposition"] = (
            f'attachment; filename="{report.work_order.code}-bombeo.pdf"'
        )
        return response

    @action(detail=True, methods=["post"], url_path="send-email")
    def send_email(self, request, pk=None):
        report = self.get_object()
        if report.status != PumpingReport.ReportStatus.COMPLETED:
            return Response(
                {"detail": "Solo puedes enviar informes terminados y firmados."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            send_pumping_report_email(report)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Informe enviado al correo del cliente."})
