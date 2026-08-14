from rest_framework.permissions import BasePermission

from .models import User


class IsAdminRole(BasePermission):
    message = "Solo un administrador puede realizar esta acción."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.role == User.Role.ADMIN or user.is_superuser)
        )
