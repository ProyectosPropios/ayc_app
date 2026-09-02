from django.core import mail
from django.test import TestCase
from django.test import override_settings
from rest_framework.test import APIClient

from customer.models import Customer
from users.models import User
from workorder.models import WorkOrder

from .models import ElectricalReport


class ElectricalReportTests(TestCase):
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
            title="Mantenimiento de planta",
            description="Mantenimiento preventivo.",
            customer=self.customer,
            technician=self.technician,
            created_by=self.admin,
            scheduled_date="2030-05-20",
        )

    def report_payload(self):
        payload = {
            "work_order": self.order.id,
            "report_date": "2030-05-20",
            "responsible_name": "Encargado Cliente",
            "generator": "Generador diesel",
            "brand": "Marca",
            "kva": "100",
            "motor": "Motor diesel",
            "model_name": "Modelo X",
            "serial_number": "SER-001",
            "general_observations": "Equipo revisado.",
            "received_by": "Recibido Cliente",
        }
        for key, _ in ElectricalReport.INSPECTION_DEFINITIONS:
            payload[f"{key}_status"] = "OK"
            payload[f"{key}_observation"] = "Correcto"
        return payload

    def test_report_has_all_24_inspection_rows_and_pdf_endpoint(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            "/api/electrical-reports/",
            self.report_payload(),
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data["inspection_items"]), 24)
        self.assertEqual(response.data["inspection_items"][0]["status"], "OK")

        pdf_response = self.client.get(
            f"/api/electrical-reports/{response.data['id']}/pdf/"
        )
        self.assertEqual(pdf_response.status_code, 200)
        self.assertEqual(pdf_response["Content-Type"], "application/pdf")
        self.assertTrue(pdf_response.content.startswith(b"%PDF"))

    def test_only_ok_or_no_are_accepted(self):
        self.client.force_authenticate(self.admin)
        payload = self.report_payload()
        payload["oil_level_status"] = "BIEN"
        response = self.client.post("/api/electrical-reports/", payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("oil_level_status", response.data)

    def test_completed_report_requires_both_signatures(self):
        self.client.force_authenticate(self.admin)
        create_response = self.client.post(
            "/api/electrical-reports/",
            self.report_payload(),
            format="json",
        )
        report_url = f"/api/electrical-reports/{create_response.data['id']}/"
        response = self.client.patch(
            report_url,
            {"status": "terminado"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("status", response.data)

    def test_technician_can_only_access_report_from_assigned_order(self):
        self.client.force_authenticate(self.technician)
        response = self.client.post(
            "/api/electrical-reports/",
            self.report_payload(),
            format="json",
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
        response = self.client.post("/api/electrical-reports/", payload, format="json")
        self.assertEqual(response.status_code, 403)

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="no-reply@example.com",
    )
    def test_completed_report_is_emailed_automatically_with_pdf(self):
        self.client.force_authenticate(self.admin)
        payload = self.report_payload()
        signature = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4z8DwHwAFgAI/ScK9WQAAAABJRU5ErkJggg=="
        payload.update(
            {
                "status": "terminado",
                "technician_signature": signature,
                "recipient_signature": signature,
            }
        )
        create_response = self.client.post(
            "/api/electrical-reports/", payload, format="json"
        )
        self.assertEqual(create_response.status_code, 201)
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(
            mail.outbox[0].attachments[0][0].endswith("-planta-electrica.pdf")
        )
        self.assertEqual(mail.outbox[0].attachments[0][2], "application/pdf")
