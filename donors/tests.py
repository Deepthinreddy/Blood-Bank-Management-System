from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Donor


class DonorRegistrationTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.staff = user_model.objects.create_user(
            username="bloodbankstaff",
            password="test-password",
            is_staff=True,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.staff)

        self.url = "/api/donors/"
        self.list_url = "/api/donors/list/"

        self.valid_payload = {
            "full_name": "Asha Rao",
            "date_of_birth": "2000-04-12",
            "phone_number": "+91 9876543210",
            "email": "asha@example.com",
            "address": "Bengaluru, Karnataka",
            "blood_group": "O+",
        }

    # --------------------------------------------------
    # DONOR REGISTRATION TESTS
    # --------------------------------------------------

    def test_staff_can_register_donor(self):
        response = self.client.post(
            self.url,
            self.valid_payload,
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Donor.objects.count(), 1)
        self.assertEqual(Donor.objects.get().blood_group, "O+")
        self.assertIn("id", response.data)

    def test_required_fields_are_validated(self):
        payload = self.valid_payload.copy()
        payload.pop("full_name")

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("full_name", response.data)
        self.assertEqual(Donor.objects.count(), 0)

    def test_invalid_blood_group_is_rejected(self):
        payload = self.valid_payload.copy()
        payload["blood_group"] = "X+"

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("blood_group", response.data)
        self.assertEqual(Donor.objects.count(), 0)

    def test_future_date_of_birth_is_rejected(self):
        payload = self.valid_payload.copy()
        payload["date_of_birth"] = (
            date.today() + timedelta(days=1)
        ).isoformat()

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("date_of_birth", response.data)

    def test_non_staff_user_is_forbidden(self):
        user = get_user_model().objects.create_user(
            username="regularuser",
            password="test-password",
            is_staff=False,
        )
        self.client.force_authenticate(user=user)

        response = self.client.post(
            self.url,
            self.valid_payload,
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Donor.objects.count(), 0)

    def test_anonymous_user_is_rejected(self):
        self.client.force_authenticate(user=None)

        response = self.client.post(
            self.url,
            self.valid_payload,
            format="json",
        )

        self.assertIn(response.status_code, (401, 403))
        self.assertEqual(Donor.objects.count(), 0)

    # --------------------------------------------------
    # DONOR LIST AND SEARCH TESTS
    # --------------------------------------------------

    def test_staff_can_list_donors(self):
        self.client.post(
            self.url,
            self.valid_payload,
            format="json",
        )

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["full_name"], "Asha Rao")

    def test_staff_can_search_donors_by_name(self):
        self.client.post(
            self.url,
            self.valid_payload,
            format="json",
        )

        response = self.client.get(
            self.list_url,
            {"name": "Asha"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["full_name"], "Asha Rao")

    def test_staff_can_filter_donors_by_blood_group(self):
        self.client.post(
            self.url,
            self.valid_payload,
            format="json",
        )

        response = self.client.get(
            self.list_url,
            {"blood_group": "O+"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    # --------------------------------------------------
    # DONOR DETAIL TESTS
    # --------------------------------------------------

    def test_staff_can_view_donor_detail(self):
        self.client.post(
            self.url,
            self.valid_payload,
            format="json",
        )
        donor = Donor.objects.get()

        response = self.client.get(
            f"/api/donors/{donor.id}/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["full_name"], "Asha Rao")

    def test_staff_gets_404_for_missing_donor(self):
        response = self.client.get("/api/donors/99999/")

        self.assertEqual(response.status_code, 404)

    # --------------------------------------------------
    # DONOR UPDATE TESTS
    # --------------------------------------------------

    def test_staff_can_update_donor(self):
        self.client.post(
            self.url,
            self.valid_payload,
            format="json",
        )
        donor = Donor.objects.get()

        response = self.client.patch(
            f"/api/donors/{donor.id}/update/",
            {"address": "Updated address"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        donor.refresh_from_db()
        self.assertEqual(donor.address, "Updated address")

    # --------------------------------------------------
    # ACCESS CONTROL TESTS
    # --------------------------------------------------

    def test_non_staff_cannot_list_donors(self):
        user = get_user_model().objects.create_user(
            username="regularuser2",
            password="test-password",
            is_staff=False,
        )
        self.client.force_authenticate(user=user)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 403)