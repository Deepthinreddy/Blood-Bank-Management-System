from django.urls import path

from .views import (
    register_donor,
    donor_list,
    donor_detail,
    update_donor,
    donor_donation_history,
)

urlpatterns = [
    path("donors/", register_donor, name="register-donor"),
    path("donors/list/", donor_list, name="donor-list"),
    path("donors/<int:donor_id>/", donor_detail, name="donor-detail"),
    path("donors/<int:donor_id>/update/", update_donor, name="update-donor"),
    path(
        "donors/<int:donor_id>/donations/",
        donor_donation_history,
        name="donor-donation-history",
    ),
]