import logging
from datetime import timedelta

from django.utils.timezone import now
from django.contrib.auth.hashers import check_password
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics,permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import  User, Driver
from .serializers import (
    UserSignupSerializer,
    EmailVerificationSerializer,
    UserLoginSerializer,
    ResendOTPSerializer,
    UserProfileSerializer,
    DriverSignupSerializer,
    DriverLoginSerializer,
    KYCUpdateSerializer
)
from .utils import generate_otp, send_password_reset_otp_email, send_verification_otp_email 
logger = logging.getLogger(__name__)

###############################################################################
# Base Views for Signup, Login, Forgot & Reset Password
###############################################################################

class BaseSignupView(APIView):
    """
    Base view for handling signup.
    Expects a serializer_class attribute and returns a success message upon creation.
    """
    serializer_class = None
    success_message = "Signup successful. Check your email for OTP."

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Generate OTP
            otp = generate_otp()
            # Assuming your User model has 'otp' and 'otp_created_at' fields
            user.otp = otp
            user.otp_created_at = now()
            user.save()
            # Send OTP via email
            email_sent = send_verification_otp_email(user.email, otp)
            if email_sent:
                return Response({"message": self.success_message},
                                status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "Failed to send OTP email. Please try again."},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BaseLoginView(APIView):
    """
    Base view for handling login.
    Expects a serializer_class attribute that validates and returns a user.
    """
    serializer_class = None

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BaseForgotPasswordView(APIView):
    """
    Base view for handling forgot password.
    Expects a model_class attribute (User or Driver) that has 'otp' and 'otp_created_at'.
    """
    model_class = None

    def post(self, request):
        email = request.data.get("email")
        try:
            obj = self.model_class.objects.get(email=email)
            reset_otp = generate_otp()
            obj.otp = reset_otp
            obj.otp_created_at = now()
            obj.save()
            send_password_reset_otp(obj.email, reset_otp)
            return Response({"message": "OTP sent to email for password reset."},
                            status=status.HTTP_200_OK)
        except self.model_class.DoesNotExist:
            return Response({"error": "User not found."},
                            status=status.HTTP_404_NOT_FOUND)


class BaseResetPasswordView(APIView):
    """
    Base view for handling password reset using OTP.
    Expects a model_class attribute (User or Driver) with 'otp' and 'otp_created_at'.
    """
    model_class = None

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        new_password = request.data.get("new_password")
        try:
            obj = self.model_class.objects.get(email=email)
            otp_validity_duration = timedelta(minutes=5)
            if obj.otp == otp and now() - obj.otp_created_at <= otp_validity_duration:
                obj.set_password(new_password)
                obj.otp = None  # Clear OTP after successful reset
                obj.save()
                return Response({"message": "Password reset successful."},
                                status=status.HTTP_200_OK)
            return Response({"error": "Invalid or expired OTP."},
                            status=status.HTTP_400_BAD_REQUEST)
        except self.model_class.DoesNotExist:
            return Response({"error": "User not found."},
                            status=status.HTTP_404_NOT_FOUND)

###############################################################################
# User Endpoints
###############################################################################

class UserSignupView(BaseSignupView):
    serializer_class = UserSignupSerializer
    success_message = "User signup successful. Check your email for OTP."

    @swagger_auto_schema(
        request_body=UserSignupSerializer,
        responses={
            201: "Signup successful. Check your email for OTP.",
            400: "Invalid input or user already exists."
        }
    )
    def post(self, request):
        return super().post(request)


class UserLoginView(BaseLoginView):
    serializer_class = UserLoginSerializer

    @swagger_auto_schema(
        request_body=UserLoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful. Returns JWT tokens.",
                examples={"application/json": {
                    "refresh": "refresh_token_here",
                    "access": "access_token_here"
                }}
            ),
            400: "Invalid email or password."
        }
    )
    def post(self, request):
        return super().post(request)


class UserForgotPasswordView(BaseForgotPasswordView):
    model_class = User

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description="User email")
            },
            required=['email']
        ),
        responses={200: "OTP sent to email for password reset.", 404: "User not found."}
    )
    def post(self, request):
        return super().post(request)


class UserResetPasswordView(BaseResetPasswordView):
    model_class = User

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description="User email"),
                'otp': openapi.Schema(type=openapi.TYPE_STRING, description="OTP received via email"),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, description="New password"),
            },
            required=['email', 'otp', 'new_password']
        ),
        responses={
            200: "Password reset successful.",
            400: "Invalid or expired OTP.",
            404: "User not found."
        }
    )
    def post(self, request):
        return super().post(request)


