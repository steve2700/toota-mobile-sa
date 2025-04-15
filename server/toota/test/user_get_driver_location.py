import websocket
import json
import time

PASSENGER_WS_URL = "ws://localhost:8000/ws/trips/user/location/6e919bcb-74f5-41ef-994d-a3d66449b1a9/"
USER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ0NzI5MTQxLCJpYXQiOjE3NDQ3MjU1NDEsImp0aSI6ImJkZDhkZWM1MWNhNzQzOTM4NTkxZWE1NmU1NmYwZDVhIiwidXNlcl9pZCI6IjgzYjVmMzQ0LTQwYTktNDYyMy1iNDg3LWNlM2ZhNDMwNzFiZSJ9.ngC-IFj8IDQCs10dGmAeGNXdffWvfFVa0tIWbaJkoI4"

MAX_RETRIES = 10
retries = 0
USER_LATITUDE = 6.6137086720679354
USER_LONGITUDE = 3.305057535428996

def on_open(ws):
    print(f"Passenger WebSocket opened")
    payload = {
        "user_latitude": USER_LATITUDE,
        "user_longitude": USER_LONGITUDE
    }
    ws.send(json.dumps(payload))
    print(f"Sent user current location: {payload}")

def on_message(ws, message):
    data = json.loads(message)
    print(f"Passenger received: {data}")

def on_error(ws, error):
    global retries
    print(f"WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    global retries
    print(f"WebSocket closed (code={close_status_code}, msg={close_msg})")

def passenger_simulation():
    global retries

    headers = {"Authorization": "Bearer " + USER_TOKEN}
    
    while retries < MAX_RETRIES:
        try:
            print(f"Attempting to connect (Retry {retries + 1}/{MAX_RETRIES})")
            ws_app = websocket.WebSocketApp(
                PASSENGER_WS_URL,
                header=headers,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            ws_app.run_forever()
        except KeyboardInterrupt:
            print("\n[INFO] KeyboardInterrupt detected. Exiting simulator.")
            ws_app.close()
        except Exception as e:
            print("Unexpected exception: {e}")
        finally:
            retries += 1
            print("Reconnecting in 3 seconds...")
            time.sleep(3)

    print("Max retries reached. Exiting.")

if __name__ == "__main__":
    passenger_simulation()
