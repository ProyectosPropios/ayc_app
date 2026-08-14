from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    work_order_code = serializers.CharField(source="work_order.code", read_only=True)

    class Meta:
        model = Notification
        fields = (
            "id",
            "notification_type",
            "title",
            "message",
            "payload",
            "work_order",
            "work_order_code",
            "is_read",
            "created_at",
        )
        read_only_fields = (
            "id",
            "notification_type",
            "title",
            "message",
            "payload",
            "work_order",
            "work_order_code",
            "created_at",
        )
