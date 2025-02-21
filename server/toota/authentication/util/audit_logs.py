# from .models import DriverCheck
# from django.utils.timezone import now

# def log_verification_attempt(user, status, reason=None):
#     """ Audit log based on driver verification """
#     DriverCheck.objects.create(
#         user=user,
#         created_at=now(),
#         is_verified=status,
#         reason=reason or "No reason provided."
#     )
