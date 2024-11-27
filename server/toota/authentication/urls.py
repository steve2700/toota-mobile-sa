from django.urls import path
from .views import SignupView, VerifyEmailView, LoginView, KYCUpdateView,  ResendOTPView

urlpatterns = [
    path('signup/user/', SignupView.as_view(), name='signup'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify_email'),
    path('login/user/', LoginView.as_view(), name='login'),
    path('kyc-update/', KYCUpdateView.as_view(), name='kyc_update'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
]

