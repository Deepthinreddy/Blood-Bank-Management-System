
from datetime import timedelta

from django.contrib import messages
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import DonationForm
from .models import BloodInventory


def donation_create(request):
    if request.method == "POST":
        form = DonationForm(request.POST)

        if form.is_valid():
            donation = form.save(commit=False)

            try:
                with transaction.atomic():
                    donation.save()

                    eligible = (
                        donation.screening_status == "Passed"
                        and donation.donation_status == "Accepted"
                    )

                    if eligible:
                        collection_date = donation.donation_date.date()

                        BloodInventory.objects.create(
                            donation=donation,
                            blood_group=donation.blood_group,
                            quantity_ml=donation.quantity_ml,
                            available_ml=donation.quantity_ml,
                            collection_date=collection_date,
                            expiry_date=collection_date + timedelta(days=42),
                            status="Available",
                            storage_location="Main Storage",
                        )

                if eligible:
                    messages.success(
                        request,
                        "Donation recorded and blood inventory updated successfully.",
                    )
                else:
                    messages.success(
                        request,
                        "Donation recorded. Inventory was not updated because "
                        "screening or acceptance requirements were not met.",
                    )

                return redirect("donation_create")

            except IntegrityError:
                messages.error(
                    request,
                    "The donation could not be saved because a database "
                    "constraint was violated. Please check the records.",
                )

    else:
        form = DonationForm()

    return render(
        request,
        "inventory/donation_form.html",
        {"form": form},
    )


def inventory_list(request):
    today = timezone.localdate()
    warning_date = today + timedelta(days=7)

    # F-014: Mark expired available stock as expired.
    # Do not change Reserved, Issued, or Discarded stock automatically.
    BloodInventory.objects.filter(
        status="Available",
        expiry_date__lt=today,
    ).update(status="Expired")

    inventory = BloodInventory.objects.all()

    # F-013: Search by blood group or storage location.
    search_query = request.GET.get("q", "").strip()
    if search_query:
        inventory = inventory.filter(
            Q(blood_group__icontains=search_query)
            | Q(storage_location__icontains=search_query)
        )

    # Filter by status.
    selected_status = request.GET.get("status", "").strip()
    valid_statuses = {choice[0] for choice in BloodInventory.Status.choices}

    if selected_status in valid_statuses:
        inventory = inventory.filter(status=selected_status)
    else:
        selected_status = ""

    # Filter by expiry category.
    expiry_filter = request.GET.get("expiry", "").strip()

    if expiry_filter == "expiring":
        inventory = inventory.filter(
            status="Available",
            expiry_date__gte=today,
            expiry_date__lte=warning_date,
        )
    elif expiry_filter == "expired":
        inventory = inventory.filter(
            Q(status="Expired") | Q(expiry_date__lt=today)
        )
    elif expiry_filter == "valid":
        inventory = inventory.filter(
            status="Available",
            expiry_date__gt=warning_date,
            available_ml__gt=0,
        )

    inventory = inventory.order_by("blood_group", "expiry_date")

    # Attach display-only expiry information; no schema changes needed.
    for item in inventory:
        if item.expiry_date < today or item.status == "Expired":
            item.expiry_label = "Expired"
        elif (
            item.status == "Available"
            and item.expiry_date <= warning_date
        ):
            item.expiry_label = "Expiring soon"
        else:
            item.expiry_label = "Normal"

    context = {
        "inventory": inventory,
        "search_query": search_query,
        "selected_status": selected_status,
        "expiry_filter": expiry_filter,
        "status_choices": BloodInventory.Status.choices,
        "today": today,
    }

    return render(request, "inventory/inventory_list.html", context)
