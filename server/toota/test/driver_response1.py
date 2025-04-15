import websocket
import time
import json
import sys
import threading

# --- Configuration ---
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ0NzM1MDAzLCJpYXQiOjE3NDQ3MzE0MDMsImp0aSI6IjUwYmRjNDA1YjAxMzQ3ZjU5Y2RjM2ZlNjM2MmVmYWY4IiwidXNlcl9pZCI6ImRmNjVkOWQ1LTMwYzctNGNhMC1iN2FhLTk4OGQzZmUyMjZhNSJ9.8Qt-E0OWWm9ZdmvtqTmrje66-jS6UQPsKCmAl83d1is"
WS_URL = f"ws://localhost:8000/ws/trips/driver/"
RECONNECT_DELAY = 5  # seconds before retrying to connect
MAX_RETRIES = 10

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
            decision = "accept"
            break
        elif choice == "2":
            decision = "reject"
            break
        elif choice == "3":
            print_json(notif_data, "Trip Request Details:")
        else:
            print("[ERROR] Invalid choice. Please enter a number between 1-3.")

    message = {
        "trip_id": trip_id,
        "driver_response": decision
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
    retry_count = 0

    while retry_count < MAX_RETRIES:
        print(f"\n=== DRIVER TRIP RESPONSE SIMULATION === (Attempt {retry_count + 1}/{MAX_RETRIES})")
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
            ws_app.run_forever(ping_interval=20, ping_timeout=10)
        except KeyboardInterrupt:
            print("\n[INFO] KeyboardInterrupt detected. Exiting simulator.")
            ws_app.close()
        except Exception as e:
            print(f"[ERROR] WebSocketApp encountered an exception: {e}")
            ws_app.close()

        retry_count += 1
        print(f"[INFO] Reconnecting in {RECONNECT_DELAY} seconds... (retry {retry_count}/{MAX_RETRIES})\n")
        time.sleep(RECONNECT_DELAY)

    print("[ERROR] Max retries exceeded. Exiting.")

if __name__ == "__main__":
    simulate_driver_response()
