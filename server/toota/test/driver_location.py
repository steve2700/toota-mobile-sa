import asyncio
import json
import websockets

# Define the WebSocket server URL (replace with your actual server URL)
DRIVER_WS_URL = "ws://localhost:8000/ws/trips/driver/location/1aee28fd-0ce7-498d-8150-7cc0f5ef32b3/"
PASSENGER_WS_URL = "ws://localhost:8000/ws/trips/user/location/1aee28fd-0ce7-498d-8150-7cc0f5ef32b3/"

async def driver_simulation():
    """Simulates a driver sending real-time location updates."""
    async with websockets.connect(DRIVER_WS_URL) as ws:
        print("Driver connected!")
        
        # Simulate sending location updates every 2 seconds
        locations = [
            {"latitude": 12.30, "longitude": 56.75},
            {"latitude": 12.31, "longitude": 56.76},
            {"latitude": 12.32, "longitude": 56.77},
        ]

        for location in locations:
            await ws.send(json.dumps(location))
            print(f"Driver sent location: {location}")
            await asyncio.sleep(2)  # Wait before sending the next update

async def passenger_simulation():
    """Simulates a passenger receiving real-time driver location updates."""
    async with websockets.connect(PASSENGER_WS_URL) as ws:
        print("Passenger connected!")

        while True:
            try:
                response = await ws.recv()  # Receive data from the WebSocket
                data = json.loads(response)
                print(f"Passenger received location: {data}")
            except websockets.exceptions.ConnectionClosed:
                print("Passenger WebSocket closed.")
                break

async def main():
    """Run driver and passenger simulations concurrently."""
    await asyncio.gather(driver_simulation(), passenger_simulation())

# Run the test
asyncio.run(main())
# websockets.close()
