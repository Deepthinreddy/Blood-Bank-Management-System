
from django.urls import path

from .views import (
    allocate_request,
    issue_allocation,
    process_request,
    recipient_list,
    recipient_detail,
    create_blood_request,
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
        "requests/create/",
        create_blood_request,
        name="create-blood-request",
    ),
    path("recipients/", recipient_list, name="recipient-list"),
    path("recipients/<int:recipient_id>/", recipient_detail, name="recipient-detail"),
]
