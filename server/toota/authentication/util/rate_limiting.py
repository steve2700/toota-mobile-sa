from datetime import timedelta
from django.utils.timezone import now
from authentication.models import IDVerification

def is_rate_limited(user, max_attempts=3, time_period=timedelta(days=1)):
    """
    Rate limiting for user attempts per day 
    """
    time_threshold = now() - time_period
    attempts = IDVerification.objects.filter(user=user, created_at__gte=time_threshold).count()
    return attempts >= max_attempts
