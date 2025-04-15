import time
import json
import websocket
import threading

# WebSocket URL
uri = "ws://localhost:8000/ws/trips/user/"

# Authorization token and headers
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ0NzM1MTM3LCJpYXQiOjE3NDQ3MzE1MzcsImp0aSI6IjBiNjlkN2YzZDE5ZDQ5MjZhOWUxY2Q2MmUwMjg0MzZlIiwidXNlcl9pZCI6IjgzYjVmMzQ0LTQwYTktNDYyMy1iNDg3LWNlM2ZhNDMwNzFiZSJ9.Soy6VbkX-qlX1rRDInICtQ-AeOUxY42bvQVfv72mBik"
headers = {
    "Authorization": f"Bearer {token}"
}

# Payload to send once connection is open
payload = {
    "action": "create_trip",
    "vehicle_type": "Bakkie",
    "pickup": "21, Jinadu Street, Off E.C.N Bus Stop",
    "destination": "23, Ogunnaike Street, Adealu Bus Stop",
    "pickup_latitude": 6.614465476614534,
    "pickup_longitude": 3.3110880585889353,
    "dest_latitude": 6.462208135036844,
    "dest_longitude": 3.3362118942921,
    "load_description": "Two bags of rice"
}

def on_message(ws, message):
    print("Received from server:", message)

def on_error(ws, error):
    print("WebSocket error:", error)

def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed:", close_status_code, close_msg)

def on_open(ws):
    print("WebSocket opened. Sending payload...")
    ws.send(json.dumps(payload))

def run_websocket():
    ws = websocket.WebSocketApp(uri,
                                 header=headers,
                                 on_message=on_message,
                                 on_error=on_error,
                                 on_close=on_close,
                                 on_open=on_open)
    ws.run_forever()

def create_connection_with_retries(max_retries=5, retry_delay=3):
    retries = 0
    while retries < max_retries:
        print(f"Attempting connection... (Attempt {retries + 1})")
        ws_thread = threading.Thread(target=run_websocket)
        ws_thread.start()

        time.sleep(5)  # Wait to see if connection is alive

        if not ws_thread.is_alive():
            print("Connection failed or dropped. Retrying...")
            retries += 1
            time.sleep(retry_delay)
        else:
            print("WebSocket connected successfully.")
            return ws_thread

    print("Max retries reached. WebSocket connection failed.")

# Run the test
create_connection_with_retries()
