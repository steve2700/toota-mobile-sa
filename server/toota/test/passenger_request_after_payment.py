import json
import websocket
import time
import sys

WS_URL = "ws://localhost:8000/ws/trips/user/"
USER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ0NzM4MDI1LCJpYXQiOjE3NDQ3MzQ0MjUsImp0aSI6IjIxN2U2MmVlZTFkZjQ2ODk4MGMxZTkzYjE1OGRiNTIzIiwidXNlcl9pZCI6IjgzYjVmMzQ0LTQwYTktNDYyMy1iNDg3LWNlM2ZhNDMwNzFiZSJ9.55fCypyKH_j38F_qOSPp7USqcVv_SXIxxLIzo2ftgUU"
TRIP_ID = "1177dc3a-9159-450e-916e-c599006e27ca"
DRIVER_ID = "6e919bcb-74f5-41ef-994d-a3d66449b1a9"

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
        if data.get("type") == "select_new_driver":
            available_drivers = data.get("available_drivers", [])
            if available_drivers:
                driver_id = available_drivers[0].get("id")
                if driver_id:
                    confirmation = {
                        "action": "confirm_driver",
                        "trip_id": TRIP_ID,
                        "driver_id": driver_id
                    }
                    print(f"[INFO] Sending confirmation to new driver ID: {driver_id}")
                    ws.send(json.dumps(confirmation))
                else:
                    print("[WARN] No valid driver ID found in available_drivers[0]")
            else:
                print("[WARN] No available drivers found in message.")
    except json.JSONDecodeError:
        print(f"[RAW MESSAGE]: {message}")


def on_error(ws, error):
    print(f"[ERROR] {error}")


def on_close(ws, close_status_code, close_msg):
    print(f"[INFO] Connection closed. Code: {close_status_code}, Message: {close_msg}")


# === WebSocket Connection with Retry Logic ===

def connect_with_retries(max_retries=10, base_delay=2):
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
            ws_app.close()
        except Exception as e:
            print(f"[ERROR] Exception occurred: {e}")
            ws_app.close()

        retry_count += 1

        if retry_count >= max_retries:
            print(f"[ERROR] Maximum retries ({max_retries}) reached. Giving up.")
            break


        print(f"[INFO] Reconnecting in {base_delay} seconds...")
        time.sleep(base_delay)


if __name__ == "__main__":
    connect_with_retries(max_retries=10)
