
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="accounts/login.html"
        ),
        name="login",
    ),
    path(
        "admin-dashboard/",
        views.admin_dashboard,
        name="admin_dashboard",
    ),
        path(
        "admin-reports/",
        views.admin_reports,
        name="admin_reports",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
]
