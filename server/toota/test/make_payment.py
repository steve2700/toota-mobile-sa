import requests
import json

# --- Configuration ---
API_URL = "http://localhost:8000/trips/payment/"
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQxOTQ3NDcyLCJpYXQiOjE3NDE5NDM4NzIsImp0aSI6IjUxOTZlYjkxZDY2MjQxOTNiZGIzOTAxNzM5OTE3YjM4IiwidXNlcl9pZCI6IjUwMWEwZjE5LTM2ZGEtNGY4OC05MjVjLWE3YjBkY2RiMDU3OSJ9.yW5yRrXh6EKxXdQOYbx3SM4yNu6EqwJVuDXR2JntX7A"
TRIP_ID = "52619e2f-c7d1-46a4-9918-95daabb4e897"  # Ensure this exists in your DB

# --- Payload with Flutterwave Test Card Details ---
payload = {
    "trip_id": TRIP_ID,
    "amount": "381.6",
    "currency": "NGN",
    "payment_method": "card",
    "card_details": {
        "card_number": "5531886652142950",
        "expiry_month": "09",
        "expiry_year": "32",
        "cvv": "564",
        "otp": "12345",
        "pin": "3310"
    }
}
USER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQyNDk1MTgxLCJpYXQiOjE3NDI0OTE1ODEsImp0aSI6Ijg0ZjgzOGYzY2RkYjRiZTU4NTZiYzJhMzBjMzliYzczIiwidXNlcl9pZCI6IjUwMWEwZjE5LTM2ZGEtNGY4OC05MjVjLWE3YjBkY2RiMDU3OSJ9.iWCW9rFf9s513cXsN5xL1-Tl-O2RrREQraKSFlZbUtc"

# --- Headers ---
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# --- Print payload for debugging ---
print("Sending payment request with the following payload:")
print(json.dumps(payload, indent=2))

# --- Make the POST request ---
response = requests.post(API_URL, json=payload, headers=headers)

# --- Print response ---
print("\nResponse Status Code:", response.status_code)
try:
    print("Response JSON:", json.dumps(response.json(), indent=2))
except Exception as e:
    print("Failed to decode JSON response:", e)