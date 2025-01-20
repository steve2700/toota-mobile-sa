from django.urls import path
from .views import SignupView, VerifyEmailView, LoginView, KYCUpdateView,  ResendOTPView,  DriverSignupView, DriverEmailVerificationView, DriverLoginView

urlpatterns = [
    path('signup/user/', SignupView.as_view(), name='signup'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify_email'),
    path('login/user/', LoginView.as_view(), name='login'),
    path('kyc-update/', KYCUpdateView.as_view(), name='kyc_update'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
    path('signup/driver/', DriverSignupView.as_view(), name='driver_signup'),
    path('verify-email/driver/', DriverEmailVerificationView.as_view(), name='driver_verify_email'),
    path('login/driver/', DriverLoginView.as_view(), name='driver_login'),
]

