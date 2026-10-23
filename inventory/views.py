
from datetime import timedelta

from django.contrib import messages
from django.db import IntegrityError, transaction
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

    inventory = BloodInventory.objects.filter(
        status="Available",
        available_ml__gt=0,
        expiry_date__gte=today,
    ).order_by("blood_group", "expiry_date")

    return render(
        request,
        "inventory/inventory_list.html",
        {"inventory": inventory},
    )
