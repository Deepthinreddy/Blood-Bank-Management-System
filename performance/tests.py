import time

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from donors.models import Donor


User = get_user_model()


class ResponseTimeTests(TestCase):
    """
    Basic response-time measurements for dashboard and donor search.

    These are application-level measurements, not a substitute for
    a concurrent load test against a running server.
    """

    TARGET_SECONDS = 2.0
    REQUEST_COUNT = 30

    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.create_user(
            username="performance_admin",
            password="TestPass123!",
            role="ADMIN",
            is_active=True,
        )

        cls.staff_user = User.objects.create_user(
            username="performance_staff",
            password="TestPass123!",
            is_staff=True,
            is_active=True,
        )

        Donor.objects.create(
            full_name="Performance Test Donor",
            date_of_birth="2000-04-12",
            phone_number="+919876543210",
            email="performance@example.com",
            address="Bengaluru",
            blood_group="O+",
        )

    def measure_requests(self, url, client, params=None):
        durations = []

        # Warm up the endpoint before recording timings.
        response = client.get(url, params or {})
        self.assertEqual(response.status_code, 200)

        for _ in range(self.REQUEST_COUNT):
            start = time.perf_counter()
            response = client.get(url, params or {})
            elapsed = time.perf_counter() - start

            self.assertEqual(response.status_code, 200)
            durations.append(elapsed)

        durations.sort()
        percentile_index = int(0.90 * len(durations)) - 1
        percentile_90 = durations[max(0, percentile_index)]

        print(
            f"\n{url}: "
            f"p90={percentile_90:.4f}s, "
            f"max={max(durations):.4f}s"
        )

        return durations, percentile_90

    def test_dashboard_response_time(self):
        self.client.force_login(self.admin_user)

        _, percentile_90 = self.measure_requests(
            reverse("admin_dashboard"),
            self.client,
        )

        self.assertLessEqual(
            percentile_90,
            self.TARGET_SECONDS,
            "Dashboard p90 response time exceeded two seconds.",
        )

    def test_donor_search_response_time(self):
        from rest_framework.test import APIClient

        client = APIClient()
        client.force_authenticate(user=self.staff_user)

        _, percentile_90 = self.measure_requests(
            reverse("donor-list"),
            client,
            {"name": "Performance"},
        )

        self.assertLessEqual(
            percentile_90,
            self.TARGET_SECONDS,
            "Donor search p90 response time exceeded two seconds.",
        )