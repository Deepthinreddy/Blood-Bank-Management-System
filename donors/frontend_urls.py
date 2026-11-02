from django.urls import path

from . import frontend_views

urlpatterns = [
    path("", frontend_views.donor_list, name="donor-ui-list"),
    path("register/", frontend_views.register_donor, name="donor-ui-register"),
    path("<int:donor_id>/", frontend_views.donor_detail, name="donor-ui-detail"),
    path(
        "<int:donor_id>/edit/",
        frontend_views.update_donor,
        name="donor-ui-update",
    ),
]
