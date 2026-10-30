
from django.urls import path

from .views import (
    allocate_request,
    issue_allocation,
    process_request,
    track_request_status,
)

urlpatterns = [
    path(
        "requests/<int:request_id>/allocate/",
        allocate_request,
        name="allocate-request",
    ),
    path(
        "allocations/<int:allocation_id>/issue/",
        issue_allocation,
        name="issue-allocation",
    ),
    path(
        "requests/<int:request_id>/process/",
        process_request,
        name="process-request",
    ),
    path(
        "requests/<int:request_id>/status/",
        track_request_status,
        name="track-request-status",
    ),
]
