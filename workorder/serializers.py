from rest_framework import serializers

from customer.models import Customer
from users.models import User

from .models import WorkOrder


class WorkOrderBaseSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    customer_address = serializers.CharField(source="customer.address", read_only=True)
    technician_email = serializers.EmailField(source="technician.email", read_only=True)
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)

    class Meta:
        model = WorkOrder
        fields = (
            "id",
            "code",
            "title",
            "description",
            "customer",
            "customer_name",
            "customer_address",
            "technician",
            "technician_email",
            "created_by_email",
            "scheduled_date",
            "scheduled_time",
            "service_address",
            "priority",
            "status",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "code",
            "customer_name",
            "customer_address",
            "technician_email",
            "created_by_email",
            "created_at",
            "updated_at",
        )

    def validate_customer(self, value):
        if not value.is_active:
            raise serializers.ValidationError("No puedes asignar una orden a un cliente inactivo.")
        return value

    def validate_technician(self, value):
        if value is not None and (
            value.role != User.Role.TECHNICIAN or not value.is_active
        ):
            raise serializers.ValidationError("El usuario seleccionado no es un técnico activo.")
        return value


class WorkOrderAdminSerializer(WorkOrderBaseSerializer):
    def create(self, validated_data):
        return WorkOrder.objects.create(
            created_by=self.context["request"].user,
            **validated_data,
        )


class WorkOrderTechnicianSerializer(WorkOrderBaseSerializer):
    """El técnico solo puede cambiar el estado de su orden asignada."""

    class Meta(WorkOrderBaseSerializer.Meta):
        read_only_fields = tuple(
            field for field in WorkOrderBaseSerializer.Meta.fields if field != "status"
        )

    def validate_status(self, value):
        if value not in (
            WorkOrder.Status.IN_PROGRESS,
            WorkOrder.Status.COMPLETED,
        ):
            raise serializers.ValidationError(
                "El técnico solo puede marcar una orden como 'en labor' o 'realizado'."
            )

        current = self.instance.status if self.instance else None
        allowed_transitions = {
            WorkOrder.Status.PENDING: {WorkOrder.Status.IN_PROGRESS},
            WorkOrder.Status.ASSIGNED: {WorkOrder.Status.IN_PROGRESS},
            WorkOrder.Status.IN_PROGRESS: {WorkOrder.Status.COMPLETED},
            WorkOrder.Status.COMPLETED: set(),
        }
        if current in allowed_transitions and value not in allowed_transitions[current]:
            raise serializers.ValidationError("Ese cambio de estado no está permitido.")
        return value
