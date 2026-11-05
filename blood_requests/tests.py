
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


class BloodRequestFrontendTests(TestCase):
    def setUp(self):
        self.staff = get_user_model().objects.create_user(
            username="request_frontend_staff",
            password="RequestFrontendPass123!",
            is_staff=True,
        )
        self.client.force_login(self.staff)

    def test_request_and_recipient_pages_render(self):
        blood_request = BloodRequest.objects.create(
            recipient_name="Listed Recipient",
            blood_group="A+",
            units_requested=1,
        )
        response = self.client.get("/requests/")
        recipient_response = self.client.get("/requests/recipients/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Listed Recipient")
        self.assertContains(response, blood_request.get_status_display())
        self.assertEqual(recipient_response.status_code, 200)

    def test_request_can_be_created_from_frontend(self):
        response = self.client.post(
            "/requests/",
            {
                "recipient_name": "Frontend Recipient",
                "blood_group": "A+",
                "units_requested": 2,
            },
        )

        self.assertRedirects(response, "/requests/")
        self.assertTrue(
            BloodRequest.objects.filter(
                recipient_name="Frontend Recipient",
                status=BloodRequest.Status.PENDING,
            ).exists()
        )

    def test_request_processing_uses_existing_workflow(self):
        blood_request = BloodRequest.objects.create(
            recipient_name="Pending Recipient",
            blood_group="O+",
            units_requested=1,
        )

        response = self.client.post(
            f"/requests/{blood_request.pk}/process/",
            {"decision": BloodRequest.Status.APPROVED},
        )

        self.assertRedirects(response, "/requests/")
        blood_request.refresh_from_db()
        self.assertEqual(blood_request.status, BloodRequest.Status.APPROVED)

    def test_recipient_management_page_registers_existing_model(self):
        response = self.client.post(
            "/requests/recipients/",
            {
                "full_name": "Frontend Recipient",
                "identification_number": "FRONTEND-001",
                "contact_number": "9876543210",
                "blood_group": "B+",
                "notes": "Registered from UI",
            },
        )

        self.assertRedirects(response, "/requests/recipients/")
        self.assertTrue(
            Recipient.objects.filter(
                identification_number="FRONTEND-001"
            ).exists()
        )


