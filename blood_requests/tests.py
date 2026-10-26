from django.test import TestCase

# Create your tests here.

from datetime import timedelta
from unittest.mock import patch
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from . import services
from .models import BloodAllocation, BloodIssue, BloodRequest, BloodUnit
from .services import AllocationError, IssueError, allocate_blood, issue_blood


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
