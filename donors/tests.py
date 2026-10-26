from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Donor


class DonorRegistrationTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.staff = user_model.objects.create_user(
            username="bloodbankstaff", password="test-password", is_staff=True
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.staff)
        self.url = "/api/donors/"
        self.valid_payload = {
            "full_name": "Asha Rao",
            "date_of_birth": "2000-04-12",
            "phone_number": "+91 9876543210",
            "email": "asha@example.com",
            "address": "Bengaluru, Karnataka",
            "blood_group": "O+",
        }

    def test_staff_can_register_donor(self):
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Donor.objects.count(), 1)
        self.assertEqual(Donor.objects.get().blood_group, "O+")
        self.assertIn("id", response.data)

    def test_required_fields_are_validated(self):
        payload = self.valid_payload.copy()
        payload.pop("full_name")
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("full_name", response.data)
        self.assertEqual(Donor.objects.count(), 0)

    def test_invalid_blood_group_is_rejected(self):
        payload = self.valid_payload.copy()
        payload["blood_group"] = "X+"
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("blood_group", response.data)
        self.assertEqual(Donor.objects.count(), 0)

    def test_future_date_of_birth_is_rejected(self):
        payload = self.valid_payload.copy()
        payload["date_of_birth"] = (date.today() + timedelta(days=1)).isoformat()
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("date_of_birth", response.data)

    def test_non_staff_user_is_forbidden(self):
        user = get_user_model().objects.create_user(
            username="regularuser", password="test-password", is_staff=False
        )
        self.client.force_authenticate(user=user)
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Donor.objects.count(), 0)

    def test_anonymous_user_is_rejected(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertIn(response.status_code, (401, 403))
        self.assertEqual(Donor.objects.count(), 0)
