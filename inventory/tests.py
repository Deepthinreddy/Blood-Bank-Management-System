
from datetime import date, timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from blood_requests.models import BloodRequest
from donors.models import Donor
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


class UnifiedDashboardTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="dashboard_staff",
            password="DashboardPass123!",
            is_staff=True,
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))

        self.assertRedirects(
            response,
            "/accounts/login/?next=/",
        )

    def test_dashboard_shows_database_totals(self):
        Donor.objects.create(
            full_name="Dashboard Donor",
            date_of_birth=date(1995, 1, 1),
            phone_number="9876543210",
            email="dashboard@example.com",
            address="Bengaluru",
            blood_group="O+",
        )
        BloodRequest.objects.create(
            recipient_name="Dashboard Recipient",
            blood_group="A+",
            units_requested=2,
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_donors"], 1)
        self.assertEqual(response.context["pending_requests"], 1)
        self.assertContains(response, "Dashboard Donor")
        self.assertContains(response, "Dashboard Recipient")

class InventoryFilterAndExpiryTests(TestCase):

    def setUp(self):
        from django.utils import timezone

        self.today = timezone.localdate()

        donor = Donor.objects.create(
            full_name="Inventory Test Donor",
            date_of_birth=date(1995, 1, 1),
            phone_number="9876543210",
            email="inventorytest@example.com",
            address="Bengaluru",
            blood_group="O+",
        )

        self.donation = Donation.objects.create(
            donor=donor,
            donation_date=timezone.now(),
            blood_group="O+",
            quantity_ml=450,
            screening_status="Passed",
            donation_status="Accepted",
        )

    def create_inventory(self, **kwargs):
        defaults = {
            "donation": self.donation,
            "blood_group": "O+",
            "quantity_ml": 450,
            "available_ml": 450,
            "collection_date": self.today,
            "expiry_date": self.today + timedelta(days=42),
            "status": "Available",
            "storage_location": "Main Storage",
        }
        defaults.update(kwargs)
        return BloodInventory.objects.create(**defaults)

    def test_search_by_blood_group(self):
        item = self.create_inventory(blood_group="O+")
        self.create_inventory(blood_group="A+")

        response = self.client.get(
            reverse("inventory_list"),
            {"q": "O+"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["inventory"].object_list),
            [item],
        )

    def test_search_by_storage_location(self):
        item = self.create_inventory(
            storage_location="Emergency Storage",
        )
        self.create_inventory(storage_location="Main Storage")

        response = self.client.get(
            reverse("inventory_list"),
            {"q": "Emergency"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["inventory"].object_list),
            [item],
        )

    def test_valid_status_filter(self):
        item = self.create_inventory(status="Reserved")
        self.create_inventory(status="Available")

        response = self.client.get(
            reverse("inventory_list"),
            {"status": "Reserved"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["selected_status"], "Reserved")
        self.assertEqual(
            list(response.context["inventory"].object_list),
            [item],
        )

    def test_invalid_status_filter_is_ignored(self):
        self.create_inventory(status="Available")
        self.create_inventory(status="Reserved")

        response = self.client.get(
            reverse("inventory_list"),
            {"status": "InvalidStatus"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["selected_status"], "")
        self.assertEqual(
            response.context["inventory"].paginator.count,
            2,
        )

    def test_expiring_filter(self):
        item = self.create_inventory(
            expiry_date=self.today + timedelta(days=3),
        )
        self.create_inventory(
            expiry_date=self.today + timedelta(days=20),
        )

        response = self.client.get(
            reverse("inventory_list"),
            {"expiry": "expiring"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["inventory"].object_list),
            [item],
        )

    def test_expired_filter_updates_old_available_stock(self):
        item = self.create_inventory(
            expiry_date=self.today - timedelta(days=2),
            status="Available",
        )

        response = self.client.get(
            reverse("inventory_list"),
            {"expiry": "expired"},
        )

        item.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(item.status, "Expired")
        self.assertIn(
            item,
            list(response.context["inventory"].object_list),
        )

    def test_valid_filter_excludes_zero_available_stock(self):
        item = self.create_inventory(
            expiry_date=self.today + timedelta(days=15),
            available_ml=300,
        )
        self.create_inventory(
            expiry_date=self.today + timedelta(days=15),
            available_ml=0,
        )

        response = self.client.get(
            reverse("inventory_list"),
            {"expiry": "valid"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["inventory"].object_list),
            [item],
        )

    def test_expiry_labels_are_assigned_correctly(self):
        expired = self.create_inventory(
            expiry_date=self.today - timedelta(days=2),
            status="Discarded",
        )
        expiring = self.create_inventory(
            expiry_date=self.today + timedelta(days=3),
        )
        normal = self.create_inventory(
            expiry_date=self.today + timedelta(days=15),
        )

        response = self.client.get(reverse("inventory_list"))

        self.assertEqual(response.status_code, 200)

        labels = {
            item.pk: item.expiry_label
            for item in response.context["inventory"]
        }

        self.assertEqual(labels[expired.pk], "Expired")
        self.assertEqual(labels[expiring.pk], "Expiring soon")
        self.assertEqual(labels[normal.pk], "Normal")

    def test_unknown_expiry_filter_does_not_filter_inventory(self):
        self.create_inventory()
        self.create_inventory(blood_group="A+")

        response = self.client.get(
            reverse("inventory_list"),
            {"expiry": "unknown"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["inventory"].paginator.count,
            2,
        )
