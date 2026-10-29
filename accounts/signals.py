
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from .models import AuditRecord


def get_client_ip(request):
    if request is None:
        return None

    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


@receiver(user_logged_in)
def record_login(sender, request, user, **kwargs):
    AuditRecord.objects.create(
        user=user,
        action="LOGIN",
        details="User logged in successfully.",
        ip_address=get_client_ip(request),
    )


@receiver(user_logged_out)
def record_logout(sender, request, user, **kwargs):
    AuditRecord.objects.create(
        user=user,
        action="LOGOUT",
        details="User logged out.",
        ip_address=get_client_ip(request),
    )
