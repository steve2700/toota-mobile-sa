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
            required=['trip_id', 'payment_method', 'currency'],
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
                    description="Currency for the payment (e.g., NGN, ZAR)"
                ),
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
                    "logo": ""
                }
            }

            FLUTTERWAVE_BASE_URL = os.getenv("FLUTTERWAVE_BASE_URL")
            FLUTTERWAVE_SECRET_KEY = os.getenv("FLUTTERWAVE_SECRET_KEY")

            url = f"{FLUTTERWAVE_BASE_URL}/payments"
            headers = {
                "Authorization": f"Bearer {FLUTTERWAVE_SECRET_KEY}",
                "Content-Type": "application/json"
            }

            try:
                response = requests.post(url, json=payment_data, headers=headers)
                res_data = response.json()

                if response.status_code == 200 and res_data.get("status") == "success":
                    return Response({
                        "message": "Payment initialized successfully",
                        "payment_link": res_data["data"]["link"],
                        "transaction_id": transaction_id
                    }, status=status.HTTP_200_OK)

                payment.status = "failed"
                payment.save()
                return Response({
                    "error": "Failed to initialize payment",
                    "details": res_data
                }, status=status.HTTP_400_BAD_REQUEST)

            except requests.RequestException as e:
                payment.status = "failed"
                payment.save()
                return Response({
                    "error": "Payment service unavailable",
                    "details": str(e)
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
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
        Handle Flutterwave redirect verification
        """
        tx_ref = request.GET.get('tx_ref')
        transaction_id = request.GET.get('transaction_id')
        status_param = request.GET.get('status')

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

        # If user cancelled
        if status_param == 'cancelled':
            payment.status = 'failed'
            payment.save()
            return Response({
                "status": "failed",
                "message": "Payment not successful",
            }, status=400)

        # Verify payment with Flutterwave
        FLUTTERWAVE_BASE_URL = os.getenv("FLUTTERWAVE_BASE_URL")
        FLUTTERWAVE_SECRET_KEY = os.getenv("FLUTTERWAVE_SECRET_KEY")

        verify_url = f"{FLUTTERWAVE_BASE_URL}/transactions/{transaction_id}/verify"
        headers = {
            "Authorization": f"Bearer {FLUTTERWAVE_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(verify_url, headers=headers)
            res_data = response.json()


            if response.status_code == 200 and res_data.get("status") == "success":
                if res_data["data"]["status"] == "successful":
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

                else:
                    payment.status = "failed"
                    payment.save()
                    return Response({
                        "status": "failed",
                        "message": "Payment not successful",
                    }, status=400)

            payment.status = "failed"
            payment.save()
            return Response({
                "status": "failed",
                "message": "Payment not successful",
            }, status=400)

        except requests.RequestException as e:
            payment.status = "failed"
            payment.save()
            return Response({
                "status": "failed",
                "message": "Payment not successful",
            }, status=400)


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

        # Verify with Flutterwave
        FLUTTERWAVE_BASE_URL = os.getenv("FLUTTERWAVE_BASE_URL")
        FLUTTERWAVE_SECRET_KEY = os.getenv("FLUTTERWAVE_SECRET_KEY")

        verify_url = f"{FLUTTERWAVE_BASE_URL}/transactions/verify_by_reference?tx_ref={transaction_id}"
        headers = {
            "Authorization": f"Bearer {FLUTTERWAVE_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(verify_url, headers=headers)
            res_data = response.json()

            if response.status_code == 200 and res_data.get("status") == "success":
                if res_data["data"]["status"] == "successful":
                    payment.status = "success"
                    payment.payment_reference = str(res_data["data"].get("id", ""))
                    trip.is_paid = True
                    trip.save()
                    payment.save()
                    return Response({
                        "status": "failed",
                        "message": "Payment not successful",
                    }, status=400)

                payment.status = "failed"
                payment.save()
                return Response({
                    "message": "Payment not successful",
                    "status": res_data["data"]["status"]
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
        print(f"this is flw_ref: {flw_ref}")
        
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

