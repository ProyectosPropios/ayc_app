from django.test import TestCase
from django.test.utils import override_settings
from rest_framework.test import APIClient

from .models import User


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            password="Admin123!",
            first_name="Admin",
        )
        self.technician = User.objects.create_user(
            email="tecnico@example.com",
            password="Tecnico123!",
            first_name="Carlos",
            role=User.Role.TECHNICIAN,
        )

    def test_login_uses_email_and_sets_cookies(self):
        response = self.client.post(
            "/api/auth/login/",
            {"email": "tecnico@example.com", "password": "Tecnico123!"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.cookies)
        self.assertEqual(response.data["user"]["role"], User.Role.TECHNICIAN)

    def test_technician_cannot_manage_technicians(self):
        self.client.force_authenticate(self.technician)
        response = self.client.get("/api/auth/technicians/")
        self.assertEqual(response.status_code, 403)

    def test_admin_can_manage_technicians(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get("/api/auth/technicians/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_admin_creates_technician_and_sends_credentials(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            "/api/auth/technicians/",
            {
                "email": "nuevo@example.com",
                "first_name": "Nuevo",
                "last_name": "Tecnico",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(email="nuevo@example.com").exists())
        from django.core import mail

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Contraseña temporal", mail.outbox[0].body)

    def test_user_can_read_and_update_own_profile(self):
        self.client.force_authenticate(self.technician)
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], self.technician.email)

        response = self.client.patch(
            "/api/auth/me/",
            {"first_name": "Carlos Actualizado"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.technician.refresh_from_db()
        self.assertEqual(self.technician.first_name, "Carlos Actualizado")

    def test_profile_rejects_numbers_in_names(self):
        self.client.force_authenticate(self.technician)
        response = self.client.patch(
            "/api/auth/me/",
            {"first_name": "Carlos123"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_user_can_change_password(self):
        self.client.force_authenticate(self.technician)
        response = self.client.post(
            "/api/auth/change-password/",
            {
                "current_password": "Tecnico123!",
                "new_password": "NuevaTecnico456!",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.technician.refresh_from_db()
        self.assertTrue(self.technician.check_password("NuevaTecnico456!"))
