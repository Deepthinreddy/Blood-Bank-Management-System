
from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import DonationForm


def donation_create(request):
    if request.method == "POST":
        form = DonationForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Blood donation recorded successfully.")
            return redirect("donation_create")
    else:
        form = DonationForm()

    return render(
        request,
        "inventory/donation_form.html",
        {"form": form},
    )
