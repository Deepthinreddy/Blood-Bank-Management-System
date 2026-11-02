from django.urls import path

from . import frontend_views

urlpatterns = [
    path("", frontend_views.request_list, name="blood-request-list"),
    path(
        "recipients/",
        frontend_views.recipient_list,
        name="recipient-ui-list",
    ),
    path(
        "recipients/<int:recipient_id>/edit/",
        frontend_views.update_recipient,
        name="recipient-ui-update",
    ),
    path(
        "<int:request_id>/process/",
        frontend_views.process_request,
        name="blood-request-process",
    ),
    path(
        "<int:request_id>/allocate/",
        frontend_views.allocate_request,
        name="blood-request-allocate",
    ),
    path(
        "allocations/<int:allocation_id>/issue/",
        frontend_views.issue_allocation,
        name="blood-allocation-issue",
    ),
]
