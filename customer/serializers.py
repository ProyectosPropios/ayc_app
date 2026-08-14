from rest_framework import serializers

from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)

    class Meta:
        model = Customer
        fields = (
            "id",
            "name",
            "identification",
            "email",
            "phone",
            "address",
            "city",
            "notes",
            "is_active",
            "created_by_email",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_by_email", "created_at", "updated_at")
