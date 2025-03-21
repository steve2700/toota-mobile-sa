import websocket
import json
import random
import time
from datetime import datetime

# Tokens and WebSocket URLs
DRIVER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQyMTIyNjI5LCJpYXQiOjE3NDIxMTkwMjksImp0aSI6IjRlMzI2M2YyMDkwNDRhMzc4NGU5NjczNjIyMjMzYzUzIiwidXNlcl9pZCI6ImFhZjA3ODAzLTI5MzUtNDllOC04NWZiLTJhY2E5Y2QwNWZmNSJ9.gwH1zpHlwh_5aijWDV1pRDq1fnCNWq0L5vNZeZKn4_c"
DRIVER_WS_URL = "ws://localhost:8000/ws/trips/driver/location/"

def driver_simulation():
    headers = ["Authorization: Bearer " + DRIVER_TOKEN]
    
    while True:
        try:
            print(f"[{datetime.now()}] Connecting driver to {DRIVER_WS_URL}")
            ws = websocket.create_connection(DRIVER_WS_URL, header=headers)
            print(f"[{datetime.now()}] Driver connected")

            # Initial location
            latitude = 7.769137135650247
            longitude = 4.57368459596944

            # Send 10 location updates with small random movements
            for update in range(1, 11):
                latitude += random.uniform(-0.001, 0.001)
                longitude += random.uniform(-0.001, 0.001)
                location = {"latitude": latitude, "longitude": longitude}
                message = json.dumps(location)
                ws.send(message)
                print(f"[{datetime.now()}] Driver sent update {update}: {location}")
                time.sleep(2)

            ws.close()
            print(f"[{datetime.now()}] Driver connection closed")
            # Exit loop if simulation completes successfully
            break

        except Exception as e:
            print(f"[{datetime.now()}] Driver connection error: {e}")
            try:
                ws.close()
            except Exception:
                pass
            print(f"[{datetime.now()}] Retrying connection in 3 seconds...")
            time.sleep(3)

if __name__ == "__main__":
    driver_simulation()
