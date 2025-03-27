import websocket
import time
import json
import sys
import threading

# --- Configuration ---
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQzMTE0MTMzLCJpYXQiOjE3NDMxMTA1MzMsImp0aSI6ImFkYmY2MGM2OGJiMjQwYjBhYzUyNTQzODE2OTIwOTRlIiwidXNlcl9pZCI6ImFhZjA3ODAzLTI5MzUtNDllOC04NWZiLTJhY2E5Y2QwNWZmNSJ9.nnTGsHctJKrmzA08cNJXtZsXYAL13JBjcmpQ9mro_9E"
WS_URL = f"ws://localhost:8000/ws/trips/driver/response/"
RECONNECT_DELAY = 5  # seconds before retrying to connect

# === Utility Functions ===
def print_json(data, title=None):
    if title:
        print(f"{title}")
    print(json.dumps(data, indent=2))

# === WebSocket Event Handlers ===
def on_open(ws):
    print("[INFO] Connection opened.")

def on_message(ws, message):
    try:
        notif_data = json.loads(message)
        print_json(notif_data, "\n[INFO] Received notification:")

        if notif_data.get("type") == "new_trip_request":
            handle_trip_request(ws, notif_data)
        else:
            print(f"[WARN] Unexpected message type: {notif_data.get('type')}")

    except json.JSONDecodeError:
        print(f"[ERROR] Failed to decode server message: {message}")

def on_error(ws, error):
    print(f"[ERROR] WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    print(f"[INFO] Connection closed: {close_status_code} - {close_msg}")

# === Handle Trip Request Logic ===
def handle_trip_request(ws, notif_data):
    trip_details = notif_data.get("trip_details", {})
    trip_id = trip_details.get("trip_id")

    # === Present trip details ===
    user_info = trip_details.get("user_info", {})
    print("\n=== USER DETAILS ===")
    print(f"Name: {user_info.get('name', 'N/A')}")
    print(f"Phone: {user_info.get('phone', 'N/A')}")

    print("\n=== TRIP REQUEST SUMMARY ===")
    print(f"Trip ID: {trip_id}")
    print(f"Pickup: {trip_details.get('pickup', 'Unknown')}")
    print(f"Destination: {trip_details.get('destination', 'Unknown')}")
    print(f"Fare: {trip_details.get('payment_info', {}).get('amount', 'N/A')} NGN")
    print(f"Distance: {trip_details.get('distance_km', 'N/A')} km")
    print(f"Est. Time: {trip_details.get('estimated_time', 'N/A')}")
    print(f"Vehicle Type: {trip_details.get('vehicle_type', 'N/A')}")
    print(f"Load Description: {trip_details.get('load_description', 'None')}")

    print("\n=== DRIVER RESPONSE OPTIONS ===")
    print("1. Accept Trip")
    print("2. Reject Trip")
    print("3. View Trip Details Again")

    while True:
        choice = input("\nEnter your choice (1-3): ").strip()

        if choice == "1":
            decision = "accepted"
            break
        elif choice == "2":
            decision = "rejected"
            break
        elif choice == "3":
            print_json(notif_data, "Trip Request Details:")
        else:
            print("[ERROR] Invalid choice. Please enter a number between 1-3.")

    message = {
        "trip_id": trip_id,
        "driver_response_status": decision
    }

    print("\n[INFO] Sending driver response message:")
    print_json(message, "Driver Response Payload:")

    try:
        ws.send(json.dumps(message))
        print("[INFO] Driver response sent.")
    except Exception as e:
        print(f"[ERROR] Failed to send response: {e}")

# === Main Simulation Loop with Retry ===
def simulate_driver_response():
    headers = [f"Authorization: Bearer {ACCESS_TOKEN}"]

    while True:
        print("=== DRIVER TRIP RESPONSE SIMULATION ===")
        print(f"[INFO] Connecting to DriverTripConsumer at {WS_URL}")

        ws_app = websocket.WebSocketApp(
            WS_URL,
            header=headers,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )

        try:
            # Run forever with ping/pong automatically handled
            ws_app.run_forever(ping_interval=20, ping_timeout=10)
        except KeyboardInterrupt:
            print("\n[INFO] KeyboardInterrupt detected. Exiting simulator.")
            break
        except Exception as e:
            print(f"[ERROR] WebSocketApp encountered an exception: {e}")

        # Wait before retrying connection
        print(f"[INFO] Reconnecting in {RECONNECT_DELAY} seconds...\n")
        time.sleep(RECONNECT_DELAY)

if __name__ == "__main__":
    simulate_driver_response()
