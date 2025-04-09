import asyncio
import json
import websockets
from websockets.exceptions import ConnectionClosedError

# Test configuration
WEBSOCKET_URL = "ws://127.0.0.1:8000/ws/trips/drivers/all/"
BEARER_TOKEN = "your_bearer_token_here"  # Replace with a valid token
RETRY_LIMIT = 5
RETRY_DELAY = 2  # seconds

async def test_user_get_available_drivers():
    headers = [("Authorization", f"Bearer {BEARER_TOKEN}")]
    retries = 0

    while retries < RETRY_LIMIT:
        try:
            # Connect to the WebSocket
            async with websockets.connect(WEBSOCKET_URL, extra_headers=headers) as websocket:
                print("Connected to WebSocket.")

                # Send a valid payload to request available drivers
                request_payload = {
                    "user_latitude": 6.5244,
                    "user_longitude": 3.3792,
                }
                await websocket.send(json.dumps(request_payload))
                print(f"Sent payload: {request_payload}")

                while True:
                    try:
                        # Receive messages from the WebSocket
                        response = await websocket.recv()
                        response_data = json.loads(response)

                        # Handle ping messages
                        if response_data.get("type") == "ping":
                            print("Received ping from server.")
                            continue

                        # Validate the expected payload
                        if response_data.get("type") == "nearest_drivers":
                            print("Received nearest drivers response:")
                            print(json.dumps(response_data, indent=4))

                            # Perform assertions or validations
                            assert "nearest_drivers" in response_data
                            assert isinstance(response_data["nearest_drivers"], list)
                            for driver_info in response_data["nearest_drivers"]:
                                assert isinstance(driver_info, list)
                                assert "id" in driver_info[0]
                                assert "distance" in driver_info[1]
                                assert "duration" in driver_info[1]

                            # Exit the loop after successful validation
                            return

                        # Handle unexpected messages
                        print(f"Unexpected message: {response_data}")

                    except json.JSONDecodeError:
                        print("Received invalid JSON from server.")
                    except ConnectionClosedError:
                        print("Connection closed by server.")
                        break

        except (ConnectionRefusedError, ConnectionClosedError) as e:
            retries += 1
            print(f"Connection failed ({retries}/{RETRY_LIMIT}). Retrying in {RETRY_DELAY} seconds...")
            await asyncio.sleep(RETRY_DELAY)

    print("Failed to connect to WebSocket after multiple retries.")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_user_get_available_drivers())