from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


def generate_temporary_password(length=14):
    import secrets
    import string

    required = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice("!@#$%^&*()-_=+"),
    ]
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    password = required + [secrets.choice(alphabet) for _ in range(length - len(required))]
    secrets.SystemRandom().shuffle(password)
    return "".join(password)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "role", "date_joined")
        read_only_fields = ("id", "email", "role", "date_joined")


class LoginSerializer(TokenObtainPairSerializer):
    """Valida las credenciales usando el correo como identificador."""

    username_field = User.USERNAME_FIELD

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value, self.context["request"].user)
        return value

    def validate(self, attrs):
        if not authenticate(
            email=self.context["request"].user.email,
            password=attrs["current_password"],
        ):
            raise serializers.ValidationError({"current_password": "La contraseña actual no es correcta."})
        return attrs


class TechnicianSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "password", "is_active", "date_joined")
        read_only_fields = ("id", "date_joined")

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop("password", None) or generate_temporary_password()
        user = User.objects.create_user(
            password=password,
            role=User.Role.TECHNICIAN,
            **validated_data,
        )
        self.generated_password = password
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if password:
            instance.set_password(password)
        instance.role = User.Role.TECHNICIAN
        instance.save()
        return instance
