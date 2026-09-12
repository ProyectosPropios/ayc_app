from django.test import TestCase

# Create your tests here.


class HealthCheckTests(TestCase):
    def test_health_check_accepts_get(self):
        response = self.client.get("/health/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_health_check_rejects_non_get_requests(self):
        response = self.client.post("/health/")

        self.assertEqual(response.status_code, 405)
