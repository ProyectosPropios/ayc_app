from django.test import TestCase
from rest_framework.test import APIClient

from users.models import User


class CustomerCrudTests(TestCase):
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
        )
        self.payload = {
            "name": "Cliente de Prueba",
            "identification": "900123456",
            "email": "cliente@example.com",
            "phone": "+57 300 123 4567",
            "address": "Calle 10 # 20-30",
            "city": "Bogotá",
            "notes": "Cliente nuevo",
        }

    def test_admin_can_create_and_list_customers(self):
        self.client.force_authenticate(self.admin)
        create_response = self.client.post("/api/customers/", self.payload, format="json")
        self.assertEqual(create_response.status_code, 201)

        list_response = self.client.get("/api/customers/")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.data[0]["name"], "Cliente de Prueba")
        self.assertEqual(list_response.data[0]["created_by_email"], self.admin.email)

    def test_customer_validation_rejects_invalid_data(self):
        self.client.force_authenticate(self.admin)
        invalid_payload = {**self.payload, "name": "Cliente 123", "email": "correo-invalido"}
        response = self.client.post("/api/customers/", invalid_payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("name", response.data)
        self.assertIn("email", response.data)

    def test_technician_cannot_manage_customers(self):
        self.client.force_authenticate(self.technician)
        response = self.client.get("/api/customers/")
        self.assertEqual(response.status_code, 403)
