from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import AuthenticationFailed

User = get_user_model()

class CustomJWTAuthentication(JWTAuthentication):
    user_id_claim = 'user_id'
    def get_user(self, validated_token):
        try:
            user_id = validated_token[self.user_id_claim]
        except KeyError:
            raise AuthenticationFailed('Token contained no recognizable user identification')

        try:
            # If your ID is a UUID, no conversion needed
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found')

        if not user.is_active:
            raise AuthenticationFailed('User is inactive')

        return user
