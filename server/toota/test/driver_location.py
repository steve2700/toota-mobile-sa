import websocket
import json
import time
import random

DRIVER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ0NzI5NTQyLCJpYXQiOjE3NDQ3MjU5NDIsImp0aSI6IjYyOGI4MjkwN2Q1ZDRlODBiOTU1YWNmZGIxMzQ2ZjhjIiwidXNlcl9pZCI6IjZlOTE5YmNiLTc0ZjUtNDFlZi05OTRkLWEzZDY2NDQ5YjFhOSJ9.TUHZGZQk3bXJqV-SMVmrQCMR9raIPCTB5JwAll1hPu8"
DRIVER_WS_URL = "ws://localhost:8000/ws/trips/driver/location/"

latitude = 7.769137135650247
longitude = 4.57368459596944
update_count = 0

def on_open(ws):
    global latitude, longitude, update_count
    print(f"Driver WebSocket opened")

    def run(*args):
        global latitude, longitude, update_count
        for update in range(1, 11):
            latitude += random.uniform(-0.001, 0.001)
            longitude += random.uniform(-0.001, 0.001)
            location = {"latitude": latitude, "longitude": longitude}
            ws.send(json.dumps(location))
            print(f"Driver sent update {update}: {location}")
            update_count += 1
            time.sleep(2)

        ws.close()
        print(f"Driver simulation complete")

    # Start the sending loop in a separate thread
    import threading
    threading.Thread(target=run).start()

def on_message(ws, message):
    print(f"Message from server: {message}")

def on_error(ws, error):
    print(f"WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    print(f"Driver WebSocket closed. Status: {close_status_code}, Message: {close_msg}")

def driver_simulation():
    headers = {"Authorization": "Bearer " + DRIVER_TOKEN}
    ws_app = websocket.WebSocketApp(
        DRIVER_WS_URL,
        header=headers,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    while update_count < 10:
        try:
            print(f"Connecting driver...")
            ws_app.run_forever()
        except KeyboardInterrupt:
            print("\n[INFO] KeyboardInterrupt detected. Exiting simulator.")
            ws_app.close()
        except Exception as e:
            print(f"[ERROR] WebSocketApp encountered an exception: {e}")
            ws_app.close()
        time.sleep(3)
if __name__ == "__main__":
    driver_simulation()
