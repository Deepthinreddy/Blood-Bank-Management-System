
from django.urls import path

from .views import allocate_request, issue_allocation

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
]
