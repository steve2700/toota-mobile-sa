from django.urls import path
from .views import (
    # User endpoints
    UserSignupView,
    UserLoginView,
    UserForgotPasswordView,
    UserResetPasswordView,
    ProfileView,
    KYCUpdateView,
    
    # Driver endpoints
    DriverSignupView,
    DriverLoginView,
    DriverForgotPasswordView,
    DriverResetPasswordView,
    DriverKYCUpdateView,
    
    # Common endpoints for both users and drivers
    LogoutView,
    ChangePasswordView,
    CommonVerifyEmailView,
    ResendVerificationCodeView,
)

urlpatterns = [
    # User endpoints
    path('signup/user/', UserSignupView.as_view(), name='signup_user'),
    path('login/user/', UserLoginView.as_view(), name='login_user'),
    path('forgot-password/user/', UserForgotPasswordView.as_view(), name='forgot_password_user'),
    path('reset-password/user/', UserResetPasswordView.as_view(), name='reset_password_user'),
    path('profile/user/', ProfileView.as_view(), name='profile_user'),
    path('kyc-update/user/', KYCUpdateView.as_view(), name='kyc_update_user'),  # Update name to be more specific

    # Driver endpoints
    path('signup/driver/', DriverSignupView.as_view(), name='signup_driver'),
    path('login/driver/', DriverLoginView.as_view(), name='login_driver'),
    path('forgot-password/driver/', DriverForgotPasswordView.as_view(), name='forgot_password_driver'),
    path('reset-password/driver/', DriverResetPasswordView.as_view(), name='reset_password_driver'),
    path('kyc-update/driver/', DriverKYCUpdateView.as_view(), name='driver_kyc_update'),  # More clear and descriptive

    # Common endpoints
    path('logout/', LogoutView.as_view(), name='logout'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('verify-email/', CommonVerifyEmailView.as_view(), name='verify_email'),
    path('resend-code/', ResendVerificationCodeView.as_view(), name='resend_code'),
]
