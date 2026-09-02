from django.core import mail
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from customer.models import Customer
from users.models import User
from workorder.models import WorkOrder

from .models import PumpingReport


class PumpingReportTests(TestCase):
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
            last_name="Gomez",
        )
        self.customer = Customer.objects.create(
            name="Empresa Cliente",
            email="cliente@example.com",
            phone="3001234567",
            address="Calle 10 # 20-30",
            city="Bogota",
            created_by=self.admin,
        )
        self.order = WorkOrder.objects.create(
            title="Mantenimiento de bombas",
            description="Mantenimiento preventivo del sistema de bombeo.",
            customer=self.customer,
            technician=self.technician,
            created_by=self.admin,
            scheduled_date="2030-05-20",
        )

    def report_payload(self):
        return {
            "work_order": self.order.id,
            "report_date": "2030-05-20",
            "attention": "Carlos Gómez",
            "equipment_rows": [
                {
                    "pressure": "80 PSI",
                    "submersibles": "2",
                    "hp_measure": "5 HP",
                    "hp_plate": "5 HP",
                    "amperage_measure": "12 A",
                    "amperage_plate": "13 A",
                    "temperature": "normal",
                    "noises": "normal",
                    "humidity": "no",
                    "electrical_connections": "normal",
                }
            ],
            "hydropneumatic_tank_brand": "IHM",
            "hydropneumatic_tank_determined_charge": "40 PSI",
            "hydropneumatic_tank_measured_charge": "40 PSI",
            "speed_controller_brand": "ABB",
            "observations": "El sistema queda operativo.",
        }

    def test_report_has_fields_and_pdf_endpoint(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            "/api/pumping-reports/", self.report_payload(), format="json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["equipment_rows"][0]["temperature"], "normal")

        pdf_response = self.client.get(
            f"/api/pumping-reports/{response.data['id']}/pdf/"
        )
        self.assertEqual(pdf_response.status_code, 200)
        self.assertEqual(pdf_response["Content-Type"], "application/pdf")
        self.assertTrue(pdf_response.content.startswith(b"%PDF"))

    def test_only_defined_equipment_options_are_accepted(self):
        self.client.force_authenticate(self.admin)
        payload = self.report_payload()
        payload["equipment_rows"][0]["temperature"] = "caliente"
        response = self.client.post("/api/pumping-reports/", payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("equipment_rows", response.data)

    def test_completed_report_requires_signature(self):
        self.client.force_authenticate(self.admin)
        payload = self.report_payload()
        payload["status"] = PumpingReport.ReportStatus.COMPLETED
        response = self.client.post("/api/pumping-reports/", payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("status", response.data)

    def test_technician_can_only_create_for_assigned_order(self):
        self.client.force_authenticate(self.technician)
        response = self.client.post(
            "/api/pumping-reports/", self.report_payload(), format="json"
        )
        self.assertEqual(response.status_code, 201)

        other_order = WorkOrder.objects.create(
            title="Otra orden",
            description="Otra orden.",
            customer=self.customer,
            technician=self.admin,
            created_by=self.admin,
            scheduled_date="2030-05-21",
        )
        payload = self.report_payload()
        payload["work_order"] = other_order.id
        response = self.client.post("/api/pumping-reports/", payload, format="json")
        self.assertEqual(response.status_code, 403)

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="no-reply@example.com",
    )
    def test_completed_report_is_emailed_automatically_with_pdf(self):
        self.client.force_authenticate(self.admin)
        payload = self.report_payload()
        payload.update(
            {
                "status": PumpingReport.ReportStatus.COMPLETED,
                "technician_signature": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4z8DwHwAFgAI/ScK9WQAAAABJRU5ErkJggg==",
            }
        )
        create_response = self.client.post(
            "/api/pumping-reports/", payload, format="json"
        )
        self.assertEqual(create_response.status_code, 201)
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(mail.outbox[0].attachments[0][0].endswith("-bombeo.pdf"))
        self.assertEqual(mail.outbox[0].attachments[0][2], "application/pdf")
