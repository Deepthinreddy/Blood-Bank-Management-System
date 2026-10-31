
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("donors", "0001_initial"),
        ("inventory", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Donation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("donation_date", models.DateTimeField()),
                ("blood_group", models.CharField(max_length=3)),
                ("quantity_ml", models.PositiveIntegerField()),
                (
                    "screening_status",
                    models.CharField(
                        choices=[
                            ("Pending", "Pending"),
                            ("Passed", "Passed"),
                            ("Failed", "Failed"),
                        ],
                        default="Pending",
                        max_length=7,
                    ),
                ),
                (
                    "donation_status",
                    models.CharField(
                        choices=[
                            ("Recorded", "Recorded"),
                            ("Accepted", "Accepted"),
                            ("Rejected", "Rejected"),
                            ("Processed", "Processed"),
                        ],
                        default="Recorded",
                        max_length=9,
                    ),
                ),
                ("notes", models.TextField(blank=True, null=True)),
                ("recorded_at", models.DateTimeField(auto_now_add=True)),
                (
                    "donor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="donations",
                        to="donors.donor",
                    ),
                ),
            ],
        ),
        migrations.DeleteModel(name="BloodInventory"),
        migrations.CreateModel(
            name="BloodInventory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("blood_group", models.CharField(max_length=3)),
                ("quantity_ml", models.PositiveIntegerField()),
                ("available_ml", models.PositiveIntegerField()),
                ("collection_date", models.DateField()),
                ("expiry_date", models.DateField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Available", "Available"),
                            ("Reserved", "Reserved"),
                            ("Issued", "Issued"),
                            ("Expired", "Expired"),
                            ("Discarded", "Discarded"),
                        ],
                        default="Available",
                        max_length=9,
                    ),
                ),
                (
                    "storage_location",
                    models.CharField(
                        blank=True,
                        max_length=100,
                        null=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "donation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="inventory_items",
                        to="inventory.donation",
                    ),
                ),
            ],
            options={
                "ordering": ["blood_group", "expiry_date"],
            },
        ),
        migrations.DeleteModel(name="BloodAllocations"),
        migrations.DeleteModel(name="BloodRequests"),
        migrations.DeleteModel(name="Donations"),
        migrations.DeleteModel(name="Donors"),
        migrations.DeleteModel(name="Recipients"),
    ]
