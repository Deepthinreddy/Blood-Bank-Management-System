# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Donors(models.Model):
    donor_id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    sex = models.CharField(max_length=17, blank=True, null=True)
    blood_group = models.CharField(max_length=3)
    phone = models.CharField(max_length=20)
    email = models.CharField(unique=True, max_length=254, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    eligibility_status = models.CharField(max_length=10)
    last_donation_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'donors'


class Recipients(models.Model):
    recipient_id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(blank=True, null=True)
    blood_group = models.CharField(max_length=3)
    phone = models.CharField(max_length=20)
    email = models.CharField(unique=True, max_length=254, blank=True, null=True)
    hospital_name = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'recipients'


class Donations(models.Model):
    donation_id = models.BigAutoField(primary_key=True)
    donor = models.ForeignKey(Donors, models.DO_NOTHING)
    donation_date = models.DateTimeField()
    blood_group = models.CharField(max_length=3)
    quantity_ml = models.PositiveIntegerField()
    screening_status = models.CharField(max_length=7)
    donation_status = models.CharField(max_length=9)
    notes = models.TextField(blank=True, null=True)
    recorded_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'donations'


class BloodInventory(models.Model):
    inventory_id = models.BigAutoField(primary_key=True)
    donation = models.ForeignKey(Donations, models.DO_NOTHING)
    blood_group = models.CharField(max_length=3)
    quantity_ml = models.PositiveIntegerField()
    available_ml = models.PositiveIntegerField()
    collection_date = models.DateField()
    expiry_date = models.DateField()
    status = models.CharField(max_length=9)
    storage_location = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'blood_inventory'


class BloodRequests(models.Model):
    request_id = models.BigAutoField(primary_key=True)
    recipient = models.ForeignKey(Recipients, models.DO_NOTHING)
    blood_group = models.CharField(max_length=3)
    requested_quantity_ml = models.PositiveIntegerField()
    priority = models.CharField(max_length=9)
    required_by = models.DateTimeField(blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=19)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'blood_requests'


class BloodAllocations(models.Model):
    allocation_id = models.BigAutoField(primary_key=True)
    request = models.ForeignKey(BloodRequests, models.DO_NOTHING)
    inventory = models.ForeignKey(BloodInventory, models.DO_NOTHING)
    allocated_quantity_ml = models.PositiveIntegerField()
    status = models.CharField(max_length=9)
    allocated_at = models.DateTimeField(blank=True, null=True)
    issued_at = models.DateTimeField(blank=True, null=True)
    issued_by = models.CharField(max_length=150, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'blood_allocations'
