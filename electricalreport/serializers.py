import re

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import ElectricalReport

User = get_user_model()
SIGNATURE_DATA_URL_PATTERN = re.compile(
    r"data:image/(?:png|jpe?g|webp);base64,[A-Za-z0-9+/=\s]+\Z"
)
MAX_SIGNATURE_LENGTH = 2_000_000


class ElectricalReportSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="work_order.customer.name", read_only=True)
    customer_address = serializers.CharField(source="work_order.customer.address", read_only=True)
    customer_city = serializers.CharField(source="work_order.customer.city", read_only=True)
    customer_phone = serializers.CharField(source="work_order.customer.phone", read_only=True)
    customer_email = serializers.EmailField(source="work_order.customer.email", read_only=True)
    work_order_code = serializers.CharField(source="work_order.code", read_only=True)
    inspection_items = serializers.SerializerMethodField()

    class Meta:
        model = ElectricalReport
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
            "responsible_name",
            "generator",
            "brand",
            "kva",
            "motor",
            "model_name",
            "serial_number",
            *ElectricalReport.inspection_field_names(),
            "inspection_items",
            "general_observations",
            "technician_name",
            "received_by",
            "technician_signature",
            "recipient_signature",
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
            "inspection_items",
            "created_by",
            "created_at",
            "updated_at",
        )
        extra_kwargs = {
            "technician_name": {"required": False},
        }

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

    def get_inspection_items(self, instance):
        return [
            {
                "key": key,
                "label": label,
                "status": getattr(instance, f"{key}_status"),
                "observation": getattr(instance, f"{key}_observation"),
            }
            for key, label in ElectricalReport.INSPECTION_DEFINITIONS
        ]

    def validate_technician_signature(self, value):
        return self._validate_signature(value, "la firma del técnico")

    def validate_recipient_signature(self, value):
        return self._validate_signature(value, "la firma del recibido")

    @staticmethod
    def _validate_signature(value, label):
        if value and (
            len(value) > MAX_SIGNATURE_LENGTH
            or not SIGNATURE_DATA_URL_PATTERN.fullmatch(value)
        ):
            raise serializers.ValidationError(
                f"{label.capitalize()} debe ser PNG, JPG o WebP en formato data URL y no superar 2 MB."
            )
        return value

    def validate(self, attrs):
        report_status = attrs.get(
            "status",
            getattr(self.instance, "status", ElectricalReport.ReportStatus.DRAFT),
        )
        technician_signature = attrs.get(
            "technician_signature",
            getattr(self.instance, "technician_signature", ""),
        )
        recipient_signature = attrs.get(
            "recipient_signature",
            getattr(self.instance, "recipient_signature", ""),
        )
        if report_status == ElectricalReport.ReportStatus.COMPLETED:
            missing = []
            if not technician_signature:
                missing.append("la firma del técnico")
            if not recipient_signature:
                missing.append("la firma del recibido")
            if missing:
                raise serializers.ValidationError(
                    {"status": "Para terminar el informe debes incluir " + " y ".join(missing) + "."}
                )
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["created_by"] = request.user
        full_name = " ".join(
            filter(None, [request.user.first_name, request.user.last_name])
        )
        validated_data.setdefault("technician_name", full_name or request.user.email)
        try:
            return super().create(validated_data)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict) from exc
