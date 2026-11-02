from rest_framework import serializers

from .models import Recipient


class RecipientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipient
        fields = [
            "id",
            "full_name",
            "identification_number",
            "contact_number",
            "blood_group",
            "notes",
            "registered_at",
        ]
        read_only_fields = ["id", "registered_at"]

    def validate_full_name(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "Recipient name cannot be empty."
            )
        return value.strip()

    def validate_identification_number(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "Identification number cannot be empty."
            )
        return value.strip()

    def validate_blood_group(self, value):
        valid_groups = [
            "A+", "A-", "B+", "B-",
            "AB+", "AB-", "O+", "O-",
        ]

        if value not in valid_groups:
            raise serializers.ValidationError(
                "Invalid blood group."
            )
        return value