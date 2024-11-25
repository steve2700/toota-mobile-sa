from django.core.mail import send_mail
from django.conf import settings
import random
import string

def generate_otp(length=4):
    """
    Generate a random numeric OTP of the specified length.
    :param length: Length of the OTP, defaults to 4 digits.
    :return: A string representing the generated OTP.
    """
    return ''.join(random.choices(string.digits, k=length))

def send_otp_email(user_email, otp_code):
    """
    Send an email with the OTP code to the specified user.
    :param user_email: The email address of the recipient.
    :param otp_code: The OTP code to be sent.
    :return: Boolean indicating if the email was sent successfully.
    """
    subject = "Your Email Verification OTP"
    message = f"""
    Hello,

    Your OTP for email verification is: {otp_code}

    This OTP is valid for 1 hour. Please do not share this code with anyone.

    Thank you for using Toota!
    """
    from_email = settings.DEFAULT_FROM_EMAIL

    try:
        send_mail(subject, message, from_email, [user_email])
        return True
    except Exception as e:
        # Optionally log the error here
        print(f"Error sending email: {e}")
        return False

