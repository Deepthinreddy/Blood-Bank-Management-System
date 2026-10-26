from django.contrib import admin

from .models import Donor


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "blood_group", "phone_number", "email")
    list_filter = ("blood_group",)
    search_fields = ("full_name", "phone_number", "email")
