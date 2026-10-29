
from django import forms
from donors.models import Donor
from .models import Donation


class DonationForm(forms.ModelForm):
    donor = forms.ModelChoiceField(
        queryset=Donor.objects.all(),
        empty_label="Select a donor",
    )

    class Meta:
        model = Donation
        fields = [
            "donor",
            "donation_date",
            "blood_group",
            "quantity_ml",
            "screening_status",
            "donation_status",
            "notes",
        ]
        widgets = {
            "donation_date": forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            ),
            "quantity_ml": forms.NumberInput(attrs={"min": 1}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_quantity_ml(self):
        quantity = self.cleaned_data["quantity_ml"]
        if quantity <= 0:
            raise forms.ValidationError(
                "Donation quantity must be greater than zero."
            )
        return quantity
