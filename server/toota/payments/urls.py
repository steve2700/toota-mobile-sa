from django.urls import path
from .views import  (PaymentView, flutterwave_webhook, VerifyPaymentView)


urlpatterns = [
    path("verify/", VerifyPaymentView.as_view(), name="verify-payment"),
    path("", PaymentView.as_view(), name="make-payment"),
    path("flutterwave/webhook/", flutterwave_webhook, name="flutterwave-webhook")
]
