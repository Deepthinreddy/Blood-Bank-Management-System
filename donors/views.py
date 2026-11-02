from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Donor, Donation
from .serializers import (
    DonorRegistrationSerializer,
    DonationSerializer,
    DonorEligibilitySerializer,
)


def staff_authorized(user):
    return user.is_authenticated and (
        user.is_staff or user.is_superuser
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def register_donor(request):
    """Register a donor. Only authorized staff may do this."""

    if not staff_authorized(request.user):
        return Response(
            {"detail": "Staff authorization required."},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = DonorRegistrationSerializer(data=request.data)

    if serializer.is_valid():
        donor = serializer.save()
        return Response(
            DonorRegistrationSerializer(donor).data,
            status=status.HTTP_201_CREATED,
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def donor_list(request):
    """List and search registered donors."""

    if not staff_authorized(request.user):
        return Response(
            {"detail": "Staff authorization required."},
            status=status.HTTP_403_FORBIDDEN,
        )

    donors = Donor.objects.all()

    name = request.query_params.get("name", "").strip()
    blood_group = request.query_params.get("blood_group", "").strip()
    phone = request.query_params.get("phone", "").strip()

    if name:
        donors = donors.filter(full_name__icontains=name)

    if blood_group:
        donors = donors.filter(blood_group=blood_group)

    if phone:
        donors = donors.filter(phone_number__icontains=phone)

    serializer = DonorRegistrationSerializer(donors, many=True)

    return Response(
        serializer.data,
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def donor_detail(request, donor_id):
    """Retrieve an individual donor."""

    if not staff_authorized(request.user):
        return Response(
            {"detail": "Staff authorization required."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        donor = Donor.objects.get(pk=donor_id)
    except Donor.DoesNotExist:
        return Response(
            {"detail": "Donor not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = DonorRegistrationSerializer(donor)

    return Response(
        serializer.data,
        status=status.HTTP_200_OK,
    )


@api_view(["PATCH", "PUT"])
@permission_classes([IsAuthenticated])
def update_donor(request, donor_id):
    """Update an existing donor's personal details."""

    if not staff_authorized(request.user):
        return Response(
            {"detail": "Staff authorization required."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        donor = Donor.objects.get(pk=donor_id)
    except Donor.DoesNotExist:
        return Response(
            {"detail": "Donor not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = DonorRegistrationSerializer(
        donor,
        data=request.data,
        partial=(request.method == "PATCH"),
    )

    if serializer.is_valid():
        donor = serializer.save()

        return Response(
            DonorRegistrationSerializer(donor).data,
            status=status.HTTP_200_OK,
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def donor_donation_history(request, donor_id):
    """Retrieve donation history or record a donation for a donor."""

    if not staff_authorized(request.user):
        return Response(
            {"detail": "Staff authorization required."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        donor = Donor.objects.get(pk=donor_id)
    except Donor.DoesNotExist:
        return Response(
            {"detail": "Donor not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == "GET":
        donations = Donation.objects.filter(donor=donor)
        serializer = DonationSerializer(donations, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    payload = request.data.copy()
    payload["donor"] = donor.pk

    serializer = DonationSerializer(data=payload)

    if serializer.is_valid():
        donation = serializer.save()

        return Response(
            DonationSerializer(donation).data,
            status=status.HTTP_201_CREATED,
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["GET", "PATCH", "PUT"])
@permission_classes([IsAuthenticated])
def donor_eligibility(request, donor_id):
    """Retrieve or update a donor's eligibility assessment."""

    if not staff_authorized(request.user):
        return Response(
            {"detail": "Staff authorization required."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        donor = Donor.objects.get(pk=donor_id)
    except Donor.DoesNotExist:
        return Response(
            {"detail": "Donor not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == "GET":
        serializer = DonorEligibilitySerializer(donor)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    serializer = DonorEligibilitySerializer(
        donor,
        data=request.data,
        partial=(request.method == "PATCH"),
    )

    if serializer.is_valid():
        donor = serializer.save()

        return Response(
            DonorEligibilitySerializer(donor).data,
            status=status.HTTP_200_OK,
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )