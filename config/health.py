from django.db import connection
from django.http import JsonResponse


def health_check(request):
    """
    Check whether the application and database are operational.
    Returns HTTP 200 if healthy, otherwise HTTP 503.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()

        return JsonResponse(
            {
                "status": "healthy",
                "database": "connected"
            },
            status=200
        )

    except Exception:
        return JsonResponse(
            {
                "status": "unhealthy",
                "database": "unavailable"
            },
            status=503
        )