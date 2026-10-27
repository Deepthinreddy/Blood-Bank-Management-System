from django.urls import path

from .views import register_donor

urlpatterns = [
    path("donors/", register_donor, name="register-donor"),
]
