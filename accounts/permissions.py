from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def is_bbms_admin(user):
    return (
        user.is_authenticated
        and user.is_active
        and user.role == "ADMIN"
    )


def is_operational_staff(user):
    return (
        user.is_authenticated
        and user.is_active
        and (
            user.is_staff
            or user.is_superuser
            or user.role == "ADMIN"
        )
    )


def operational_staff_required(view_func):
    @login_required(login_url="/accounts/login/")
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not is_operational_staff(request.user):
            raise PermissionDenied

        return view_func(request, *args, **kwargs)

    return wrapper


def admin_required(view_func):
    @login_required(login_url="/accounts/login/")
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not is_bbms_admin(request.user):
            raise PermissionDenied

        return view_func(request, *args, **kwargs)

    return wrapper