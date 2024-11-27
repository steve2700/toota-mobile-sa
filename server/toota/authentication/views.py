import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.tokens import RefreshToken  # For token generation
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import (
    UserSignupSerializer, 
    EmailVerificationSerializer,
    UserLoginSerializer, 
    KYCSerializer,
    ResendOTPSerializer
)

class SignupView(APIView):
    """
    API View to handle user signup.
    This endpoint is used to create a new user account by providing an email and password.
    The user will receive an OTP on their email for verification.
    """

    @swagger_auto_schema(
        operation_description="Register a new user. An OTP will be sent to the user's email for verification.",
        request_body=UserSignupSerializer,
        responses={
            201: openapi.Response("Signup successful. Check your email for OTP."),
            400: "Invalid input or user already exists."
        }
    )
    def post(self, request):
        """
        Handles POST request for user signup.
        """
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Signup successful. Check your email for OTP."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    """
    API View to verify email using OTP.
    This endpoint verifies the email by matching the OTP sent to the user's email.
    """

    @swagger_auto_schema(
        operation_description="Verify the user's email with the OTP sent to the email address.",
        request_body=EmailVerificationSerializer,
        responses={
            200: openapi.Response("Email verified successfully."),
            400: "Invalid email or OTP provided."
        }
    )
    def post(self, request):
        """
        Handles POST request to verify the user's email.
        """
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResendOTPView(APIView):
    """
    API View to handle resending OTP to a user's email.
    """

    @swagger_auto_schema(
        operation_description="Resend OTP to the user's registered email.",
        request_body=ResendOTPSerializer,
        responses={
            200: "OTP sent successfully.",
            400: "Invalid request or too many OTP requests."
        }
    )
    def post(self, request):
        """
        Handle POST request to resend OTP.
        """
        serializer = ResendOTPSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "OTP sent successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

logger = logging.getLogger(__name__)

class LoginView(APIView):
    """
    API View for user login.
    """

    @swagger_auto_schema(
        operation_description="Authenticate the user and provide JWT tokens for access.",
        request_body=UserLoginSerializer,
        responses={
            200: openapi.Response(
                "Login successful, returns JWT tokens (access and refresh).",
                examples={
                    "application/json": {
                        "refresh": "refresh_token_here",
                        "access": "access_token_here"
                    }
                }
            ),
            400: "Invalid email or password."
        }
    )
    def post(self, request):
        logger.info("LoginView POST request received.")
        logger.debug(f"Request data: {request.data}")

        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            logger.info("Serializer validated successfully.")
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            logger.info(f"Tokens generated for user: {user.email}")
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }, status=status.HTTP_200_OK)

        logger.error(f"Login failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# JWT Authentication Header
token_param = openapi.Parameter(
    'Authorization', openapi.IN_HEADER,
    description="Bearer token for authentication",
    type=openapi.TYPE_STRING,
    required=True
)


first_name_param = openapi.Parameter(
    'first_name', openapi.IN_FORM, description="First name", type=openapi.TYPE_STRING, required=True
)

last_name_param = openapi.Parameter(
    'last_name', openapi.IN_FORM, description="Last name", type=openapi.TYPE_STRING, required=True
)

physical_address_param = openapi.Parameter(
    'physical_address', openapi.IN_FORM, description="Physical address", type=openapi.TYPE_STRING, required=True
)

profile_pic_param = openapi.Parameter(
    'profile_pic', openapi.IN_FORM, description="Profile picture file upload", type=openapi.TYPE_FILE, required=False
)

logger = logging.getLogger(__name__)

class KYCUpdateView(APIView):
    """
    API View for updating KYC details.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_description="Update KYC (Know Your Customer) details such as address and profile picture.",
        manual_parameters=[token_param, first_name_param, last_name_param, physical_address_param, profile_pic_param],
        consumes=['multipart/form-data'],  # Specify the content type
        responses={
            200: openapi.Response("KYC updated successfully."),
            400: "Invalid input or missing data.",
            401: "Unauthorized. Authentication credentials were not provided.",
        }
    )
    def patch(self, request):
        logger.info("Received PATCH request for KYC update.")
        logger.debug(f"Request headers: {request.headers}")
        logger.debug(f"Request data: {request.data}")

        # Check authentication
        if not request.user.is_authenticated:
            logger.warning("User is not authenticated.")
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = KYCSerializer(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid():
            logger.info("Serializer validated successfully.")
            serializer.save()
            logger.info("KYC details updated successfully.")
            return Response({"message": "KYC updated successfully."}, status=status.HTTP_200_OK)
        
        logger.error(f"Serializer validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


