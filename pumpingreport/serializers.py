from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import PumpingReport

User = get_user_model()


class EquipmentRowSerializer(serializers.Serializer):
    pressure = serializers.CharField(required=False, allow_blank=True, default="")
    submersibles = serializers.CharField(required=False, allow_blank=True, default="")
    hp_measure = serializers.CharField(required=False, allow_blank=True, default="")
    hp_plate = serializers.CharField(required=False, allow_blank=True, default="")
    amperage_measure = serializers.CharField(required=False, allow_blank=True, default="")
    amperage_plate = serializers.CharField(required=False, allow_blank=True, default="")
    temperature = serializers.ChoiceField(
        choices=PumpingReport.TemperatureStatus.choices,
        required=False,
        default=PumpingReport.TemperatureStatus.NORMAL,
    )
    noises = serializers.ChoiceField(
        choices=PumpingReport.NoiseStatus.choices,
        required=False,
        default=PumpingReport.NoiseStatus.NORMAL,
    )
    humidity = serializers.ChoiceField(
        choices=PumpingReport.HumidityStatus.choices,
        required=False,
        default=PumpingReport.HumidityStatus.NO,
    )
    electrical_connections = serializers.ChoiceField(
        choices=PumpingReport.ElectricalConnectionStatus.choices,
        required=False,
        default=PumpingReport.ElectricalConnectionStatus.NORMAL,
    )


class PumpingReportSerializer(serializers.ModelSerializer):
    equipment_rows = EquipmentRowSerializer(many=True, allow_empty=False)
    customer_name = serializers.CharField(source="work_order.customer.name", read_only=True)
    customer_address = serializers.CharField(source="work_order.customer.address", read_only=True)
    customer_city = serializers.CharField(source="work_order.customer.city", read_only=True)
    customer_phone = serializers.CharField(source="work_order.customer.phone", read_only=True)
    customer_email = serializers.EmailField(source="work_order.customer.email", read_only=True)
    work_order_code = serializers.CharField(source="work_order.code", read_only=True)

    class Meta:
        model = PumpingReport
        fields = (
            "id",
            "work_order",
            "work_order_code",
            "customer_name",
            "customer_address",
            "customer_city",
            "customer_phone",
            "customer_email",
            "report_date",
            "attention",
            "equipment_rows",
            "hydropneumatic_tank_brand",
            "hydropneumatic_tank_determined_charge",
            "hydropneumatic_tank_measured_charge",
            "speed_controller_brand",
            "observations",
            "technician_name",
            "technician_signature",
            "status",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "work_order_code",
            "customer_name",
            "customer_address",
            "customer_city",
            "customer_phone",
            "customer_email",
            "created_by",
            "created_at",
            "updated_at",
        )
        extra_kwargs = {"technician_name": {"required": False}}

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")
        is_admin = bool(
            request
            and request.user.is_authenticated
            and (request.user.role == User.Role.ADMIN or request.user.is_superuser)
        )
        if request and request.method != "POST" and not is_admin:
            fields["work_order"].read_only = True
            fields["technician_name"].read_only = True
        return fields

    def validate_technician_signature(self, value):
        if value and not value.startswith("data:image/"):
            raise serializers.ValidationError(
                "La firma del técnico debe ser una imagen en formato data URL."
            )
        return value

    def validate(self, attrs):
        report_status = attrs.get(
            "status",
            getattr(self.instance, "status", PumpingReport.ReportStatus.DRAFT),
        )
        signature = attrs.get(
            "technician_signature",
            getattr(self.instance, "technician_signature", ""),
        )
        if report_status == PumpingReport.ReportStatus.COMPLETED and not signature:
            raise serializers.ValidationError(
                {"status": "Para terminar el informe debes incluir la firma del técnico."}
            )
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["created_by"] = request.user
        full_name = " ".join(filter(None, [request.user.first_name, request.user.last_name]))
        validated_data.setdefault("technician_name", full_name or request.user.email)
        try:
            return super().create(validated_data)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict) from exc
