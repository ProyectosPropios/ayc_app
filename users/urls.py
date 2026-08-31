from django.urls import path

from .views import (
    BootstrapAdminView,
    ChangePasswordView,
    LoginView,
    LogoutView,
    MeView,
    RefreshView,
    TechnicianDetailView,
    TechnicianListCreateView,
)

urlpatterns = [
    path("bootstrap-admin/", BootstrapAdminView.as_view(), name="bootstrap-admin"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshView.as_view(), name="refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("technicians/", TechnicianListCreateView.as_view(), name="technician-list-create"),
    path("technicians/<int:pk>/", TechnicianDetailView.as_view(), name="technician-detail"),
]
