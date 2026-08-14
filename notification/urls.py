from rest_framework.routers import DefaultRouter
from django.urls import path

from .views import NotificationViewSet, PusherAuthView


router = DefaultRouter()
router.register("", NotificationViewSet, basename="notification")

urlpatterns = [
    path("pusher/auth/", PusherAuthView.as_view(), name="pusher-auth"),
    *router.urls,
]