class ProfileView(APIView):
    """
    Endpoint for client users to retrieve and update their profile.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: UserProfileSerializer()}
    )
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=UserProfileSerializer,
        responses={
            200: "Profile updated successfully.",
            400: "Invalid input."
        }
    )
    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully."},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

###############################################################################
# Driver Endpoints
###############################################################################

class DriverSignupView(BaseSignupView):
    serializer_class = DriverSignupSerializer
    success_message = "Driver signup successful. Check your email for OTP."

    @swagger_auto_schema(
        request_body=DriverSignupSerializer,
        responses={
            201: "Driver signup successful. Check your email for OTP.",
            400: "Invalid input or driver already exists."
        }
    )
    def post(self, request):
        return super().post(request)


class DriverLoginView(BaseLoginView):
    serializer_class = DriverLoginSerializer

    @swagger_auto_schema(
        request_body=DriverLoginSerializer,
        responses={
            200: openapi.Response(
                description="Driver login successful. Returns JWT tokens.",
                examples={"application/json": {
                    "refresh": "refresh_token_here",
                    "access": "access_token_here"
                }}
            ),
            400: "Invalid email or password."
        }
    )
    def post(self, request):
        return super().post(request)


class DriverForgotPasswordView(BaseForgotPasswordView):
    model_class = Driver

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description="Driver email")
            },
            required=['email']
        ),
        responses={200: "OTP sent to email for password reset.", 404: "Driver not found."}
    )
    def post(self, request):
        return super().post(request)


class DriverResetPasswordView(BaseResetPasswordView):
    model_class = Driver

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description="Driver email"),
                'otp': openapi.Schema(type=openapi.TYPE_STRING, description="OTP received via email"),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, description="New password"),
            },
            required=['email', 'otp', 'new_password']
        ),
        responses={
            200: "Password reset successful.",
            400: "Invalid or expired OTP.",
            404: "Driver not found."
        }
    )
    def post(self, request):
        return super().post(request)

###############################################################################
# Common Endpoints for Both Users & Drivers
###############################################################################

class LogoutView(APIView):
    """
    Endpoint to logout an authenticated user (client or driver) by blacklisting the refresh token.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh_token': openapi.Schema(type=openapi.TYPE_STRING, description="Refresh token")
            },
            required=['refresh_token']
        ),
        responses={
            200: "Logout successful.",
            400: "Invalid token or already blacklisted."
        }
    )
    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response({"error": "Refresh token is required."},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful."},
                            status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Invalid token or already blacklisted."},
                            status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """
    Endpoint for authenticated users (client or driver) to change their password.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'old_password': openapi.Schema(type=openapi.TYPE_STRING, description="Current password"),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, description="New password"),
            },
            required=['old_password', 'new_password']
        ),
        responses={
            200: "Password changed successfully.",
            400: "Invalid old password or input."
        }
    )
    def post(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        if not check_password(old_password, user.password):
            return Response({"error": "Old password is incorrect."},
                            status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        return Response({"message": "Password changed successfully."},
                        status=status.HTTP_200_OK)


class CommonVerifyEmailView(APIView):
    """
    Common endpoint to verify a user's email (for both client users and drivers).
    Expects 'email' and 'otp' in the request.
    """
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description="User email"),
                'otp': openapi.Schema(type=openapi.TYPE_STRING, description="OTP code")
            },
            required=['email', 'otp']
        ),
        responses={
            200: "Email verified successfully.",
            400: "Invalid or expired OTP, or email not found."
        }
    )
    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        if not email or not otp:
            return Response({"error": "Email and OTP are required."},
                            status=status.HTTP_400_BAD_REQUEST)
        user_obj = None
        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            try:
                user_obj = Driver.objects.get(email=email)
            except Driver.DoesNotExist:
                return Response({"error": "User not found."},
                                status=status.HTTP_404_NOT_FOUND)
        
        otp_validity_duration = timedelta(minutes=5)
        if user_obj.otp != otp or (now() - user_obj.otp_created_at) > otp_validity_duration:
            return Response({"error": "Invalid or expired OTP."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        user_obj.is_active = True
        user_obj.otp = None
        user_obj.save()
        return Response({"message": "Email verified successfully."},
                        status=status.HTTP_200_OK)


class ResendVerificationCodeView(APIView):
    """
    Common endpoint to resend the verification OTP code for email verification
    for both client users and drivers. Expects 'email' in the request.
    """
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description="User email")
            },
            required=['email']
        ),
        responses={
            200: "Verification code resent successfully.",
            404: "User not found."
        }
    )
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        user_obj = None
        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            try:
                user_obj = Driver.objects.get(email=email)
            except Driver.DoesNotExist:
                return Response({"error": "User not found."},
                                status=status.HTTP_404_NOT_FOUND)
        
        new_otp = generate_otp()
        user_obj.otp = new_otp
        user_obj.otp_created_at = now()
        user_obj.save()
        send_verification_otp_email(user_obj.email, new_otp)
        return Response({"message": "Verification code resent successfully."},
                        status=status.HTTP_200_OK)

class KYCUpdateView(generics.UpdateAPIView):
    """
    Endpoint for updating KYC details for the authenticated client user.
    Allows updating first name, last name, physical address, phone number, and profile picture.
    """
    queryset = User.objects.all()
    serializer_class = KYCUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    @swagger_auto_schema(
        operation_description="Update KYC details for the authenticated user. Fields include first name, last name, physical address, phone number, and profile picture.",
        request_body=KYCUpdateSerializer,
        responses={
            200: openapi.Response("KYC update successful."),
            400: "Invalid input data."
        }
    )
    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "KYC update successful."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

