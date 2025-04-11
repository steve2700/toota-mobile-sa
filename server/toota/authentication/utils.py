import random
import string
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils.timezone import now

# Default OTP validity in minutes; we set it to 60 (1 hour)
DEFAULT_OTP_VALIDITY_MINUTES = getattr(settings, 'OTP_VALIDITY_MINUTES', 60)

def generate_otp(length=4):
    """
    Generate a random numeric OTP of the specified length.
    
    :param length: The length of the OTP; defaults to 4 digits.
    :return: A string representing the generated OTP.
    """
    return ''.join(random.choices(string.digits, k=length))

def _send_email(subject, message, recipient_list, from_email=None):
    """
    Internal helper to send an email using Django's send_mail.
    
    :param subject: Subject of the email.
    :param message: Body message of the email.
    :param recipient_list: List of recipient email addresses.
    :param from_email: Sender's email address; defaults to settings.DEFAULT_FROM_EMAIL.
    :return: Boolean indicating if the email was sent successfully.
    """
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL
    try:
        send_mail(subject, message, from_email, recipient_list)
        return True
    except Exception as e:
        # In production, use proper logging rather than print
        print(f"Error sending email: {e}")
        return False

def send_verification_otp_email(user_email, otp_code, validity_minutes=DEFAULT_OTP_VALIDITY_MINUTES):
    """
    Send an email with the OTP code for email verification.
    
    :param user_email: The recipient's email address.
    :param otp_code: The OTP code to be sent.
    :param validity_minutes: Validity duration (in minutes) for the OTP.
                               Defaults to 60 minutes.
    :return: Boolean indicating if the email was sent successfully.
    """
    subject = "Your Email Verification OTP"
    message = (
        f"Hello,\n\n"
        f"Your OTP for email verification is: {otp_code}\n\n"
        f"This OTP is valid for {validity_minutes} minute{'s' if validity_minutes != 1 else ''}. "
        "Please do not share this code with anyone.\n\n"
        "Thank you for using our service!"
    )
    return _send_email(subject, message, [user_email])

def send_password_reset_otp_email(user_email, otp_code, validity_minutes=DEFAULT_OTP_VALIDITY_MINUTES):
    """
    Send an email with the OTP code for password reset.
    
    :param user_email: The recipient's email address.
    :param otp_code: The OTP code to be sent.
    :param validity_minutes: Validity duration (in minutes) for the OTP.
                               Defaults to 60 minutes.
    :return: Boolean indicating if the email was sent successfully.
    """
    subject = "Your Password Reset OTP"
    message = (
        f"Hello,\n\n"
        f"Your OTP for password reset is: {otp_code}\n\n"
        f"This OTP is valid for {validity_minutes} minute{'s' if validity_minutes != 1 else ''}. "
        "If you did not request a password reset, please ignore this email.\n\n"
        "Thank you!"
    )
    return _send_email(subject, message, [user_email])

def is_otp_valid(otp_obj, provided_otp, validity_duration=timedelta(minutes=DEFAULT_OTP_VALIDITY_MINUTES)):
    """
    Check if the provided OTP is valid within the specified duration.
    
    :param otp_obj: An object representing the OTP, expected to have 'code' and 'created_at' attributes.
    :param provided_otp: The OTP code provided by the user.
    :param validity_duration: A timedelta indicating how long the OTP is valid.
    :return: True if the OTP is correct and not expired, False otherwise.
    """
    return otp_obj.code == provided_otp and (now() - otp_obj.created_at) <= validity_duration


def send_kyc_submission_email(driver_email):
    """
    Send an email to the driver after they complete the KYC process.
    Informs the driver that the admin team will review their details.
    """
    subject = "Driver KYC Application Submitted"
    message = (
        f"Dear Driver,\n\n"
        f"Thank you for submitting your KYC details. Our admin team is currently reviewing your application.\n\n"
        "You will be notified once the review process is complete.\n\n"
        "Thank you for using our platform!"
    )

    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [driver_email])
    except Exception as e:
        # Log the error if sending the email fails
        logging.error(f"Error sending email to {driver_email}: {e}")
        return False
    return True
