from rest_framework.permissions import BasePermission
from .models import IDVerification

class IsVerifiedDriver(BasePermission):
    """
    Custom permission to allow access only to verified drivers.
    """

    def has_permission(self, request, view):
        # Ensure the user is authenticated
        if not request.user.is_authenticated:
            return False

        # Fetch the most recent verification record for the user
        verification = IDVerification.objects.filter(user=request.user).order_by('-created_at').first()

        # Grant access only if a verification exists and is verified
        return verification and verification.is_verified
