
"""
URL configuration for config project.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("inventory.urls")),
    path("accounts/", include("accounts.urls")),
    path("api/", include("blood_requests.urls")),
    path("api/", include("donors.urls")),
]
