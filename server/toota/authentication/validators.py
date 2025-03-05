from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import User, Driver

def validate_unique_email(value):
    if User.objects.filter(email=value).exists() or Driver.objects.filter(email=value).exists():
        raise ValidationError(_("A user with that email already exists."))

