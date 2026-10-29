import time

from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect


class SessionInactivityMiddleware:
    """
    Log out authenticated users after a period of inactivity.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.timeout = getattr(
            settings,
            "SESSION_INACTIVITY_TIMEOUT",
            1800,
        )

    def __call__(self, request):
        if request.user.is_authenticated:
            now = time.time()
            last_activity = request.session.get("last_activity")

            if last_activity is not None:
                if now - last_activity > self.timeout:
                    logout(request)
                    return redirect(settings.LOGIN_URL)

            request.session["last_activity"] = now

        response = self.get_response(request)
        return response