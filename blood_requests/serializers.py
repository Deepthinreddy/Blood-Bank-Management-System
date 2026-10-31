from rest_framework import serializers

from .models import BloodRequest


class BloodRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodRequest
        fields = [
            "id",
            "recipient_name",
            "blood_group",
            "units_requested",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "status", "created_at"]

    def validate_recipient_name(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "Recipient name cannot be empty."
            )
        return value.strip()

    def validate_blood_group(self, value):
        valid_groups = [
            "A+", "A-", "B+", "B-",
            "AB+", "AB-", "O+", "O-",
        ]

        if value not in valid_groups:
            raise serializers.ValidationError(
                "Invalid blood group. Choose a valid ABO/Rh blood group."
            )
        return value

    def validate_units_requested(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Units requested must be greater than zero."
            )
        return value