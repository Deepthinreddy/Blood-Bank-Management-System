from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch


class HealthCheckTests(TestCase):

    def test_health_check_success(self):
        response = self.client.get("/health/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")
        self.assertEqual(response.json()["database"], "connected")

    @patch("config.health.connection.cursor")
    def test_health_check_database_failure(self, mock_cursor):
        mock_cursor.side_effect = Exception("Database unavailable")

        response = self.client.get("/health/")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["status"], "unhealthy")
        self.assertEqual(response.json()["database"], "unavailable")