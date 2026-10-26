from django.db import models

# Create your models here.

from django.conf import settings
from django.db import models


class BloodRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        ALLOCATED = "ALLOCATED", "Allocated"
        FULFILLED = "FULFILLED", "Fulfilled"
        REJECTED = "REJECTED", "Rejected"

    recipient_name = models.CharField(max_length=150)
    blood_group = models.CharField(max_length=3)
    units_requested = models.PositiveIntegerField()
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)


class BloodUnit(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        ALLOCATED = "ALLOCATED", "Allocated"
        ISSUED = "ISSUED", "Issued"
        EXPIRED = "EXPIRED", "Expired"

    blood_group = models.CharField(max_length=3)
    expires_on = models.DateField()
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.AVAILABLE,
        db_index=True,
    )


class BloodAllocation(models.Model):
    class Status(models.TextChoices):
        ALLOCATED = "ALLOCATED", "Allocated"
        ISSUED = "ISSUED", "Issued"
        CANCELLED = "CANCELLED", "Cancelled"

    request = models.ForeignKey(
        BloodRequest,
        on_delete=models.PROTECT,
        related_name="allocations",
    )
    blood_unit = models.OneToOneField(
        BloodUnit,
        on_delete=models.PROTECT,
        related_name="allocation",
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ALLOCATED,
        db_index=True,
    )
    allocated_at = models.DateTimeField(auto_now_add=True)


class BloodIssue(models.Model):
    allocation = models.OneToOneField(
        BloodAllocation,
        on_delete=models.PROTECT,
        related_name="issue",
    )
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )
    issued_at = models.DateTimeField(auto_now_add=True)
