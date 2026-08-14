from django.test import TestCase
from rest_framework.test import APIClient

from customer.models import Customer
from notification.models import Notification
from users.models import User


class WorkOrderTests(TestCase):
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
        self.customer = Customer.objects.create(
            name="Cliente de Prueba",
            email="cliente@example.com",
            phone="3001234567",
            address="Calle 10 # 20-30",
            city="Bogotá",
            created_by=self.admin,
        )
        self.payload = {
            "title": "Mantenimiento preventivo",
            "description": "Revisar el sistema de bombeo.",
            "customer": self.customer.id,
            "technician": self.technician.id,
            "scheduled_date": "2030-05-20",
            "scheduled_time": "08:30:00",
            "service_address": "Calle 10 # 20-30",
            "priority": "alta",
            "notes": "Llevar repuestos.",
        }

    def test_admin_can_create_and_assign_work_order(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post("/api/work-orders/", self.payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "asignado")
        self.assertTrue(response.data["code"].startswith("OT-"))
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.technician,
                notification_type=Notification.Type.WORK_ORDER_ASSIGNED,
            ).exists()
        )

    def test_technician_only_sees_assigned_work_orders(self):
        self.client.force_authenticate(self.admin)
        self.client.post("/api/work-orders/", self.payload, format="json")
        self.client.force_authenticate(self.technician)
        response = self.client.get("/api/work-orders/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_technician_can_change_status(self):
        self.client.force_authenticate(self.admin)
        create_response = self.client.post("/api/work-orders/", self.payload, format="json")
        order_url = f"/api/work-orders/{create_response.data['id']}/"
        self.client.force_authenticate(self.technician)
        response = self.client.patch(order_url, {"status": "en_labor"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "en_labor")
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.admin,
                notification_type=Notification.Type.WORK_ORDER_STATUS,
            ).exists()
        )

    def test_technician_cannot_create_work_orders(self):
        self.client.force_authenticate(self.technician)
        response = self.client.post("/api/work-orders/", self.payload, format="json")
        self.assertEqual(response.status_code, 403)

    def test_daily_task_notifies_pending_orders_once(self):
        from datetime import date

        from .tasks import enviar_recordatorio_trabajos_dia

        self.payload["scheduled_date"] = date.today().isoformat()
        self.client.force_authenticate(self.admin)
        self.client.post("/api/work-orders/", self.payload, format="json")

        # La asignación ya crea una notificación; el recordatorio no duplica la de hoy.
        sent = enviar_recordatorio_trabajos_dia()
        self.assertEqual(sent, 0)
