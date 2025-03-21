import websocket
import time
import json
import sys

def connect_with_retries(url, headers, max_retries=10, delay=3):
    for attempt in range(1, max_retries+1):
        try:
            ws = websocket.create_connection(url, header=headers)
            print(f"[INFO] Connected on attempt {attempt}.")
            return ws
        except Exception as e:
            print(f"[WARN] Attempt {attempt} failed: {e}")
            time.sleep(delay)
    sys.exit("Failed to connect after several retries.")

def keep_connection_alive(ws, interval=10):
    while True:
        try:
            ws.send("ping")
            time.sleep(interval)
        except Exception as e:
            print(f"[WARN] Keep-alive ping failed: {e}")
            break

def test_send_and_receive(url, headers, payload):
    ws = connect_with_retries(url, headers)
    try:
        print("[INFO] Sending payload...")
        ws.send(json.dumps(payload))
        # Wait for response; this may block until the server sends a response.
        response = ws.recv()
        print("[INFO] Received response:")
        print(response)
    except Exception as e:
        print(f"[ERROR] Exception during send/receive: {e}")
    finally:
        ws.close()

if __name__ == "__main__":
    # Example URL and headers
    WS_URL = "ws://localhost:8000/ws/trips/user/request/"
    headers = [f"Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQyNDk1MTgxLCJpYXQiOjE3NDI0OTE1ODEsImp0aSI6Ijg0ZjgzOGYzY2RkYjRiZTU4NTZiYzJhMzBjMzliYzczIiwidXNlcl9pZCI6IjUwMWEwZjE5LTM2ZGEtNGY4OC05MjVjLWE3YjBkY2RiMDU3OSJ9.iWCW9rFf9s513cXsN5xL1-Tl-O2RrREQraKSFlZbUtc"]
    
    # Example payload
    payload = {
        "action": "create_trip",
        "vehicle_type": "Bakkie",
        "pickup": "21, Jinadu Street, Off E.C.N Bus Stop",
        "destination": "23, Ogunnaike Street, Adealu Bus Stop",
        "pickup_lat": 6.614465476614534,
        "pickup_lon": 3.3110880585889353,
        "dest_lat": 6.462208135036844,
        "dest_lon": 3.3362118942921,
        "load_description": "Two bags of rice"
    }
    
    test_send_and_receive(WS_URL, headers, payload)
