
from django.db import transaction
from django.utils import timezone

from .models import BloodAllocation, BloodRequest, BloodUnit


class AllocationError(Exception):
    """Raised when a blood request cannot be allocated."""


# Temporary configurable compatibility mapping.
# Replace with the team-approved matrix before production.
BLOOD_COMPATIBILITY = {}


def compatible_donor_groups(recipient_group):
    """Return permitted donor groups for a recipient."""
    if recipient_group not in BLOOD_COMPATIBILITY:
        raise AllocationError(
            f"No approved compatibility rule for {recipient_group}."
        )
    return BLOOD_COMPATIBILITY[recipient_group]


@transaction.atomic
def allocate_blood(request_id):
    blood_request = (
        BloodRequest.objects.select_for_update()
        .get(pk=request_id)
    )

    if blood_request.status != BloodRequest.Status.APPROVED:
        raise AllocationError("Only approved requests can be allocated.")

    if blood_request.units_requested < 1:
        raise AllocationError("Requested units must be greater than zero.")

    donor_groups = compatible_donor_groups(blood_request.blood_group)

    units = list(
        BloodUnit.objects.select_for_update()
        .filter(
            blood_group__in=donor_groups,
            status=BloodUnit.Status.AVAILABLE,
            expires_on__gte=timezone.localdate(),
        )
        .order_by("expires_on", "id")[:blood_request.units_requested]
    )

    if len(units) != blood_request.units_requested:
        raise AllocationError("Insufficient compatible, unexpired stock.")

    allocations = [
        BloodAllocation(request=blood_request, blood_unit=unit)
        for unit in units
    ]
    BloodAllocation.objects.bulk_create(allocations)

    BloodUnit.objects.filter(
        id__in=[unit.id for unit in units],
        status=BloodUnit.Status.AVAILABLE,
    ).update(status=BloodUnit.Status.ALLOCATED)

    blood_request.status = BloodRequest.Status.ALLOCATED
    blood_request.save(update_fields=["status"])

    return allocations

from django.db import transaction
from django.utils import timezone

from .models import BloodAllocation, BloodIssue, BloodRequest, BloodUnit


class IssueError(Exception):
    """Raised when an allocation cannot be issued."""


@transaction.atomic
def issue_blood(allocation_id, issued_by):
    allocation = (
        BloodAllocation.objects.select_for_update()
        .select_related("request", "blood_unit")
        .get(pk=allocation_id)
    )

    if allocation.status != BloodAllocation.Status.ALLOCATED:
        raise IssueError("Only allocated blood can be issued.")

    unit = BloodUnit.objects.select_for_update().get(
        pk=allocation.blood_unit_id
    )

    if unit.status != BloodUnit.Status.ALLOCATED:
        raise IssueError("The blood unit is not currently allocated.")

    if unit.expires_on < timezone.localdate():
        raise IssueError("Expired blood cannot be issued.")

    # The OneToOneField on BloodIssue also prevents duplicate issue records.
    issue = BloodIssue.objects.create(
        allocation=allocation,
        issued_by=issued_by,
    )

    allocation.status = BloodAllocation.Status.ISSUED
    allocation.save(update_fields=["status"])

    unit.status = BloodUnit.Status.ISSUED
    unit.save(update_fields=["status"])

    blood_request = allocation.request
    remaining = blood_request.allocations.exclude(
        status=BloodAllocation.Status.ISSUED
    ).exists()

    if not remaining:
        blood_request.status = BloodRequest.Status.FULFILLED
        blood_request.save(update_fields=["status"])

    return issue
class RequestProcessingError(Exception):
    """Raised when a blood request cannot be processed."""


@transaction.atomic
def process_blood_request(request_id, decision):
    if decision not in (
        BloodRequest.Status.APPROVED,
        BloodRequest.Status.REJECTED,
    ):
        raise RequestProcessingError(
            "Decision must be APPROVED or REJECTED."
        )

    blood_request = BloodRequest.objects.select_for_update().get(
        pk=request_id
    )

    if blood_request.status != BloodRequest.Status.PENDING:
        raise RequestProcessingError(
            "Only pending blood requests can be processed."
        )

    blood_request.status = decision
    blood_request.save(update_fields=["status"])

    return blood_request
