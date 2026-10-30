"""
URL configuration for config project.
"""

from django.contrib import admin
from django.urls import include, path
from config.health import health_check

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("api/", include("blood_requests.urls")),
    path("api/", include("donors.urls")),
    path("health/", health_check, name="health_check"),
]