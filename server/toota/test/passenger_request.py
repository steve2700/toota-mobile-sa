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
    ws = websocket.WebSocket()
    ws.connect(url, header=headers)

    try:
        print("[INFO] Sending payload...")
        ws.send(json.dumps(payload))

        while True:
            response = ws.recv()
            if response:
                response_data = json.loads(response)

                # Ignore ping messages
                if response_data.get("type") == "ping":
                    print("[INFO] Received ping, keeping connection open...")
                    continue  

                # Actual response received
                print("[INFO] Received response:")
                print(json.dumps(response_data, indent=2))
                break

    except websocket.WebSocketException as e:
        print(f"[ERROR] WebSocket error: {e}")

    finally:
        ws.close()
        print("[INFO] Connection closed.")
if __name__ == "__main__":
    # Example URL and headers
    WS_URL = "ws://localhost:8000/ws/trips/user/request/"
    headers = [f"Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQzMTA5MjAyLCJpYXQiOjE3NDMxMDU2MDIsImp0aSI6IjdjOGM3OGIwNDJkZTQxMjNiZTU3YzIxMWFkYmIwYjMyIiwidXNlcl9pZCI6IjUwMWEwZjE5LTM2ZGEtNGY4OC05MjVjLWE3YjBkY2RiMDU3OSJ9.t7_t_3TE2J8ppxv05fH1TGXrVXP8-G_7JZN4NRM8QOw"]
    
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
