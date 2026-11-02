
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import AuditRecord, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "is_active",
        "is_staff",
    )
    list_filter = ("role", "is_active", "is_staff")

    fieldsets = UserAdmin.fieldsets + (
        ("BBMS Role", {"fields": ("role",)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("BBMS Role", {"fields": ("role",)}),
    )


@admin.register(AuditRecord)
class AuditRecordAdmin(admin.ModelAdmin):
    list_display = (
        "action",
        "user",
        "ip_address",
        "timestamp",
    )
    list_filter = ("action", "timestamp")
    search_fields = (
        "action",
        "details",
        "user__username",
        "ip_address",
    )
    readonly_fields = (
        "user",
        "action",
        "details",
        "timestamp",
        "ip_address",
    )
