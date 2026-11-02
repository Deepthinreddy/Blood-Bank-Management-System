
from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from . import services
from .models import (
    BloodAllocation,
    BloodIssue,
    BloodRequest,
    BloodUnit,
    Recipient,
)
from .serializers import BloodRequestSerializer
from .services import (
    AllocationError,
    IssueError,
    RequestProcessingError,
    allocate_blood,
    issue_blood,
    process_blood_request,
)


class BloodWorkflowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="staff",
            password="test-password",
            is_staff=True,
        )
        self.request = BloodRequest.objects.create(
            recipient_name="John Doe",
            blood_group="A+",
            units_requested=2,
        )

    def test_staff_can_track_all_six_request_statuses(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        statuses = [
            BloodRequest.Status.PENDING,
            BloodRequest.Status.APPROVED,
            BloodRequest.Status.REJECTED,
            BloodRequest.Status.ALLOCATED,
            BloodRequest.Status.FULFILLED,
            BloodRequest.Status.CANCELLED,
        ]

        for request_status in statuses:
            self.request.status = request_status
            self.request.save(update_fields=["status"])

            response = client.get(
                f"/api/requests/{self.request.id}/status/"
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["status"], request_status)
            self.assertEqual(response.data["request_id"], self.request.id)

    def test_non_staff_cannot_track_request_status(self):
        user = get_user_model().objects.create_user(
            username="ordinarytracker",
            password="test-password",
            is_staff=False,
        )

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get(
            f"/api/requests/{self.request.id}/status/"
        )

        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_cannot_track_request_status(self):
        client = APIClient()

        response = client.get(
            f"/api/requests/{self.request.id}/status/"
        )

        self.assertIn(response.status_code, (401, 403))

    def test_tracking_nonexistent_request_returns_404(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        response = client.get("/api/requests/99999/status/")

        self.assertEqual(response.status_code, 404)

    def test_valid_blood_request_data_is_accepted(self):
        data = {
            "recipient_name": "John Doe",
            "blood_group": "A+",
            "units_requested": 2,
        }

        serializer = BloodRequestSerializer(data=data)

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_empty_recipient_name_is_rejected(self):
        data = {
            "recipient_name": "   ",
            "blood_group": "A+",
            "units_requested": 1,
        }

        serializer = BloodRequestSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("recipient_name", serializer.errors)

    def test_invalid_blood_group_is_rejected(self):
        data = {
            "recipient_name": "John Doe",
            "blood_group": "XYZ",
            "units_requested": 1,
        }

        serializer = BloodRequestSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("blood_group", serializer.errors)

    def test_zero_units_are_rejected(self):
        data = {
            "recipient_name": "John Doe",
            "blood_group": "A+",
            "units_requested": 0,
        }

        serializer = BloodRequestSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("units_requested", serializer.errors)

    def test_missing_required_fields_are_rejected(self):
        serializer = BloodRequestSerializer(data={})

        self.assertFalse(serializer.is_valid())
        self.assertIn("recipient_name", serializer.errors)
        self.assertIn("blood_group", serializer.errors)
        self.assertIn("units_requested", serializer.errors)

    def test_staff_can_create_valid_blood_request(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        data = {
            "recipient_name": "Jane Doe",
            "blood_group": "O+",
            "units_requested": 2,
        }

        response = client.post(
            "/api/requests/create/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["recipient_name"], "Jane Doe")

    def test_invalid_blood_request_returns_validation_errors(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        data = {
            "recipient_name": " ",
            "blood_group": "XYZ",
            "units_requested": 0,
        }

        response = client.post(
            "/api/requests/create/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("recipient_name", response.data)
        self.assertIn("blood_group", response.data)
        self.assertIn("units_requested", response.data)

    def test_non_staff_cannot_create_blood_request(self):
        user = get_user_model().objects.create_user(
            username="ordinarycreator",
            password="test-password",
            is_staff=False,
        )

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post(
            "/api/requests/create/",
            {
                "recipient_name": "Jane Doe",
                "blood_group": "O+",
                "units_requested": 1,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)


class RecipientManagementTests(TestCase):
    def setUp(self):
        self.staff = get_user_model().objects.create_user(
            username="recipientstaff",
            password="test-password",
            is_staff=True,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.staff)

        self.recipient = Recipient.objects.create(
            full_name="John Doe",
            identification_number="ID12345",
            contact_number="9876543210",
            blood_group="A+",
            notes="Regular donor",
        )

    def test_staff_can_list_recipients(self):
        response = self.client.get("/api/recipients/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["full_name"], "John Doe")

    def test_staff_can_search_recipients(self):
        response = self.client.get("/api/recipients/?search=ID12345")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_staff_can_view_recipient_details(self):
        response = self.client.get(
            f"/api/recipients/{self.recipient.id}/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["full_name"], "John Doe")

    def test_staff_can_update_recipient(self):
        response = self.client.put(
            f"/api/recipients/{self.recipient.id}/",
            {
                "full_name": "Jane Doe",
                "identification_number": "ID12345",
                "contact_number": "9876543210",
                "blood_group": "B+",
                "notes": "Updated record",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.recipient.refresh_from_db()
        self.assertEqual(self.recipient.full_name, "Jane Doe")
        self.assertEqual(self.recipient.blood_group, "B+")

    def test_staff_can_partially_update_recipient(self):
        response = self.client.patch(
            f"/api/recipients/{self.recipient.id}/",
            {"contact_number": "9999999999"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.recipient.refresh_from_db()
        self.assertEqual(self.recipient.contact_number, "9999999999")

    def test_non_staff_cannot_manage_recipients(self):
        user = get_user_model().objects.create_user(
            username="ordinaryrecipientuser",
            password="test-password",
            is_staff=False,
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/recipients/")

        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_cannot_manage_recipients(self):
        client = APIClient()
        response = client.get("/api/recipients/")

        self.assertIn(response.status_code, (401, 403))

    def test_missing_recipient_returns_404(self):
        response = self.client.get("/api/recipients/99999/")

        self.assertEqual(response.status_code, 404)
