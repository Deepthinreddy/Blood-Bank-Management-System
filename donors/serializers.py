from datetime import date

from rest_framework import serializers

from .models import Donor, Donation


class DonorRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donor
        fields = [
            "id",
            "full_name",
            "date_of_birth",
            "phone_number",
            "email",
            "address",
            "blood_group",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_full_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Full name is required.")
        return value

    def validate_phone_number(self, value):
        value = value.strip()
        digits = sum(character.isdigit() for character in value)
        if digits < 7 or digits > 15:
            raise serializers.ValidationError(
                "Enter a valid phone number containing 7 to 15 digits."
            )
        return value

    def validate_date_of_birth(self, value):
        if value > date.today():
            raise serializers.ValidationError(
                "Date of birth cannot be in the future."
            )
        return value


class DonationSerializer(serializers.ModelSerializer):
    donor_name = serializers.CharField(
        source="donor.full_name",
        read_only=True,
    )
    blood_group = serializers.CharField(
        source="donor.blood_group",
        read_only=True,
    )

    class Meta:
        model = Donation
        fields = [
            "id",
            "donor",
            "donor_name",
            "blood_group",
            "donation_date",
            "quantity_ml",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_donation_date(self, value):
        if value > date.today():
            raise serializers.ValidationError(
                "Donation date cannot be in the future."
            )
        return value

    def validate_quantity_ml(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Donation quantity must be greater than zero."
            )
        return value