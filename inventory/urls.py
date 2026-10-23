
from django.urls import path
from . import views

urlpatterns = [
    path("donations/new/", views.donation_create, name="donation_create"),
    path("inventory/", views.inventory_list, name="inventory_list"),
]
