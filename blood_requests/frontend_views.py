from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.permissions import operational_staff_required
from donors.models import Donor
from .models import (
    BloodRequest,
    Recipient,
)
from .recipient_serializers import RecipientSerializer
from .serializers import BloodRequestSerializer
from .services import (
    AllocationError,
    IssueError,
    RequestProcessingError,
    allocate_blood,
    issue_blood,
    process_blood_request,
)


@operational_staff_required
def request_list(request):
    form_errors = {}
    if request.method == "POST":
        serializer = BloodRequestSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, "Blood request was created.")
            return redirect("blood-request-list")
        form_errors = serializer.errors

    requests = BloodRequest.objects.prefetch_related(
        "allocations__blood_unit",
        "allocations__issue",
    ).order_by("-created_at")
    selected_status = request.GET.get("status", "").strip()
    if selected_status in dict(BloodRequest.Status.choices):
        requests = requests.filter(status=selected_status)
    else:
        selected_status = ""

    context = {
        "active_nav": "requests",
        "requests": Paginator(requests, 20).get_page(
            request.GET.get("page")
        ),
        "status_choices": BloodRequest.Status.choices,
        "selected_status": selected_status,
        "blood_groups": Donor.BloodGroup.choices,
        "form_errors": form_errors,
        "submitted": request.POST if request.method == "POST" else {},
    }
    return render(request, "blood_requests/request_list.html", context)


@operational_staff_required
@require_POST
def process_request(request, request_id):
    decision = request.POST.get("decision")
    try:
        process_blood_request(request_id, decision)
    except ObjectDoesNotExist:
        messages.error(request, "Blood request not found.")
    except RequestProcessingError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, "Blood request status was updated.")
    return redirect("blood-request-list")


@operational_staff_required
@require_POST
def allocate_request(request, request_id):
    try:
        allocations = allocate_blood(request_id)
    except ObjectDoesNotExist:
        messages.error(request, "Blood request not found.")
    except AllocationError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(
            request,
            f"{len(allocations)} blood unit(s) allocated.",
        )
    return redirect("blood-request-list")


@operational_staff_required
@require_POST
def issue_allocation(request, allocation_id):
    try:
        issue_blood(allocation_id, request.user)
    except ObjectDoesNotExist:
        messages.error(request, "Blood allocation not found.")
    except IssueError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, "Allocated blood was issued.")
    return redirect("blood-request-list")


@operational_staff_required
def recipient_list(request):
    errors = {}
    if request.method == "POST":
        serializer = RecipientSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, "Recipient was registered.")
            return redirect("recipient-ui-list")
        errors = serializer.errors

    recipients = Recipient.objects.order_by("full_name", "id")
    search = request.GET.get("q", "").strip()
    if search:
        recipients = recipients.filter(full_name__icontains=search)

    return render(
        request,
        "blood_requests/recipient_list.html",
        {
            "active_nav": "requests",
            "recipients": Paginator(recipients, 25).get_page(
                request.GET.get("page")
            ),
            "blood_groups": Donor.BloodGroup.choices,
            "search_query": search,
            "errors": errors,
            "submitted": request.POST if request.method == "POST" else {},
        },
    )


@operational_staff_required
def update_recipient(request, recipient_id):
    recipient = get_object_or_404(Recipient, pk=recipient_id)
    errors = {}
    if request.method == "POST":
        serializer = RecipientSerializer(
            recipient,
            data=request.POST,
            partial=True,
        )
        if serializer.is_valid():
            serializer.save()
            messages.success(request, "Recipient record was updated.")
            return redirect("recipient-ui-list")
        errors = serializer.errors

    return render(
        request,
        "blood_requests/recipient_form.html",
        {
            "active_nav": "requests",
            "recipient": recipient,
            "blood_groups": Donor.BloodGroup.choices,
            "errors": errors,
            "submitted": request.POST if request.method == "POST" else {},
        },
    )