class BloodRequestServiceCoverageTests(TestCase):

    def setUp(self):
        self.staff = get_user_model().objects.create_user(
            username="service_test_staff",
            password="test-password",
            is_staff=True,
        )

    def create_request(self, **kwargs):
        defaults = {
            "recipient_name": "Service Test Recipient",
            "blood_group": "A+",
            "units_requested": 1,
            "status": BloodRequest.Status.APPROVED,
        }
        defaults.update(kwargs)
        return BloodRequest.objects.create(**defaults)

    def create_unit(self, **kwargs):
        defaults = {
            "blood_group": "A+",
            "expires_on": timezone.localdate() + timedelta(days=10),
            "status": BloodUnit.Status.AVAILABLE,
        }
        defaults.update(kwargs)
        return BloodUnit.objects.create(**defaults)

    def create_allocation(self, **kwargs):
        blood_request = kwargs.pop(
            "request",
            self.create_request(),
        )
        unit = kwargs.pop("blood_unit", self.create_unit(
            status=BloodUnit.Status.ALLOCATED,
        ))
        return BloodAllocation.objects.create(
            request=blood_request,
            blood_unit=unit,
            **kwargs,
        )

    def test_allocate_rejects_non_approved_request(self):
        blood_request = self.create_request(
            status=BloodRequest.Status.PENDING,
        )

        with self.assertRaises(AllocationError):
            allocate_blood(blood_request.pk)

    def test_allocate_rejects_zero_requested_units(self):
        blood_request = self.create_request(units_requested=0)

        with self.assertRaises(AllocationError):
            allocate_blood(blood_request.pk)

    def test_allocate_rejects_missing_compatibility_rule(self):
        blood_request = self.create_request()

        with self.assertRaises(AllocationError):
            allocate_blood(blood_request.pk)

    def test_allocate_rejects_insufficient_stock(self):
        blood_request = self.create_request(units_requested=2)
        self.create_unit()

        with patch.dict(
            services.BLOOD_COMPATIBILITY,
            {"A+": ["A+", "O+"]},
        ):
            with self.assertRaises(AllocationError):
                allocate_blood(blood_request.pk)

    def test_allocate_rejects_expired_or_unavailable_stock(self):
        blood_request = self.create_request()

        self.create_unit(
            expires_on=timezone.localdate() - timedelta(days=1),
        )
        self.create_unit(
            status=BloodUnit.Status.ALLOCATED,
        )

        with patch.dict(
            services.BLOOD_COMPATIBILITY,
            {"A+": ["A+"]},
        ):
            with self.assertRaises(AllocationError):
                allocate_blood(blood_request.pk)

    def test_allocate_successfully_allocates_compatible_units(self):
        blood_request = self.create_request(units_requested=2)
        first_unit = self.create_unit(
            expires_on=timezone.localdate() + timedelta(days=5),
        )
        second_unit = self.create_unit(
            expires_on=timezone.localdate() + timedelta(days=10),
        )

        with patch.dict(
            services.BLOOD_COMPATIBILITY,
            {"A+": ["A+", "O+"]},
        ):
            allocations = allocate_blood(blood_request.pk)

        self.assertEqual(len(allocations), 2)

        blood_request.refresh_from_db()
        first_unit.refresh_from_db()
        second_unit.refresh_from_db()

        self.assertEqual(
            blood_request.status,
            BloodRequest.Status.ALLOCATED,
        )
        self.assertEqual(
            first_unit.status,
            BloodUnit.Status.ALLOCATED,
        )
        self.assertEqual(
            second_unit.status,
            BloodUnit.Status.ALLOCATED,
        )

    def test_issue_rejects_non_allocated_allocation(self):
        allocation = self.create_allocation(
            status=BloodAllocation.Status.CANCELLED,
        )

        with self.assertRaises(IssueError):
            issue_blood(allocation.pk, self.staff)

    def test_issue_rejects_unit_that_is_not_allocated(self):
        unit = self.create_unit(
            status=BloodUnit.Status.AVAILABLE,
        )
        allocation = self.create_allocation(blood_unit=unit)

        with self.assertRaises(IssueError):
            issue_blood(allocation.pk, self.staff)

    def test_issue_rejects_expired_unit(self):
        unit = self.create_unit(
            status=BloodUnit.Status.ALLOCATED,
            expires_on=timezone.localdate() - timedelta(days=1),
        )
        allocation = self.create_allocation(blood_unit=unit)

        with self.assertRaises(IssueError):
            issue_blood(allocation.pk, self.staff)

    def test_issue_keeps_request_allocated_when_other_units_remain(self):
        blood_request = self.create_request()

        first_allocation = self.create_allocation(
            request=blood_request,
        )
        self.create_allocation(request=blood_request)

        issue = issue_blood(first_allocation.pk, self.staff)

        first_allocation.refresh_from_db()
        blood_request.refresh_from_db()

        self.assertTrue(
            BloodIssue.objects.filter(pk=issue.pk).exists()
        )
        self.assertEqual(
            first_allocation.status,
            BloodAllocation.Status.ISSUED,
        )
        self.assertEqual(
            blood_request.status,
            BloodRequest.Status.APPROVED,
        )

    def test_issue_fulfills_request_when_all_allocations_are_issued(self):
        blood_request = self.create_request()
        allocation = self.create_allocation(request=blood_request)

        issue = issue_blood(allocation.pk, self.staff)

        allocation.refresh_from_db()
        blood_request.refresh_from_db()

        self.assertTrue(
            BloodIssue.objects.filter(pk=issue.pk).exists()
        )
        self.assertEqual(
            allocation.status,
            BloodAllocation.Status.ISSUED,
        )
        self.assertEqual(
            blood_request.status,
            BloodRequest.Status.FULFILLED,
        )

    def test_process_rejects_invalid_decision(self):
        blood_request = self.create_request(
            status=BloodRequest.Status.PENDING,
        )

        with self.assertRaises(RequestProcessingError):
            process_blood_request(blood_request.pk, "INVALID")

    def test_process_rejects_non_pending_request(self):
        blood_request = self.create_request(
            status=BloodRequest.Status.APPROVED,
        )

        with self.assertRaises(RequestProcessingError):
            process_blood_request(
                blood_request.pk,
                BloodRequest.Status.REJECTED,
            )

    def test_process_approves_pending_request(self):
        blood_request = self.create_request(
            status=BloodRequest.Status.PENDING,
        )

        result = process_blood_request(
            blood_request.pk,
            BloodRequest.Status.APPROVED,
        )

        self.assertEqual(
            result.status,
            BloodRequest.Status.APPROVED,
        )

    def test_process_rejects_pending_request(self):
        blood_request = self.create_request(
            status=BloodRequest.Status.PENDING,
        )

        result = process_blood_request(
            blood_request.pk,
            BloodRequest.Status.REJECTED,
        )

        self.assertEqual(
            result.status,
            BloodRequest.Status.REJECTED,
        )
