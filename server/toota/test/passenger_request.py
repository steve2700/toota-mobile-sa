import asyncio
import websockets
import json

# Passenger and driver details
USER_ID = "3463e40e-be01-4837-a3d3-a1f25b17fd10"  # Change this to a real user ID
DRIVER_ID = "1aee28fd-0ce7-498d-8150-7cc0f5ef32b3"   # Change this to the assigned driver ID
WS_URL = f"ws://localhost:8000/ws/trips/user/request/{DRIVER_ID}/"  # WebSocket URL

async def passenger_simulation():
    async with websockets.connect(WS_URL) as websocket:
        print("✅ Connected to WebSocket as Passenger")

        while True:
            action = input("\nEnter 'request' to request a trip, 'cancel' to cancel a trip, or 'exit' to quit: ").strip().lower()

            if action == "request":
                trip_info = {
                    "pickup": "123 Main Street",
                    "destination": "456 Elm Street",
                    "load_description": "2 large bags, 1 small bag"
                }

                request_data = {
                    "user_id": USER_ID,
                    "trip_info": trip_info
                }

                await websocket.send(json.dumps(request_data))
                # await asyncio.sleep(2000) 
                print("🚖 Trip request sent to driver...")

            elif action == "cancel":
                cancel_data = {
                    "user_id": USER_ID,
                    "trip_request_status": "cancelled"
                }

                await websocket.send(json.dumps(cancel_data))
                print("❌ Trip cancellation request sent...")

            elif action == "exit":
                print("👋 Exiting...")
                break

            else:
                print("❌ Invalid input. Try again.")

            # Wait for a response from the server
            response = await websocket.recv()
            data = json.loads(response)

            if data.get("status") == "reject":
                print("🛑 Trip was rejected.")
                break
            # elif "trip_info" in data:
            #     print("📨 Driver received the trip request!")
            #     print(f"Pickup: {data['trip_info']['pickup']}")
            #     print(f"Destination: {data['trip_info']['destination']}")
            else:
                for i in data:
                    print(f"Driver received the trip request! {data[i]}")
# Run the passenger simulation
asyncio.run(passenger_simulation())
