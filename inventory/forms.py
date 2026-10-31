"""Forms used for blood donation data entry."""

from django import forms

from .models import Donations


class DonationForm(forms.ModelForm):
    """Validate and collect information required to record a donation."""

    class Meta:
        """Define the model fields and widgets displayed in the form."""

        model = Donations
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
            "donation_date": forms.DateInput(attrs={"type": "date"}),
            "quantity_ml": forms.NumberInput(attrs={"min": 1}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_quantity_ml(self):
        """
        Validate that the donated blood quantity is positive.

        Returns:
            int: The validated donation quantity.

        Raises:
            ValidationError: If the quantity is zero or negative.
        """
        quantity = self.cleaned_data["quantity_ml"]

        if quantity <= 0:
            raise forms.ValidationError(
                "Donation quantity must be greater than zero."
            )

        return quantity