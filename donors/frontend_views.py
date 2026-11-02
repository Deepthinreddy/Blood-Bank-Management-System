from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import operational_staff_required
from .models import Donor
from .serializers import (
    DonorRegistrationSerializer,
    DonationSerializer,
    DonorEligibilitySerializer,
)


def _render_donor_form(request, *, donor=None, serializer=None):
    blood_groups = Donor.BloodGroup.choices
    context = {
        "active_nav": "donors",
        "donor": donor,
        "blood_groups": blood_groups,
        "submitted": request.POST if request.method == "POST" else {},
        "errors": serializer.errors if serializer else {},
    }
    return render(request, "donors/donor_form.html", context)


@operational_staff_required
def donor_list(request):
    donors = Donor.objects.all()
    search = request.GET.get("q", "").strip()
    blood_group = request.GET.get("blood_group", "").strip()
    if search:
        donors = donors.filter(full_name__icontains=search)
    if blood_group in dict(Donor.BloodGroup.choices):
        donors = donors.filter(blood_group=blood_group)

    context = {
        "active_nav": "donors",
        "donors": Paginator(donors, 25).get_page(request.GET.get("page")),
        "search_query": search,
        "selected_blood_group": blood_group,
        "blood_groups": Donor.BloodGroup.choices,
    }
    return render(request, "donors/donor_list.html", context)


@operational_staff_required
def register_donor(request):
    if request.method != "POST":
        return _render_donor_form(request)

    serializer = DonorRegistrationSerializer(data=request.POST)
    if serializer.is_valid():
        donor = serializer.save()
        messages.success(request, f"{donor.full_name} was registered.")
        return redirect("donor-ui-detail", donor_id=donor.pk)

    return _render_donor_form(request, serializer=serializer)


@operational_staff_required
def update_donor(request, donor_id):
    donor = get_object_or_404(Donor, pk=donor_id)
    if request.method == "POST":
        serializer = DonorRegistrationSerializer(
            donor,
            data=request.POST,
            partial=True,
        )
        if serializer.is_valid():
            donor = serializer.save()
            messages.success(request, f"{donor.full_name}'s record was updated.")
            return redirect("donor-ui-detail", donor_id=donor.pk)
    else:
        serializer = None

    return _render_donor_form(
        request,
        donor=donor,
        serializer=serializer,
    )


@operational_staff_required
def donor_detail(request, donor_id):
    donor = get_object_or_404(Donor, pk=donor_id)
    form_errors = {}
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "record-donation":
            payload = request.POST.copy()
            payload["donor"] = donor.pk
            serializer = DonationSerializer(data=payload)
        elif action == "update-eligibility":
            serializer = DonorEligibilitySerializer(
                donor,
                data=request.POST,
                partial=True,
            )
        else:
            messages.error(request, "Choose a valid donor action.")
            return redirect("donor-ui-detail", donor_id=donor.pk)

        if serializer.is_valid():
            serializer.save()
            messages.success(request, "Donor information was updated.")
            return redirect("donor-ui-detail", donor_id=donor.pk)
        form_errors = serializer.errors

    context = {
        "active_nav": "donors",
        "donor": donor,
        "donations": donor.donation_history_records.all(),
        "eligibility_checked_at": donor.eligibility_checked_at,
        "form_errors": form_errors,
    }
    return render(request, "donors/donor_detail.html", context)
