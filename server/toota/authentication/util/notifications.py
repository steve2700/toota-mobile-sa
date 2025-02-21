from django.core.mail import send_mail
from django.conf import settings

def send_notification(email, subject, message):
    """
    Sends an email notification to the user.
    The sender email is fetched from Django settings.
    """
    send_mail(
        subject, 
        message, 
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False
    )
