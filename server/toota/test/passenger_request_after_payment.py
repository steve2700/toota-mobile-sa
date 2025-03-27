import json
import websocket
import time
import sys

WS_URL = "ws://localhost:8000/ws/trips/user/request/"
USER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQzMTE0MjEyLCJpYXQiOjE3NDMxMTA2MTIsImp0aSI6ImVmNTlkNDgyMWY1NjQ5NWNiMGExMjY3YjA2NmI4NWZiIiwidXNlcl9pZCI6IjUwMWEwZjE5LTM2ZGEtNGY4OC05MjVjLWE3YjBkY2RiMDU3OSJ9.S1P4DkdXoaPfjov-LVBN1On9OGFO7V9B1grX8VrZmJw"
TRIP_ID = "0ed7f12c-6f9d-4db8-882b-5600b00d2864"
DRIVER_ID = "aaf07803-2935-49e8-85fb-2aca9cd05ff5"

# === WebSocket Event Handlers ===

def on_open(ws):
    print("[INFO] WebSocket connection opened. Sending driver confirmation...")

    confirmation = {
        "action": "confirm_driver",
        "trip_id": TRIP_ID,
        "driver_id": DRIVER_ID
    }

    ws.send(json.dumps(confirmation))


def on_message(ws, message):
    print("[MESSAGE RECEIVED]")
    try:
        data = json.loads(message)
        print(json.dumps(data, indent=2))
    except json.JSONDecodeError:
        print(f"[RAW MESSAGE]: {message}")


def on_error(ws, error):
    print(f"[ERROR] {error}")


def on_close(ws, close_status_code, close_msg):
    print(f"[INFO] Connection closed. Code: {close_status_code}, Message: {close_msg}")


# === WebSocket Connection with Retry Logic ===

def connect_with_retries(max_retries=5, base_delay=2):
    headers = [f"Authorization: Bearer {USER_TOKEN}"]

    retry_count = 0

    while True:
        print(f"\n[INFO] Attempting to connect to WebSocket (Attempt {retry_count + 1}/{max_retries})...")
        ws_app = websocket.WebSocketApp(
            WS_URL,
            header=headers,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )

        try:
            # Blocking call. Runs until closed or error.
            ws_app.run_forever(ping_interval=20, ping_timeout=10)
        except KeyboardInterrupt:
            print("\n[INFO] Keyboard interrupt detected. Exiting.")
            sys.exit(0)
        except Exception as e:
            print(f"[ERROR] Exception occurred: {e}")

        retry_count += 1

        if retry_count >= max_retries:
            print(f"[ERROR] Maximum retries ({max_retries}) reached. Giving up.")
            break

        # Exponential backoff delay
        delay = base_delay * (2 ** (retry_count - 1))
        print(f"[INFO] Reconnecting in {delay} seconds...")
        time.sleep(delay)


if __name__ == "__main__":
    connect_with_retries(max_retries=5)
