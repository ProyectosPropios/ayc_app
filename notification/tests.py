from django.test import TestCase
from rest_framework.test import APIClient

from users.models import User

from .models import Notification


class NotificationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="tecnico@example.com",
            password="Tecnico123!",
            first_name="Carlos",
        )
        self.notification = Notification.objects.create(
            recipient=self.user,
            title="Prueba",
            message="Mensaje de prueba",
        )

    def test_user_only_sees_own_notifications_and_can_mark_all_read(self):
        self.client.force_authenticate(self.user)
        response = self.client.get("/api/notifications/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        response = self.client.post("/api/notifications/read-all/")
        self.assertEqual(response.status_code, 200)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)
