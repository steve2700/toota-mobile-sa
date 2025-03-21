import websocket
import json
import time
from datetime import datetime

PASSENGER_WS_URL = "ws://localhost:8000/ws/trips/user/location/1d7341ba-d2e1-4f12-bda4-da56649d515d/"
USER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQxNTM5NTU3LCJpYXQiOjE3NDE0NTMxNTcsImp0aSI6ImNkM2Q0NmM1MjUzMjQ1MDJhOTQ0ODI0ZmVhOGYxMWMzIiwidXNlcl9pZCI6Ijk1YWY2YzRjLTNhODctNGQ4My1hZTI0LTU1ZWYzOGFjYTcxMiJ9.tTMoxfqp9pNL3cgXDaqKZoTnyLmHpLGRQcgKBhQwEiE"

def passenger_simulation():
    headers = ["Authorization: Bearer " + USER_TOKEN]
    
    while True:
        try:
            print(f"[{datetime.now()}] Connecting passenger to {PASSENGER_WS_URL}")
            ws = websocket.create_connection(PASSENGER_WS_URL, header=headers)
            print(f"[{datetime.now()}] Passenger connected")
            
            while True:
                message = ws.recv()
                data = json.loads(message)
                print(f"[{datetime.now()}] Passenger received: {data}")
                
        except Exception as e:
            print(f"[{datetime.now()}] Passenger connection error: {e}")
        finally:
            try:
                ws.close()
            except Exception:
                pass
            print(f"[{datetime.now()}] Reconnecting in 3 seconds...")
            time.sleep(3)

if __name__ == "__main__":
    passenger_simulation()
