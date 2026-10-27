from django.shortcuts import render

from .permissions import admin_required


@admin_required
def admin_dashboard(request):
    return render(
        request,
        "accounts/admin_dashboard.html",
    )
