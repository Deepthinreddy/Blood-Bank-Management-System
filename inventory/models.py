from django.db import models
from donors.models import Donor


class Donation(models.Model):
    class ScreeningStatus(models.TextChoices):
        PENDING = "Pending", "Pending"
        PASSED = "Passed", "Passed"
        FAILED = "Failed", "Failed"

    class DonationStatus(models.TextChoices):
        RECORDED = "Recorded", "Recorded"
        ACCEPTED = "Accepted", "Accepted"
        REJECTED = "Rejected", "Rejected"
        PROCESSED = "Processed", "Processed"

    donor = models.ForeignKey(
        Donor,
        on_delete=models.PROTECT,
        related_name="donations",
    )
    donation_date = models.DateTimeField()
    blood_group = models.CharField(max_length=3)
    quantity_ml = models.PositiveIntegerField()
    screening_status = models.CharField(
        max_length=7,
        choices=ScreeningStatus.choices,
        default=ScreeningStatus.PENDING,
    )
    donation_status = models.CharField(
        max_length=9,
        choices=DonationStatus.choices,
        default=DonationStatus.RECORDED,
    )
    notes = models.TextField(blank=True, null=True)
    recorded_at = models.DateTimeField(auto_now_add=True)


class BloodInventory(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "Available", "Available"
        RESERVED = "Reserved", "Reserved"
        ISSUED = "Issued", "Issued"
        EXPIRED = "Expired", "Expired"
        DISCARDED = "Discarded", "Discarded"

    donation = models.ForeignKey(
        Donation,
        on_delete=models.PROTECT,
        related_name="inventory_items",
    )
    blood_group = models.CharField(max_length=3)
    quantity_ml = models.PositiveIntegerField()
    available_ml = models.PositiveIntegerField()
    collection_date = models.DateField()
    expiry_date = models.DateField()
    status = models.CharField(
        max_length=9,
        choices=Status.choices,
        default=Status.AVAILABLE,
    )
    storage_location = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["blood_group", "expiry_date"]