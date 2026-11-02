from django.contrib.auth import get_user_model
from django.db.models import Count
from django.shortcuts import render

from donors.models import Donor
from .permissions import admin_required


User = get_user_model()


@admin_required
def admin_dashboard(request):
    return render(
        request,
        "accounts/admin_dashboard.html",
    )


@admin_required
def admin_reports(request):
    total_users = User.objects.count()
    total_donors = Donor.objects.count()

    donors_by_blood_group = (
        Donor.objects.values("blood_group")
        .annotate(total=Count("id"))
        .order_by("blood_group")
    )

    recent_donors = Donor.objects.order_by("-created_at")[:10]

    context = {
        "total_users": total_users,
        "total_donors": total_donors,
        "donors_by_blood_group": donors_by_blood_group,
        "recent_donors": recent_donors,
    }

    return render(
        request,
        "accounts/admin_reports.html",
        context,
    )