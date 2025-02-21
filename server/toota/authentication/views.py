import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action
from django.core.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.tokens import RefreshToken  # For token generation
from rest_framework.parsers import MultiPartParser, FormParser
from .util.verification import IDAnalyzerService
from .serializers import (
    UserSignupSerializer, 
    EmailVerificationSerializer,
    UserLoginSerializer, 
    KYCSerializer,
    ResendOTPSerializer,
    DriverSignupSerializer,
    DriverEmailVerificationSerializer,
    DriverLoginSerializer,
    IDVerificationSerializer,
    VerificationWarningSerializer,
    VerificationRequestSerializer
)
from .util.verification import IDAnalyzerService
from .util.notifications import send_notification
from .util.rate_limiting import is_rate_limited
from .models import IDVerification,VerificationWarning
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

class IDVerificationViewSet(viewsets.ModelViewSet):
    queryset = IDVerification.objects.all()
    serializer_class = IDVerificationSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Ensure users only access their own verification records."""
        return self.request.user.verifications.all()

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def verify(self, request):
        """
        Verifies the user's ID using an external service and creates a verification record.
        """
        request_serializer = VerificationRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        try:
            analyzer = IDAnalyzerService()
            api_response = analyzer.verify_identity(
                document_url=request_serializer.validated_data['document_url'],
                face_url=request_serializer.validated_data['face_url']
                )
        # Process warnings
            warning_flags = self._process_warnings(api_response.get('warning', []))

        # Construct verification data
            verification_data = self._construct_verification_data(api_response, request.user, warning_flags)

        # Use IDVerificationSerializer explicitly for saving
            verification_serializer = IDVerificationSerializer(data=verification_data)
            verification_serializer.is_valid(raise_exception=True)
            verification = verification_serializer.save()

            warnings = verification.warnings.all()
            warnings_data = VerificationWarningSerializer(warnings, many=True).data

            if verification.is_verified is True:
                return Response({
                    'message': 'Verification completed successfully',
                    'is_verified': True,
                    'verification': verification_serializer.data
                    },status=200)
            elif verification.is_verified is None:
                return Response({
                    'message': 'Verification is pending',
                    'is_verified': None,
                    'verification': verification_serializer.data
                    }, status=202) 
            else:
                return Response({
                    'message': 'Verification failed',
                    'is_verified': False,
                    'verification': verification_serializer.data
                     }, status=400)

        except KeyError as ke:
            return Response({'error': f'Missing expected data: {str(ke)}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'An error occurred during verification: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    def _process_warnings(self, warnings):
    # Default warning flags
        warning_flags = {
            'is_expired': False,
            'is_fake': False,
            'image_edited': False,
            'is_sanctioned': False,
            'has_forgery': False,
            'screen_detected': False,
            'face_verification_failed': False,
            'is_black_white': False
            }
            
        for warning in warnings:
            
            if warning["code"] == "DOCUMENT_EXPIRED":
                warning_flags["is_expired"] = True
            elif warning["code"] == "FAKE_ID":
                warning_flags["is_fake"] = True
            elif warning["code"] == "IMAGE_EDITED":
                warning_flags["image_edited"] = True
            elif warning["code"] == "AML_SANCTION":
                warning_flags["is_sanctioned"] = True
            elif warning["code"] == "IMAGE_FORGERY":
                warning_flags["has_forgery"] = True
            elif warning["code"] == "SCREEN_DETECTED":
                warning_flags["screen_detected"] = True
            elif warning["code"] == "FACE_LIVENESS_ERR":
                warning_flags["face_verification_failed"] = True
            elif warning["code"] == "BLACK_WHITE_DOCUMENT":
                warning_flags["is_black_white"] = True

        return warning_flags
    def _construct_verification_data(self, api_response, user, warning_flags):
        data = api_response.get('data', {})
        return {
            'transaction_id': api_response['transactionId'],
            'success': api_response['success'],
            'execution_time': api_response['executionTime'],
            'review_score': api_response['reviewScore'],
            'reject_score': api_response['rejectScore'],
            'decision': api_response['decision'],
            'first_name': data.get('firstName', [{}])[0].get('value'),
            'last_name': data.get('lastName', [{}])[0].get('value'),
            'document_number': data.get('documentNumber', [{}])[0].get('value'),
            'date_of_birth': data.get('dob', [{}])[0].get('value'),
            'sex': data.get('sex', [{}])[0].get('value'),
            'document_type': data.get('documentType', [{}])[0].get('value'),
            'expiry_date': data.get('expiry', [{}])[0].get('value'),
            'issue_date': data.get('issued', [{}])[0].get('value'),
            'height': data.get('height', [{}])[0].get('value'),
            'weight': data.get('weight', [{}])[0].get('value'),
            'hair_color': data.get('hairColor', [{}])[0].get('value'),
            'address': data.get('address1', [{}])[0].get('value'),
            'state': data.get('stateFull', [{}])[0].get('value'),
            'country': data.get('countryFull', [{}])[0].get('value'),
            **warning_flags,  # Include all warning flags
            'user': user.id
        }

    def _create_warning_records(self, warnings, verification):
        for warning in warnings:
            VerificationWarning.objects.create(
                verification=verification,
                code=warning['code'],
                description=warning['description'],
                severity=warning['severity'],
                confidence=warning['confidence'],
                decision=warning['decision'],
                category=self._categorize_warning(warning['code']),
                additional_data=warning.get('data')
            )

    def _categorize_warning(self, code):
        """
        Categorizes the warning code into document, security, or other.
        """
        categories = {
            'DOCUMENT_EXPIRED': 'document',
            'FAKE_ID': 'document',
            'IMAGE_EDITED': 'document',
            'MISSING_EYE_COLOR': 'document',
            'BLACK_WHITE_DOCUMENT': 'document',
            'AML_SANCTION': 'security',
            'IMAGE_FORGERY': 'security',
            'TEXT_FORGERY': 'security',
            'SCREEN_DETECTED': 'security',
            'FACE_LIVENESS_ERR': 'security'
        }
        return categories.get(code, 'other')
