from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone

from accounts.permissions import operational_staff_required
from blood_requests.models import BloodRequest
from donors.models import Donor
from inventory.models import BloodInventory


@operational_staff_required
def dashboard(request):
    today = timezone.localdate()
    blood_stock = list(
        BloodInventory.objects.filter(
            status=BloodInventory.Status.AVAILABLE,
            expiry_date__gte=today,
            available_ml__gt=0,
        )
        .values("blood_group")
        .annotate(available_ml=Sum("available_ml"))
        .order_by("blood_group")
    )
    max_stock = max(
        (item["available_ml"] for item in blood_stock),
        default=0,
    )
    for item in blood_stock:
        item["bar_width"] = round(item["available_ml"] / max_stock * 100)

    context = {
        "total_donors": Donor.objects.count(),
        "available_stock_ml": sum(
            item["available_ml"] for item in blood_stock
        ),
        "pending_requests": BloodRequest.objects.filter(
            status=BloodRequest.Status.PENDING
        ).count(),
        "total_requests": BloodRequest.objects.count(),
        "recent_donors": Donor.objects.order_by("-created_at")[:5],
        "recent_requests": BloodRequest.objects.order_by("-created_at")[:5],
        "blood_stock": blood_stock,
    }
    return render(request, "dashboard/home.html", context)
