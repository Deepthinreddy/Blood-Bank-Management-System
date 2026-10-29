from django.shortcuts import render
from .models import Recipient

# Create your views here.

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from .services import (
    AllocationError,
    IssueError,
    RequestProcessingError,
    allocate_blood,
    issue_blood,
    process_blood_request,
)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def allocate_request(request, request_id):
    if not (request.user.is_staff or request.user.is_superuser):
        return Response(
            {"detail": "Staff authorization required."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        allocations = allocate_blood(request_id)
    except ObjectDoesNotExist:
        return Response(
            {"detail": "Blood request not found."},
            status=status.HTTP_404_NOT_FOUND,
        )
    except AllocationError as exc:
        return Response(
            {"detail": str(exc)},
            status=status.HTTP_409_CONFLICT,
        )

    return Response(
        {
            "request_id": request_id,
            "allocation_ids": [item.id for item in allocations],
            "allocated_units": len(allocations),
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def issue_allocation(request, allocation_id):
    if not (request.user.is_staff or request.user.is_superuser):
        return Response(
            {"detail": "Staff authorization required."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        issue = issue_blood(allocation_id, request.user)
    except ObjectDoesNotExist:
        return Response(
            {"detail": "Allocation not found."},
            status=status.HTTP_404_NOT_FOUND,
        )
    except IssueError as exc:
        return Response(
            {"detail": str(exc)},
            status=status.HTTP_409_CONFLICT,
        )

    return Response(
        {
            "issue_id": issue.id,
            "allocation_id": allocation_id,
            "issued_at": issue.issued_at.isoformat(),
        },
        status=status.HTTP_200_OK,
    )

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def process_request(request, request_id):
    if not (request.user.is_staff or request.user.is_superuser):
        return Response(
            {"detail": "Staff authorization required."},
            status=status.HTTP_403_FORBIDDEN,
        )

    decision = request.data.get("decision")

    try:
        blood_request = process_blood_request(request_id, decision)
    except ObjectDoesNotExist:
        return Response(
            {"detail": "Blood request not found."},
            status=status.HTTP_404_NOT_FOUND,
        )
    except RequestProcessingError as exc:
        return Response(
            {"detail": str(exc)},
            status=status.HTTP_409_CONFLICT,
        )

    return Response(
        {
            "request_id": blood_request.id,
            "status": blood_request.status,
        },
        status=status.HTTP_200_OK,
    )
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def register_recipient(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return Response(
            {"detail": "Staff authorization required."},
            status=status.HTTP_403_FORBIDDEN,
        )

    required_fields = [
        "full_name",
        "identification_number",
        "contact_number",
        "blood_group",
    ]

    missing_fields = [
        field for field in required_fields
        if not request.data.get(field)
    ]

    if missing_fields:
        return Response(
            {
                "detail": "Required fields are missing.",
                "missing_fields": missing_fields,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    recipient = Recipient(
        full_name=request.data["full_name"].strip(),
        identification_number=request.data[
            "identification_number"
        ].strip(),
        contact_number=request.data["contact_number"].strip(),
        blood_group=request.data["blood_group"].strip(),
        notes=request.data.get("notes", "").strip(),
    )

    try:
        recipient.full_clean()
        recipient.save()
    except Exception as exc:
        from django.core.exceptions import ValidationError
        from django.db import IntegrityError

        if isinstance(exc, (ValidationError, IntegrityError)):
            return Response(
                {"detail": "Invalid recipient data or duplicate identification number."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        raise

    return Response(
        {
            "id": recipient.id,
            "full_name": recipient.full_name,
            "blood_group": recipient.blood_group,
            "registered_at": recipient.registered_at.isoformat(),
        },
        status=status.HTTP_201_CREATED,
    )