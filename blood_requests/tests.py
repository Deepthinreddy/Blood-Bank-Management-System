from django.test import TestCase

# Create your tests here.

from datetime import timedelta
from unittest.mock import patch
from rest_framework.test import APIClient

from .serializers import BloodRequestSerializer

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from . import services
from .models import BloodAllocation, BloodIssue, BloodRequest, BloodUnit
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
            username="teststaff",
            password="test-password",
            is_staff=True,
        )
        self.request = BloodRequest.objects.create(
            recipient_name="Test Recipient",
            blood_group="A+",
            units_requested=1,
            status=BloodRequest.Status.APPROVED,
        )
        self.unit = BloodUnit.objects.create(
            blood_group="A+",
            expires_on=timezone.localdate() + timedelta(days=30),
            status=BloodUnit.Status.AVAILABLE,
        )

    @patch.dict(services.BLOOD_COMPATIBILITY, {"A+": ["A+"]})
    def test_allocate_compatible_available_unit(self):
        allocations = allocate_blood(self.request.id)

        self.assertEqual(len(allocations), 1)
        self.unit.refresh_from_db()
        self.request.refresh_from_db()

        self.assertEqual(self.unit.status, BloodUnit.Status.ALLOCATED)
        self.assertEqual(self.request.status, BloodRequest.Status.ALLOCATED)
        self.assertEqual(
            BloodAllocation.objects.filter(request=self.request).count(), 1
        )

    @patch.dict(services.BLOOD_COMPATIBILITY, {"A+": ["A+"]})
    def test_insufficient_stock_does_not_allocate(self):
        self.request.units_requested = 2
        self.request.save(update_fields=["units_requested"])

        with self.assertRaises(AllocationError):
            allocate_blood(self.request.id)

        self.unit.refresh_from_db()
        self.request.refresh_from_db()

        self.assertEqual(self.unit.status, BloodUnit.Status.AVAILABLE)
        self.assertEqual(self.request.status, BloodRequest.Status.APPROVED)
        self.assertEqual(BloodAllocation.objects.count(), 0)

    def test_unconfigured_compatibility_is_rejected(self):
        with patch.dict(services.BLOOD_COMPATIBILITY, {}, clear=True):
            with self.assertRaises(AllocationError):
                allocate_blood(self.request.id)

        self.assertEqual(BloodAllocation.objects.count(), 0)

    def test_issue_updates_inventory_and_fulfills_request(self):
        self.unit.status = BloodUnit.Status.ALLOCATED
        self.unit.save(update_fields=["status"])
        self.request.status = BloodRequest.Status.ALLOCATED
        self.request.save(update_fields=["status"])

        allocation = BloodAllocation.objects.create(
            request=self.request,
            blood_unit=self.unit,
            status=BloodAllocation.Status.ALLOCATED,
        )

        issue = issue_blood(allocation.id, self.user)

        self.assertEqual(issue.allocation_id, allocation.id)
        self.assertEqual(BloodIssue.objects.count(), 1)

        allocation.refresh_from_db()
        self.unit.refresh_from_db()
        self.request.refresh_from_db()

        self.assertEqual(allocation.status, BloodAllocation.Status.ISSUED)
        self.assertEqual(self.unit.status, BloodUnit.Status.ISSUED)
        self.assertEqual(self.request.status, BloodRequest.Status.FULFILLED)

    def test_same_allocation_cannot_be_issued_twice(self):
        self.unit.status = BloodUnit.Status.ALLOCATED
        self.unit.save(update_fields=["status"])
        self.request.status = BloodRequest.Status.ALLOCATED
        self.request.save(update_fields=["status"])

        allocation = BloodAllocation.objects.create(
            request=self.request,
            blood_unit=self.unit,
            status=BloodAllocation.Status.ALLOCATED,
        )

        issue_blood(allocation.id, self.user)

        with self.assertRaises(IssueError):
            issue_blood(allocation.id, self.user)

        self.assertEqual(BloodIssue.objects.count(), 1)

    def test_expired_blood_cannot_be_issued(self):
        self.unit.status = BloodUnit.Status.ALLOCATED
        self.unit.expires_on = timezone.localdate() - timedelta(days=1)
        self.unit.save(update_fields=["status", "expires_on"])

        self.request.status = BloodRequest.Status.ALLOCATED
        self.request.save(update_fields=["status"])

        allocation = BloodAllocation.objects.create(
            request=self.request,
            blood_unit=self.unit,
            status=BloodAllocation.Status.ALLOCATED,
        )

        with self.assertRaises(IssueError):
            issue_blood(allocation.id, self.user)

        self.assertEqual(BloodIssue.objects.count(), 0)

        allocation.refresh_from_db()
        self.unit.refresh_from_db()
        self.request.refresh_from_db()

        self.assertEqual(
            allocation.status, BloodAllocation.Status.ALLOCATED
        )
        self.assertEqual(self.unit.status, BloodUnit.Status.ALLOCATED)
        self.assertEqual(
            self.request.status, BloodRequest.Status.ALLOCATED
        )

    def test_unapproved_request_cannot_be_allocated(self):
        self.request.status = BloodRequest.Status.PENDING
        self.request.save(update_fields=["status"])

        with patch.dict(services.BLOOD_COMPATIBILITY, {"A+": ["A+"]}):
            with self.assertRaises(AllocationError):
                allocate_blood(self.request.id)

        self.assertEqual(BloodAllocation.objects.count(), 0)

        self.unit.refresh_from_db()
        self.assertEqual(self.unit.status, BloodUnit.Status.AVAILABLE)

    def test_allocate_endpoint_rejects_anonymous_user(self):
        client = APIClient()
        response = client.post(
            f"/api/requests/{self.request.id}/allocate/"
        )
        self.assertIn(response.status_code, (401, 403))

    def test_issue_endpoint_rejects_anonymous_user(self):
        client = APIClient()
        response = client.post("/api/allocations/999/issue/")
        self.assertIn(response.status_code, (401, 403))

    def test_non_staff_user_cannot_allocate_or_issue(self):
        user = get_user_model().objects.create_user(
            username="ordinaryuser",
            password="test-password",
            is_staff=False,
        )
        client = APIClient()
        client.force_authenticate(user=user)

        allocate_response = client.post(
            f"/api/requests/{self.request.id}/allocate/"
        )
        issue_response = client.post("/api/allocations/999/issue/")

        self.assertEqual(allocate_response.status_code, 403)
        self.assertEqual(issue_response.status_code, 403)

    @patch.dict(services.BLOOD_COMPATIBILITY, {"A+": ["A+"]})
    def test_allocation_failure_rolls_back_everything(self):
        with patch.object(
            BloodAllocation.objects,
            "bulk_create",
            side_effect=RuntimeError("Simulated database failure"),
        ):
            with self.assertRaises(RuntimeError):
                allocate_blood(self.request.id)

        self.request.refresh_from_db()
        self.unit.refresh_from_db()

        self.assertEqual(
            self.request.status, BloodRequest.Status.APPROVED
        )
        self.assertEqual(self.unit.status, BloodUnit.Status.AVAILABLE)
        self.assertEqual(BloodAllocation.objects.count(), 0)
    
    def test_issue_failure_rolls_back_all_status_updates(self):
        self.unit.status = BloodUnit.Status.ALLOCATED
        self.unit.save(update_fields=["status"])

        self.request.status = BloodRequest.Status.ALLOCATED
        self.request.save(update_fields=["status"])

        allocation = BloodAllocation.objects.create(
            request=self.request,
            blood_unit=self.unit,
            status=BloodAllocation.Status.ALLOCATED,
        )

        with patch.object(
            BloodIssue.objects,
            "create",
            side_effect=RuntimeError("Simulated issue-recording failure"),
        ):
            with self.assertRaises(RuntimeError):
                issue_blood(allocation.id, self.user)

        allocation.refresh_from_db()
        self.unit.refresh_from_db()
        self.request.refresh_from_db()

        self.assertEqual(
            allocation.status, BloodAllocation.Status.ALLOCATED
        )
        self.assertEqual(self.unit.status, BloodUnit.Status.ALLOCATED)
        self.assertEqual(
            self.request.status, BloodRequest.Status.ALLOCATED
        )
        self.assertEqual(BloodIssue.objects.count(), 0)
    def test_staff_can_approve_pending_request(self):
        self.request.status = BloodRequest.Status.PENDING
        self.request.save(update_fields=["status"])

        result = process_blood_request(
            self.request.id, BloodRequest.Status.APPROVED
        )

        self.assertEqual(result.status, BloodRequest.Status.APPROVED)

    def test_staff_can_reject_pending_request(self):
        self.request.status = BloodRequest.Status.PENDING
        self.request.save(update_fields=["status"])

        result = process_blood_request(
            self.request.id, BloodRequest.Status.REJECTED
        )

        self.assertEqual(result.status, BloodRequest.Status.REJECTED)

    def test_already_processed_request_cannot_be_processed_again(self):
        self.request.status = BloodRequest.Status.PENDING
        self.request.save(update_fields=["status"])

        process_blood_request(
            self.request.id, BloodRequest.Status.APPROVED
        )

        with self.assertRaises(RequestProcessingError):
            process_blood_request(
                self.request.id, BloodRequest.Status.REJECTED
            )

    def test_invalid_processing_decision_is_rejected(self):
        self.request.status = BloodRequest.Status.PENDING
        self.request.save(update_fields=["status"])

        with self.assertRaises(RequestProcessingError):
            process_blood_request(self.request.id, "ALLOCATED")

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
        self.assertEqual(
            response.data["recipient_name"], "Jane Doe"
        )

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