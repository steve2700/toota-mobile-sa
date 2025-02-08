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
    ResendOTPSerializer,
    DriverSignupSerializer,
    DriverEmailVerificationSerializer,
    DriverLoginSerializer,
    DriverCheckSerializer
)
from .util.verification import (extract_text, compare_faces, 
                                extract_expiry_date,validate_expiry,
                                get_dynamic_threshold,detect_watermark)
from .util.audit_logs import log_verification_attempt
from .util.notifications import send_notification
from .util.rate_limiting import is_rate_limited
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

# Driver Signup View
class DriverSignupView(APIView):
    """
    API View to handle driver signup.
    """

    @swagger_auto_schema(
        operation_description="Register a new driver. An OTP will be sent to the driver's email for verification.",
        request_body=DriverSignupSerializer,
        responses={
            201: openapi.Response("Signup successful. Check your email for OTP."),
            400: "Invalid input or driver already exists."
        }
    )
    def post(self, request):
        serializer = DriverSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Signup successful. Check your email for OTP."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Driver Email Verification View
class DriverEmailVerificationView(APIView):
    """
    API View to verify driver's email using OTP.
    """

    @swagger_auto_schema(
        operation_description="Verify the driver's email with the OTP sent to the email address.",
        request_body=DriverEmailVerificationSerializer,
        responses={
            200: openapi.Response("Email verified successfully."),
            400: "Invalid email or OTP provided."
        }
    )
    def post(self, request):
        serializer = DriverEmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Driver Login View
class DriverLoginView(APIView):
    """
    API View for driver login.
    """

    @swagger_auto_schema(
        operation_description="Authenticate the driver and provide JWT tokens for access.",
        request_body=DriverLoginSerializer,
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
        logger.info("DriverLoginView POST request received.")
        logger.debug(f"Request data: {request.data}")

        serializer = DriverLoginSerializer(data=request.data)
        if serializer.is_valid():
            logger.info("Serializer validated successfully.")
            driver = serializer.validated_data['driver']
            refresh = RefreshToken.for_user(driver)
            logger.info(f"Tokens generated for driver: {driver.email}")
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }, status=status.HTTP_200_OK)

        logger.error(f"Login failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class DriverCheckView(APIView):
    """
    API View for driver KYC authentication with encrypted storage.
    """
    def post(self, request, *args, **kwargs):
        # Rate Limiting Check
        if is_rate_limited(request.user):
            return Response({"message": "Rate limit exceeded. Try again later."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        serializer = DriverCheckSerializer(data=request.data)
        if serializer.is_valid():
            driver_check = serializer.save()

            # Extract text and expiry date from the document
            document_image_path = driver_check.uploaded_image.path
            extracted_text = extract_text(document_image_path)
            extracted_expiry_date = extract_expiry_date(document_image_path)

            if not extracted_expiry_date:
                return Response({"message": "Could not extract expiry date from the document."}, status=status.HTTP_400_BAD_REQUEST)

            # Validate expiry date
            if not validate_expiry(extracted_expiry_date):
                log_verification_attempt(request.user, status=False, reason="Expired document.")
                send_notification(request.user.email, "Verification Failed", "Your document has expired.")
                return Response({"message": "Verification failed. Document expired."}, status=status.HTTP_400_BAD_REQUEST)
            if not detect_watermark(document_image_path):
                return Response({"message": "Verification failed. No watermark detected on the document."}, status=status.HTTP_400_BAD_REQUEST)
            # Geo-Location Verification
            # user_location = request.data.get("location")  # Assume location is sent in the request
            # if not validate_geo_location(user_location):
            #     log_verification_attempt(request.user, status=False, reason="Invalid location.")
            #     return Response({"message": "Verification failed. Invalid location."}, status=status.HTTP_400_BAD_REQUEST)

            # Perform text match
            if driver_check.name.lower() in extracted_text.lower():
                # Use the uploaded face image for face comparison
                face_image_path = driver_check.face_image.path
                face_match_score = compare_faces(document_image_path, face_image_path)
                dynamic_threshold = get_dynamic_threshold(request.user)
                
                if face_match_score >= dynamic_threshold:
                    driver_check.is_verified = True
                    driver_check.extracted_text = extracted_text  # Encrypt extracted text
                    driver_check.expiry_date = extracted_expiry_date  # Encrypt expiry date
                    driver_check.save()

                    log_verification_attempt(request.user, status=True)
                    send_notification(request.user.email, "Verification Successful", "Your verification was successful.")
                    return Response({"message": "Verification successful. Name, face, and expiry date match."}, status=status.HTTP_200_OK)
                else:
                    log_verification_attempt(request.user, status=False, reason="Face does not match.")
                    send_notification(request.user.email, "Verification Failed", "Your face does not match the document.")
                    return Response({"message": "Verification failed. Face does not match."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                log_verification_attempt(request.user, status=False, reason="Name does not match.")
                return Response({"message": "Verification failed. Name does not match."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
