from django.shortcuts import render
import logging, requests, uuid, json
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from dotenv import load_dotenv
import hmac
import hashlib
from django.shortcuts import get_object_or_404
import os
from trips.models import Trip
from payments.models import Payment
from .serializers import PaymentSerializer

load_dotenv()
logger = logging.getLogger(__name__)
# -------------------------------
# Payment Initialization Endpoint
# -------------------------------
class PaymentView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_summary="Initiate Payment for a Trip",
        operation_description="""
            This endpoint initiates a payment for a specified trip.
            
            - If `cash` is selected as the payment method, the driver will confirm receipt.
            - For methods like `card`, `mobile_money`, and `bank_transfer`, the payment link will be generated via Flutterwave.
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['trip_id', 'payment_method', 'currency', 'location'],
            properties={
                'trip_id': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format='uuid',
                    description='UUID of the trip to be paid for'
                ),
                'payment_method': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Payment method (cash, card, mobile_money, bank_transfer)"
                ),
                'currency': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Currency for the payment (e.g., NGN, ZA)"
                ),
                'location': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="country code (e.g., NG, ZA)"
                )
            },
            example={
                "trip_id": 1,
                "payment_method": "card",
                "currency": "NGN"
            }
        ),
        responses={
            200: openapi.Response(
                description="Payment initialized successfully",
                examples={
                    "application/json": {
                        "message": "Payment initialized successfully",
                        "payment_link": "https://flutterwave.com/pay/xyz",
                        "transaction_id": "8c33a5e8-4275-4d4f-94ae-f3b5b093a0c4"
                    }
                }
            ),
            400: openapi.Response(
                description="Bad request or failed initialization",
                examples={
                    "application/json": {
                        "error": "Failed to initialize payment",
                        "details": {
                            "trip_id": ["This field is required."]
                        }
                    }
                }
            ),
            503: openapi.Response(
                description="Payment service unavailable",
                examples={
                    "application/json": {
                        "error": "Payment service unavailable",
                        "details": "Request timeout"
                    }
                }
            )
        }
    )
    def post(self, request):
        serializer = PaymentSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(
                {"error": "Invalid input data", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        trip_id = serializer.validated_data["trip_id"]
        payment_method = serializer.validated_data["payment_method"]
        currency = serializer.validated_data["currency"]
        location = serializer.validated_data["location"]

        trip = get_object_or_404(Trip, id=trip_id)
        amount = trip.accepted_fare
        if amount is None:
            return Response({"error": "Trip has no accepted fare set."}, status=status.HTTP_400_BAD_REQUEST)
        transaction_id = str(uuid.uuid4())

        payment = serializer.save(amount=amount, transaction_id=transaction_id)

        if payment_method == "cash":
            return Response(
                {"message": "Cash payment selected. Driver will confirm receipt."},
                status=status.HTTP_200_OK
            )

        elif payment_method in ["card", "mobile_money", "bank_transfer"]:
            host = request.get_host()
            protocol = "https" if request.is_secure() else "http"
            base_url = f"{protocol}://{host}"

            full_name = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.email


            PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
            PAYSTACK_BASE_URL = os.getenv("PAYSTACK_BASE_URL")
            FLUTTERWAVE_BASE_URL = os.getenv("FLUTTERWAVE_BASE_URL")
            FLUTTERWAVE_SECRET_KEY = os.getenv("FLUTTERWAVE_SECRET_KEY")


            if location == "NG":
                # Flutterwave
                url = f"{FLUTTERWAVE_BASE_URL}/payments"
                payment.gateway = "flutterwave"
                payment.save()

                payment_data = {
                    "tx_ref": transaction_id,
                    "amount": str(amount),
                    "currency": currency,
                    "redirect_url": f"{base_url}/payment/verify/",
                    "meta": {
                        "trip_id": str(trip_id),
                        "user_id": str(request.user.id)
                    },
                    "customer": {
                        "email": request.user.email,
                        "name": full_name,
                        "phone_number": str(getattr(request.user, 'phone_number', "")).strip()
                    },
                    "customizations": {
                        "title": "Trip Payment",
                        "description": f"Payment for trip #{trip_id}",
                        "logo": ""  # optional, can be omitted if empty
                    }
                }
                headers = {
                    "Authorization": f"Bearer {FLUTTERWAVE_SECRET_KEY}",
                    "Content-Type": "application/json"
                }

            else:
                # Paystack
                url = f"{PAYSTACK_BASE_URL}/transaction/initialize"
                payment.gateway = "paystack"
                payment.save()

                payment_data = {
                    "email": request.user.email,
                    "amount": int(amount) * 100,  # Convert to kobo
                    "callback_url": f"{base_url}/payment/verify/",
                    "reference": transaction_id,
                    "metadata": {
                        "trip_id": str(trip_id),
                        "user_id": str(request.user.id)
                    }
                }
                headers = {
                    "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
                    "Content-Type": "application/json"
                }

            # Call the payment API
            try:
                response = requests.post(url, json=payment_data, headers=headers)
                res_data = response.json()


                # Handle response based on gateway
                if location == "NG":
                    if response.status_code == 200 and res_data.get("status") in ["success", True]:
                        return Response({
                            "message": "Payment initialized successfully",
                            "payment_link": res_data["data"]["link"],  # Flutterwave uses "link"
                            "transaction_id": transaction_id
                        }, status=status.HTTP_200_OK)
                else:
                    if response.status_code == 200 and res_data.get("status") in ["success", True]:
                        return Response({
                            "message": "Payment initialized successfully",
                            "payment_link": res_data["data"]["authorization_url"],
                            "transaction_id": transaction_id
                        }, status=status.HTTP_200_OK)

                # If we got here, something failed
                payment.status = "failed"
                payment.save()
                return Response({
                    "error": "Failed to initialize payment",
                    "details": res_data
                }, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                # Handle unexpected exceptions
                payment.status = "failed"
                payment.save()
                return Response({
                    "error": "An error occurred during payment initialization",
                    "details": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            return Response({"error": "Unsupported payment method"}, status=status.HTTP_400_BAD_REQUEST)

# -------------------------------
# Payment Verification Endpoint
# -------------------------------
class VerifyPaymentView(APIView):
    permission_classes = []  # Public access for redirects and manual checks
    @swagger_auto_schema(
        operation_description="Handle Flutterwave redirect verification",
        manual_parameters=[
            openapi.Parameter('tx_ref', openapi.IN_QUERY, description="Transaction reference", type=openapi.TYPE_STRING),
            openapi.Parameter('transaction_id', openapi.IN_QUERY, description="Transaction ID", type=openapi.TYPE_STRING),
            openapi.Parameter('status', openapi.IN_QUERY, description="Payment status", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response(
                description="Payment verification successful",
                examples={
                    "application/json": {
                        "status": "success",
                        "message": "Payment successful.",
                        "transaction_reference": "tx_ref",
                        "payment_reference": "payment_reference",
                        "payment_method": "payment_method",
                        "amount": 100.0,
                        "currency": "NGN",
                        "trip_id": "trip_id"
                    }
                }
            ),
            400: openapi.Response(
                description="Payment verification failed",
                examples={
                    "application/json": {
                        "status": "failed",
                        "message": "Payment not successful",
                    }
                }
            ),
            404: openapi.Response(
                description="Trip not found",
                examples={
                    "application/json": {
                        "error": "Trip not found"
                    }
                }
            ),
        }
    )
    def get(self, request):
        """
        Handle payment verification for both Flutterwave and Paystack.
        """
        tx_ref = request.GET.get('tx_ref') or request.GET.get('trxref')
        transaction_id = request.GET.get("transaction_id") if request.GET.get("transaction_id") else tx_ref

        status_param = request.GET.get('status') if request.GET.get('status') else None

        if not tx_ref:
            return Response({"error": "Missing transaction reference"}, status=400)

        try:
            payment = Payment.objects.get(transaction_id=tx_ref)
        except Payment.DoesNotExist:
            return Response({"error": "Invalid transaction reference"}, status=400)

        trip_id = payment.trip_id
        try:
            trip = Trip.objects.get(id=trip_id)
        except Trip.DoesNotExist:
            return Response({"error": "Trip not found"}, status=404)

        # Handle user cancellation
        if status_param == 'cancelled':
            payment.status = 'failed'
            payment.save()
            return Response({
                "status": "failed",
                "message": "Payment not successful",
            }, status=400)

        # Determine the payment gateway
        if payment.gateway == "flutterwave":
            BASE_URL = os.getenv("FLUTTERWAVE_BASE_URL")
            SECRET_KEY = os.getenv("FLUTTERWAVE_SECRET_KEY")
            verify_url = f"{BASE_URL}/transactions/{transaction_id}/verify"
        elif payment.gateway == "paystack":
            BASE_URL = os.getenv("PAYSTACK_BASE_URL")
            SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
            verify_url = f"{BASE_URL}/transaction/verify/{transaction_id}"
        else:
            return Response({"error": "Unsupported payment gateway"}, status=400)

        headers = {
            "Authorization": f"Bearer {SECRET_KEY}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(verify_url, headers=headers)
            res_data = response.json()
            if response.status_code == 200 and res_data.get("status") in ["success", True]:
                payment_data = res_data["data"]

                if payment_data.get("status") in ["successful", "success"] and float(payment_data.get('amount')) == float(payment.amount):
                    payment.status = "success"
                    trip.is_paid = True
                    trip.save()
                    payment.payment_reference = str(transaction_id)
                    payment.save()
                    return Response({
                        "status": "success",
                        "message": "Payment successful.",
                        "transaction_reference": tx_ref,
                        "payment_reference": payment.payment_reference,
                        "payment_method": payment.payment_method,
                        "amount": payment.amount,
                        "currency": payment.currency,
                        "trip_id": str(payment.trip_id)
                    }, status=200)

            # If payment is not successful
            payment.status = "failed"
            payment.save()
            return Response({
                "status": "failed",
                "message": "Payment not successful",
            }, status=400)

        except requests.RequestException as e:
            return Response({
                "status": "failed",
                "message": "Payment verification service unavailable",
                "details": str(e)
            }, status=503)



    @swagger_auto_schema(
        operation_description="Manual Payment Verification by transaction_id",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['transaction_id'],
            properties={
                'transaction_id': openapi.Schema(type=openapi.TYPE_STRING, description='Transaction ID'),
            },
            example={
                "transaction_id": "transaction_id"
            }
        ),
        responses={
            200: openapi.Response(
                description="Payment already verified as successful",
                examples={
                    "application/json": {
                        "message": "Payment already verified as successful"
                    }
                }
            ),
            400: openapi.Response(
                description="Invalid transaction_id",
                examples={
                    "application/json": {
                        "error": "Invalid transaction_id"
                    }
                }
            ),
            404: openapi.Response(
                description="Trip not found",
                examples={
                    "application/json": {
                        "error": "Trip not found"
                    }
                }
            ),
            503: openapi.Response(
                description="Payment verification service unavailable",
                examples={
                    "application/json": {
                        "error": "Payment verification service unavailable",
                        "details": "Request timeout"
                    }
                }
            )
        }
    )
    def post(self, request):
        """
        Manual Payment Verification by transaction_id
        """
        transaction_id = request.data.get('transaction_id')

        if not transaction_id:
            return Response({"error": "transaction_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
        except Payment.DoesNotExist:
            return Response({"error": "Invalid transaction_id"}, status=status.HTTP_400_BAD_REQUEST)

        trip_id = payment.trip_id
        try:
            trip = Trip.objects.get(id=trip_id)
        except Trip.DoesNotExist:
            return Response({"error": "Trip not found"}, status=status.HTTP_404_NOT_FOUND)

        if payment.status == 'success':
            return Response({"message": "Payment already verified as successful"}, status=status.HTTP_200_OK)

        payment_gateway = payment.gateway  # Assuming you store the gateway used ("flutterwave" or "paystack")

        if payment_gateway == "flutterwave":
            FLUTTERWAVE_BASE_URL = os.getenv("FLUTTERWAVE_BASE_URL")
            FLUTTERWAVE_SECRET_KEY = os.getenv("FLUTTERWAVE_SECRET_KEY")
            verify_url = f"{FLUTTERWAVE_BASE_URL}/transactions/verify_by_reference?tx_ref={transaction_id}"
            headers = {
                "Authorization": f"Bearer {FLUTTERWAVE_SECRET_KEY}",
                "Content-Type": "application/json"
            }
        elif payment_gateway == "paystack":
            PAYSTACK_BASE_URL = os.getenv("PAYSTACK_BASE_URL", "https://api.paystack.co")
            PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
            verify_url = f"{PAYSTACK_BASE_URL}/transaction/verify/{transaction_id}"
            headers = {
                "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
                "Content-Type": "application/json"
            }
        else:
            return Response({"error": "Unknown payment gateway"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            response = requests.get(verify_url, headers=headers)
            res_data = response.json()

            if response.status_code == 200 and res_data.get("status") in ["success", True]:
                if payment_gateway == "flutterwave":
                    payment_status = res_data["data"]["status"]
                else:  # Paystack
                    payment_status = res_data["data"]["status"]

                if payment_status in ["successful", "success"] and float(payment_data.get('amount')) == float(payment.amount):
                    payment.status = "success"
                    payment.payment_reference = str(res_data["data"].get("id", ""))
                    trip.is_paid = True
                    trip.save()
                    payment.save()
                    return Response({
                        "status": "success",
                        "message": "Payment successful",
                        "transaction_reference": transaction_id,
                        "payment_reference": payment.payment_reference,
                        "payment_method": payment.payment_method,
                        "amount": payment.amount,
                        "currency": payment.currency,
                        "trip_id": str(payment.trip_id)
                    }, status=status.HTTP_200_OK)

                payment.status = "failed"
                payment.save()
                return Response({
                    "message": "Payment not successful",
                    "status": payment_status
                }, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "error": "Verification failed",
                "details": res_data
            }, status=status.HTTP_400_BAD_REQUEST)

        except requests.RequestException as e:
            return Response({
                "error": "Payment verification service unavailable",
                "details": str(e)
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

@csrf_exempt
def flutterwave_webhook(request):
    """
    Webhook endpoint for Flutterwave payment notifications
    Set this URL in your Flutterwave dashboard
    """
    # Get secret hash from environment variable
    secret_hash = os.getenv("FLUTTERWAVE_WEBHOOK_SECRET")
    
    # Get the signature from the request headers
    signature = request.headers.get("verif-hash") or request.headers.get("Verif-Hash")
    
    # Reject request if the signature does not match
    if not signature or signature != secret_hash:
        return JsonResponse({"error": "Unauthorized request"}, status=401)
    
    # Load webhook data
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    # Log the webhook data
    print("Received Flutterwave Webhook:", data)
    
    # Process based on event type
    event = data.get("event")
    
    if event == "charge.completed":
        # Get the transaction reference
        tx_ref = data.get("data", {}).get("tx_ref")
        status = data.get("data", {}).get("status")
        flw_ref = data.get("data", {}).get("id")
        
        if tx_ref and status:
            try:
                # Find the payment by transaction ID
                payment = Payment.objects.get(transaction_id=tx_ref)
                trip_id = payment.trip_id
                try:
                    trip = Trip.objects.get(id=trip_id)
                except Trip.DoesNotExist:    
                    return JsonResponse({"error": "Trip not found"}, status=404)
                
                # Update payment status based on transaction status
                if status == "successful":
                    payment.status = "success"
                    trip.is_paid = True
                    trip.save()
                    payment.payment_reference = str(flw_ref)
                    payment.save()
                elif status in ["failed", "cancelled"]:
                    payment.status = "failed"
                    payment.save()
                
                return Response({"status": "success", "message": "Webhook processed"}, status=200)
            except Payment.DoesNotExist:
                return JsonResponse({"error": "Payment not found"}, status=404)
    
    # Default response for other event types
    return JsonResponse({"status": "success", "message": "Webhook received"}, status=200)


@csrf_exempt
def paystack_webhook(request):
    """
    Webhook endpoint for Paystack payment notifications
    Set this URL in your Paystack dashboard.
    """
    # Get secret key from environment variable
    PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")

    # Validate the webhook signature
    signature = request.headers.get("x-paystack-signature")
    if not signature:
        return JsonResponse({"error": "Unauthorized request"}, status=401)

    try:
        payload = request.body
        computed_hmac = hmac.new(
            PAYSTACK_SECRET_KEY.encode("utf-8"),
            msg=payload,
            digestmod=hashlib.sha512
        ).hexdigest()

        if signature != computed_hmac:
            return JsonResponse({"error": "Invalid signature"}, status=401)
    except Exception as e:
        return JsonResponse({"error": "Webhook validation error", "details": str(e)}, status=400)

    # Load webhook data
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # Log the webhook data

    event = data.get("event")
    if event == "charge.success":
        # Extract transaction details
        tx_ref = data.get("data", {}).get("reference")
        status = data.get("data", {}).get("status")
        paystack_ref = data.get("data", {}).get("id")  # Paystack transaction ID

        if tx_ref and status:
            payment = get_object_or_404(Payment, transaction_id=tx_ref)
            trip = get_object_or_404(Trip, id=payment.trip_id)

            # Update payment status
            if status == "success":
                payment.status = "success"
                trip.is_paid = True
                trip.save()
                payment.payment_reference = str(paystack_ref)
                payment.save()
            elif status in ["failed", "abandoned"]:
                payment.status = "failed"
                payment.save()

            return JsonResponse({"status": "success", "message": "Webhook processed"}, status=200)

    # Default response for other event types
    return JsonResponse({"status": "success", "message": "Webhook received"}, status=200)