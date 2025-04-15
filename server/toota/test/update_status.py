import json
import websocket
import time

WS_URL = "ws://localhost:8000/ws/trips/status/1177dc3a-9159-450e-916e-c599006e27ca/"
USER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ0NzM4MDI1LCJpYXQiOjE3NDQ3MzQ0MjUsImp0aSI6IjIxN2U2MmVlZTFkZjQ2ODk4MGMxZTkzYjE1OGRiNTIzIiwidXNlcl9pZCI6IjgzYjVmMzQ0LTQwYTktNDYyMy1iNDg3LWNlM2ZhNDMwNzFiZSJ9.55fCypyKH_j38F_qOSPp7USqcVv_SXIxxLIzo2ftgUU"  # Replace with a real DRIVER token

# === WebSocket Event Handlers ===

def on_open(ws):
    print("[INFO] WebSocket connection opened. Awaiting trip status update...")


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

def connect_with_retries(max_retries=10, base_delay=2):
    headers = [f"Authorization: Bearer {USER_TOKEN}"]

    for attempt in range(max_retries):
        print(f"\n[INFO] Attempting connection ({attempt + 1}/{max_retries})...")
        ws_app = websocket.WebSocketApp(
            WS_URL,
            header=headers,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )

        try:
            ws_app.run_forever(ping_interval=10, ping_timeout=5)
        except KeyboardInterrupt:
            print("\n[INFO] Interrupted. Closing connection.")
            ws_app.close()
            break
        except Exception as e:
            print(f"[ERROR] Exception: {e}")
            ws_app.close()

        print(f"[INFO] Waiting {base_delay} seconds before retrying...")
        time.sleep(base_delay)

    print("[ERROR] Max retries reached. Exiting.")


if __name__ == "__main__":
    connect_with_retries()
