from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import DonorRegistrationSerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def register_donor(request):
    """Register a donor. Only authenticated blood-bank staff may do this."""
    if not (request.user.is_staff or request.user.is_superuser):
        return Response(
            {"detail": "Staff authorization required."},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = DonorRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        donor = serializer.save()
        return Response(
            DonorRegistrationSerializer(donor).data,
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
