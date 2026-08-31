import secrets

from django.conf import settings
from django.db import transaction
from rest_framework import generics, status
from rest_framework.exceptions import APIException
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import User
from .permissions import IsAdminRole
from .serializers import (
    BootstrapAdminSerializer,
    ChangePasswordSerializer,
    LoginSerializer,
    TechnicianSerializer,
    UserSerializer,
)
from .services import send_technician_credentials


def _set_auth_cookies(response, data):
    secure = not settings.DEBUG
    samesite = settings.AUTH_COOKIE_SAMESITE
    response.set_cookie("access_token", data["access"], httponly=True, secure=secure, samesite=samesite)
    response.set_cookie("refresh_token", data["refresh"], httponly=True, secure=secure, samesite=samesite)


class LoginView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            _set_auth_cookies(response, response.data)
        return response


class RefreshView(TokenRefreshView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        data.setdefault("refresh", request.COOKIES.get("refresh_token"))
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        response = Response(serializer.validated_data, status=status.HTTP_200_OK)
        if response.status_code == status.HTTP_200_OK:
            response.set_cookie(
                "access_token",
                response.data["access"],
                httponly=True,
                secure=not settings.DEBUG,
                samesite=settings.AUTH_COOKIE_SAMESITE,
            )
        return response


class LogoutView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except Exception:
                pass

        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response


class MeView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save(update_fields=["password"])
        return Response({"detail": "Contraseña actualizada correctamente."})


class BootstrapAdminView(APIView):
    """Crea una sola vez el superusuario inicial en Render Free."""

    permission_classes = (AllowAny,)

    def post(self, request):
        expected_token = getattr(settings, "BOOTSTRAP_ADMIN_TOKEN", "")
        provided_token = request.headers.get("X-Bootstrap-Token", "")
        if not expected_token or not secrets.compare_digest(provided_token, expected_token):
            return Response(status=status.HTTP_404_NOT_FOUND)

        if User.objects.filter(is_superuser=True).exists():
            return Response(
                {"detail": "El superusuario inicial ya fue creado."},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = BootstrapAdminSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = User(
            email=User.objects.normalize_email(data["email"]).lower(),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            role=User.Role.ADMIN,
            is_staff=True,
            is_superuser=True,
            is_active=True,
        )
        user.set_password(data["password"])
        user.full_clean()
        user.save()

        return Response(
            {"detail": "Superusuario creado correctamente. Elimina BOOTSTRAP_ADMIN_TOKEN ahora."},
            status=status.HTTP_201_CREATED,
        )


class TechnicianListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAdminRole,)
    serializer_class = TechnicianSerializer

    def get_queryset(self):
        return User.objects.filter(role=User.Role.TECHNICIAN)

    @transaction.atomic
    def perform_create(self, serializer):
        user = serializer.save()
        try:
            send_technician_credentials(user, serializer.generated_password)
        except Exception as exc:
            raise APIException(
                "No se pudo enviar el correo de credenciales; el técnico no fue creado."
            ) from exc


class TechnicianDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAdminRole,)
    serializer_class = TechnicianSerializer

    def get_queryset(self):
        return User.objects.filter(role=User.Role.TECHNICIAN)
