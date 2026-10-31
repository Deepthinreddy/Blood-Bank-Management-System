from django.shortcuts import render

# Create your views here.

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.db.models import Q
from .models import Recipient
from .recipient_serializers import RecipientSerializer


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
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def recipient_list(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return Response(
            {"detail": "Staff access required."},
            status=status.HTTP_403_FORBIDDEN,
        )

    recipients = Recipient.objects.all().order_by("id")
    search = request.query_params.get("search")

    if search:
        recipients = recipients.filter(
            Q(full_name__icontains=search)
            | Q(identification_number__icontains=search)
            | Q(contact_number__icontains=search)
        )

    serializer = RecipientSerializer(recipients, many=True)
    return Response(serializer.data)


@api_view(["GET", "PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def recipient_detail(request, recipient_id):
    if not (request.user.is_staff or request.user.is_superuser):
        return Response(
            {"detail": "Staff access required."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        recipient = Recipient.objects.get(pk=recipient_id)
    except Recipient.DoesNotExist:
        return Response(
            {"detail": "Recipient not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == "GET":
        serializer = RecipientSerializer(recipient)
        return Response(serializer.data)

    serializer = RecipientSerializer(
        recipient,
        data=request.data,
        partial=(request.method == "PATCH"),
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)