from django.urls import path

from .views import (
    register_donor,
    donor_list,
    donor_detail,
    update_donor,
)

urlpatterns = [
    path("donors/", register_donor, name="register-donor"),
    path("donors/list/", donor_list, name="donor-list"),
    path("donors/<int:donor_id>/", donor_detail, name="donor-detail"),
    path("donors/<int:donor_id>/update/", update_donor, name="update-donor"),
]