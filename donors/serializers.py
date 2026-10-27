from datetime import date

from rest_framework import serializers

from .models import Donor


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
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value
