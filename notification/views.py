from django.conf import settings
from django.http import JsonResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

import pusher

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).select_related("work_order")

    @action(detail=True, methods=["post"], url_path="read")
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=["is_read"])
        return Response(self.get_serializer(notification).data)

    @action(detail=False, methods=["post"], url_path="read-all")
    def mark_all_read(self, request):
        updated = self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({"updated": updated}, status=status.HTTP_200_OK)


class PusherAuthView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if not getattr(settings, "PUSHER_ENABLED", False):
            return Response({"detail": "Pusher no está habilitado."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        channel_name = request.data.get("channel_name", "")
        socket_id = request.data.get("socket_id", "")
        expected_channel = f"private-user-{request.user.id}"
        if channel_name != expected_channel or not socket_id:
            return Response({"detail": "Canal no autorizado."}, status=status.HTTP_403_FORBIDDEN)

        client = pusher.Pusher(**settings.PUSHER_CONFIG)
        return JsonResponse(client.authenticate(channel=channel_name, socket_id=socket_id))
