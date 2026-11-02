
import os
import statistics
import time
from datetime import date, timedelta
from math import ceil

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings_benchmark",
)

import django

django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from donors.models import Donor
from inventory.models import BloodInventory, Donation as InventoryDonation


# Safety check: never run this benchmark against the normal database.
database_name = str(settings.DATABASES["default"]["NAME"])

if not database_name.endswith("db_benchmark.sqlite3"):
    raise SystemExit("ERROR: Benchmark database not selected. Stopping.")

User = get_user_model()

RECORD_COUNT = 1000
REQUEST_COUNT = 30
BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]


def create_test_data():
    print("Preparing isolated benchmark data...")

    # Clear only the separate benchmark database.
    BloodInventory.objects.all().delete()
    InventoryDonation.objects.all().delete()
    Donor.objects.all().delete()

    staff, _ = User.objects.get_or_create(
        username="nf4_benchmark_staff",
        defaults={
            "email": "benchmark@example.com",
            "role": "STAFF",
            "is_staff": True,
        },
    )

    if not staff.is_staff:
        staff.is_staff = True
        staff.save(update_fields=["is_staff"])

    donors = []

    for number in range(RECORD_COUNT):
        donors.append(
            Donor(
                full_name=f"Benchmark Donor {number}",
                date_of_birth=date(1990, 1, 1),
                phone_number=f"900{number:07d}",
                email=f"benchmark{number}@example.com",
                address="Benchmark Test Address",
                blood_group=BLOOD_GROUPS[number % len(BLOOD_GROUPS)],
            )
        )

    Donor.objects.bulk_create(donors)

    donors = list(Donor.objects.all().order_by("id"))

    donations = []

    for number, donor in enumerate(donors):
        donations.append(
            InventoryDonation(
                donor=donor,
                donation_date=timezone.now(),
                blood_group=donor.blood_group,
                quantity_ml=450,
                screening_status="Passed",
                donation_status="Accepted",
            )
        )

    InventoryDonation.objects.bulk_create(donations)

    donations = list(
        InventoryDonation.objects.all().order_by("id")
    )

    today = date.today()
    inventory_records = []

    for number, donation in enumerate(donations):
        inventory_records.append(
            BloodInventory(
                donation=donation,
                blood_group=donation.blood_group,
                quantity_ml=450,
                available_ml=450,
                collection_date=today,
                expiry_date=today + timedelta(days=42),
                status="Available",
                storage_location=f"Benchmark Storage {number}",
            )
        )

    BloodInventory.objects.bulk_create(inventory_records)

    print(f"Created {Donor.objects.count()} donors.")
    print(f"Created {InventoryDonation.objects.count()} donations.")
    print(f"Created {BloodInventory.objects.count()} inventory records.")

    return staff


def benchmark_endpoint(client, label, url, params=None):
    print(f"\nBenchmarking: {label}")

    # Warm-up requests are excluded from measurements.
    for _ in range(5):
        response = client.get(url, params or {})
        if response.status_code != 200:
            raise RuntimeError(
                f"{label} returned HTTP {response.status_code}"
            )

    timings = []

    for _ in range(REQUEST_COUNT):
        start = time.perf_counter()
        response = client.get(url, params or {})
        elapsed = time.perf_counter() - start

        if response.status_code != 200:
            raise RuntimeError(
                f"{label} returned HTTP {response.status_code}"
            )

        timings.append(elapsed * 1000)

    ordered = sorted(timings)
    p90 = ordered[ceil(0.90 * len(ordered)) - 1]
    median = statistics.median(timings)
    within_target = sum(value <= 2000 for value in timings)

    print(f"Requests measured: {REQUEST_COUNT}")
    print(f"Median response: {median:.2f} ms")
    print(f"90th percentile: {p90:.2f} ms")
    print(f"Requests within 2 seconds: {within_target}/{REQUEST_COUNT}")
    print(
        f"Percentage within 2 seconds: "
        f"{within_target / REQUEST_COUNT * 100:.1f}%"
    )


def main():
    print("NF-4 Performance Benchmark")
    print("Database: SQLite benchmark database")
    print(f"Synthetic records: {RECORD_COUNT}")
    print(f"Measured requests per endpoint: {REQUEST_COUNT}")

    staff = create_test_data()

    client = APIClient()
    client.force_authenticate(user=staff)

    benchmark_endpoint(
        client,
        "Donor blood-group search",
        "/api/donors/list/",
        {"blood_group": "O+"},
    )

    benchmark_endpoint(
        client,
        "Inventory listing and pagination",
        "/inventory/",
        {"page": 1},
    )

    benchmark_endpoint(
        client,
        "Inventory search",
        "/inventory/",
        {"q": "O+", "page": 1},
    )

    print("\nBenchmark completed.")
    print("Results apply to this local SQLite test environment only.")


if __name__ == "__main__":
    main()
