import asyncio
import websockets
import json
import sys, os
from channels.db import database_sync_to_async
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toota.settings')

# Import Django and set up the environment
import django
django.setup()
from authentication.models import User

# Driver details
DRIVER_ID = "1aee28fd-0ce7-498d-8150-7cc0f5ef32b3"   # Change this to the assigned driver ID
WS_URL = f"ws://localhost:8000/ws/trips/driver/response/{DRIVER_ID}/"  # WebSocket URL

async def driver_simulation():
    async with websockets.connect(WS_URL) as websocket:
        print("✅ Connected to WebSocket as Driver")

        while True:
            print("\n🚦 Waiting for a trip request...")
            
            # Receive a trip request from a passenger
            request = await websocket.recv()
            data = json.loads(request)

            if data.get("status") == "cancelled":
                print(f"❌ Trip was cancelled by passenger {data['user_id']}")
                continue

            if "trip_info" in data:
                user = await get_user(data["user_id"])
                print(f"{user.first_name} {user.last_name} is requesting for a trip")
                print("\n🚖 New Trip Request Received!")
                print(f"📍 Pickup: {data['trip_info']['pickup']}")
                print(f"🎯 Destination: {data['trip_info']['destination']}")
                print(f"🧳 Load Description: {data['trip_info']['load_description']}")

                action = input("\nEnter 'accept' to accept trip, 'reject' to reject: ").strip().lower()

                if action == "accept":
                    response_data = {
                        "user_id": data["user_id"],
                        "trip_response_status": "accepted",
                        "trip_info": data["trip_info"]
                    }
                    await websocket.send(json.dumps(response_data))
                    print("✅ Trip accepted! Notifying passenger...")

                elif action == "reject":
                    response_data = {
                        "user_id": data["user_id"],
                        "trip_response_status": "rejected"
                    }
                    await websocket.send(json.dumps(response_data))
                    print("❌ Trip rejected! Notifying passenger...")

                else:
                    print("⚠️ Invalid input. Please enter 'accept' or 'reject'.")

@database_sync_to_async
def get_user(user_id):
    return User.objects.get(id=user_id)

# Run the driver simulation
asyncio.run(driver_simulation())
