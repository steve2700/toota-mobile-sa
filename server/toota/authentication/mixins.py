from encrypted_model_fields.fields import EncryptedFieldMixin
from django.conf import settings

class MyEncryptedFieldMixin(EncryptedFieldMixin):
    encryption_key = settings.FIELD_ENCRYPTION_KEY
