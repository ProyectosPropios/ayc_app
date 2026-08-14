from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from notification.models import Notification
from notification.services import notify_user
from users.models import User
from users.permissions import IsAdminRole

from .models import WorkOrder
from .serializers import WorkOrderAdminSerializer, WorkOrderTechnicianSerializer


class WorkOrderViewSet(viewsets.ModelViewSet):
    queryset = WorkOrder.objects.select_related("customer", "technician", "created_by").all()

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.role == User.Role.ADMIN or self.request.user.is_superuser:
            return queryset
        return queryset.filter(technician=self.request.user)

    def get_permissions(self):
        if self.action in ("list", "retrieve", "partial_update", "update"):
            if self.request.user.is_authenticated and self.request.user.role != User.Role.ADMIN:
                return [IsAuthenticated()]
        return [IsAdminRole()]

    def get_serializer_class(self):
        if self.request.user.is_authenticated and self.request.user.role != User.Role.ADMIN:
            return WorkOrderTechnicianSerializer
        return WorkOrderAdminSerializer

    def perform_create(self, serializer):
        order = serializer.save()
        if order.technician:
            notify_user(
                recipient=order.technician,
                title="Nueva orden de trabajo asignada",
                message=f"Se te asignó la orden {order.code}: {order.title}.",
                notification_type=Notification.Type.WORK_ORDER_ASSIGNED,
                work_order=order,
            )

    def perform_update(self, serializer):
        previous_status = serializer.instance.status
        previous_technician_id = serializer.instance.technician_id
        order = serializer.save()

        if order.technician_id and order.technician_id != previous_technician_id:
            notify_user(
                recipient=order.technician,
                title="Nueva orden de trabajo asignada",
                message=f"Se te asignó la orden {order.code}: {order.title}.",
                notification_type=Notification.Type.WORK_ORDER_ASSIGNED,
                work_order=order,
            )

        if order.status != previous_status:
            recipients = (
                User.objects.filter(role=User.Role.ADMIN, is_active=True)
                if self.request.user.role != User.Role.ADMIN
                else ([order.technician] if order.technician else [])
            )
            for recipient in recipients:
                if recipient:
                    notify_user(
                        recipient=recipient,
                        title="Cambio de estado de orden",
                        message=f"La orden {order.code} ahora está '{order.get_status_display()}'.",
                        notification_type=Notification.Type.WORK_ORDER_STATUS,
                        work_order=order,
                        payload={"previous_status": previous_status, "status": order.status},
                    )
