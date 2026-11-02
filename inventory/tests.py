
from datetime import date, timedelta
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from .models import BloodInventory, Donation


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


class InventoryPaginationTests(TestCase):

    def setUp(self):
        self.donation = Donation.objects.create(
            donor_id=self.create_donor().pk,
            donation_date=__import__("django").utils.timezone.now(),
            blood_group="O+",
            quantity_ml=450,
            screening_status="Passed",
            donation_status="Accepted",
        )

        for number in range(25):
            BloodInventory.objects.create(
                donation=self.donation,
                blood_group="O+",
                quantity_ml=450,
                available_ml=450,
                collection_date=date.today(),
                expiry_date=date.today() + timedelta(days=42),
                status="Available",
                storage_location=f"Storage {number}",
            )

    def create_donor(self):
        from donors.models import Donor

        return Donor.objects.create(
            full_name="Test Donor",
            date_of_birth=date(1995, 1, 1),
            phone_number="9876543210",
            email="testdonor@example.com",
            address="Test Address",
            blood_group="O+",
        )

    def test_inventory_first_page_shows_20_records(self):
        response = self.client.get(reverse("inventory_list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["inventory"]), 20)
        self.assertEqual(
            response.context["inventory"].paginator.count,
            25,
        )

    def test_inventory_second_page_shows_remaining_records(self):
        response = self.client.get(
            reverse("inventory_list"),
            {"page": 2},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["inventory"]), 5)
        self.assertEqual(response.context["inventory"].number, 2)

    def test_inventory_search_filter_is_preserved(self):
        response = self.client.get(
            reverse("inventory_list"),
            {"q": "Storage 1", "page": 1},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["search_query"],
            "Storage 1",
        )
        self.assertEqual(
            response.context["inventory"].paginator.count,
            11,
        )

    def test_invalid_page_number_returns_valid_page(self):
        response = self.client.get(
            reverse("inventory_list"),
            {"page": "invalid"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["inventory"].number, 1)
