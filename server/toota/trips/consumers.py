import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from authentication.models import Driver, User
from .models import Trip
from channels.db import database_sync_to_async
import logging

logger = logging.getLogger(__name__)

class DriverLocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """ Accepts WebSocket connection if the user is an authenticated driver """
        
        self.driver_id = self.scope["url_route"]["kwargs"]["driver_id"]

        # Ensure the user is authenticated and is the correct driver
        if self.scope["user"].is_authenticated and await self.is_driver(self.driver_id):
            self.room_group_name = f"driver_{self.driver_id}"
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()  # Reject unauthorized connections

    async def disconnect(self, close_code):
        """ Removes driver from group when disconnected """
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """ Handles incoming location updates from the driver """
        try:
            data = json.loads(text_data)
            latitude = data.get("latitude")
            longitude = data.get("longitude")

            # Save to database
            driver = await self.get_driver(self.driver_id)
            if driver:
                driver.latitude = latitude
                driver.longitude = longitude
                await self.save_driver(driver)

                # Broadcast location update to passengers
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "driver_location_update",
                        "latitude": latitude,
                        "longitude": longitude,
                        "driver_id": self.driver_id
                    }
                )
        except Exception as e:
            logger.error(f"Error processing location update: {e}", exc_info=True)

    async def driver_location_update(self, event):
        """ Sends updated location to all connected passengers """
        await self.send(text_data=json.dumps({
            "latitude": event["latitude"],
            "longitude": event["longitude"],
            "driver_id": event["driver_id"]
        }))

    @database_sync_to_async
    def is_driver(self, driver_id):
        """ Checks if the user is the correct driver """
        return Driver.objects.filter(id=driver_id).exists()

    @database_sync_to_async
    def get_driver(self, driver_id):
        """ Fetch driver synchronously """
        from authentication.models import Driver
        try:
            return Driver.objects.get(id=driver_id)
        except Driver.DoesNotExist:
            return None

    @database_sync_to_async
    def save_driver(self, driver):
        """ Save driver location synchronously """
        driver.save()

class PassengerGetLocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """ Connects passenger to the WebSocket group for the selected driver. """
        self.driver_id = self.scope["url_route"]["kwargs"]["driver_id"]

        # Ensure the user is authenticated and is a passenger
        if self.scope["user"].is_authenticated and await self.is_passenger(self.scope["user"]):
            self.room_group_name = f"driver_{self.driver_id}"
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()  # Reject unauthorized users

    async def disconnect(self, close_code):
        """ Removes passenger from the WebSocket group when they disconnect. """
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def driver_location_update(self, event):
        """ Receives driver location updates and forwards them to the passenger. """
        await self.send(text_data=json.dumps({
            "latitude": event["latitude"],
            "longitude": event["longitude"],
            "driver_id": event["driver_id"]
        }))

    @database_sync_to_async
    def is_passenger(self, user):
        """Checks if the user is a registered User."""
        from authentication.models import User
        return User.objects.filter(user=user).exists()


class TripRequestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Connect user to WebSocket."""
        self.driver_id = self.scope['url_route']['kwargs']['driver_id']
        self.room_group_name = f"trip_{self.driver_id}"
        self.user_id = self.scope["user"].id # make sure user is authenticated
        self.user_group_name = f"user_{self.user_id}"
        if self.scope["user"].is_authenticated and await self.is_user(self.user_id):
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.channel_layer.group_add(self.user_group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        """Disconnect user from WebSocket."""
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.channel_layer.group_discard(self.user_group_name, self.channel_name)

    async def receive(self, text_data):
        """Receive trip request from passenger and send it to driver."""
        data = json.loads(text_data)
        user_id = data["user_id"]
        trip_request_status = data.get("trip_request_status")  # Might not always be present

        if trip_request_status == "cancelled":
            # Notify the driver that the trip has been canceled
            await self.channel_layer.group_send(
                f"driver_{self.driver_id}",
                {
                    "type": "trip_cancelled",
                    "user_id": user_id,
                    "status": "cancelled"
                }
            )
        else:
            # the trip_info should contain the pickup and dropoff locations and the
            # latitude and longitude of the locations
            trip_info = data["trip_info"]
            # Send trip request to the specific driver
            await self.channel_layer.group_send(
                f"driver_{self.driver_id}",
                {
                    "type": "send_trip_request",
                    "trip_info": trip_info,
                    "user_id": user_id
                }
            )

    async def send_trip_request(self, event):
        """Send trip request to the driver."""
        await self.send(text_data=json.dumps({
            "user_id": event["user_id"],
            "trip_info": event["trip_info"]
        }))
    
    async def trip_cancelled(self, event):
        """Notify driver that the trip has been cancelled."""
        await self.send(text_data=json.dumps({
            "user_id": event["user_id"],
            "status": "cancelled"
        }))

    async def trip_rejected(self, event):
        """Notify user that the driver has rejected the trip."""
        await self.send(text_data=json.dumps({
            "status": "rejected"
        }))

    @database_sync_to_async
    def is_user(self, user_id):
        """ Checks if the user is the correct driver """
        return User.objects.filter(id=user_id).exists()
    

class DriverTripConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Connect driver to WebSocket."""
        self.driver_id = self.scope['url_route']['kwargs']['driver_id']
        self.room_group_name = f"driver_{self.driver_id}"

        if self.scope["user"].is_authenticated and await self.is_driver(self.driver_id): 
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()
    async def disconnect(self, close_code):
        """Disconnect driver from WebSocket."""
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Receive driver's acceptance/rejection response."""
        data = json.loads(text_data)
        user_id = data["user_id"]
        trip_response_status = data["trip_response_status"]

        if trip_response_status == "rejected":
            # Notify the user that the driver has rejected the trip
            await self.channel_layer.group_send(
                f"user_{user_id}",
                {
                    "type": "trip_rejected",
                    "status": "rejected"
                }
            )
        else:
            trip_info = data["trip_info"]
            user = await self.get_user(user_id)
            driver = await self.get_driver(self.driver_id)
            new_trip = await self.create_trip(user, driver, trip_info)

            # Notify the user about the trip status update
            await self.channel_layer.group_send(
                f"user_{user.id}",
                {
                    "type": "trip_status_update",
                    "trip_id": new_trip.id,
                    "status": "ongoing"
                }
            )

    async def trip_rejected(self, event):
        """Notify user that the driver has rejected the trip."""
        await self.send(text_data=json.dumps({
            "status": "rejected"
        }))

    async def trip_status_update(self, event):
        """Send trip status update to user."""
        await self.send(text_data=json.dumps({
            "trip_id": event["trip_id"],
            "status": event["status"]
        }))

    async def trip_cancelled(self, event):
        """Notify driver that the trip has been cancelled."""
        await self.send(text_data=json.dumps({
            "user_id": event.get("user_id"),
            "status": "cancelled"
        }))


    async def send_trip_request(self, event):
        """Send trip request to the driver."""
        await self.send(text_data=json.dumps({
            "user_id": event["user_id"],
            "trip_info": event["trip_info"]
        }))        

    @database_sync_to_async
    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    @database_sync_to_async
    def get_driver(self, driver_id):
        return Driver.objects.get(id=driver_id)

    @database_sync_to_async
    def create_trip(self, user, driver, trip_info):
        return Trip.objects.create(user=user, driver=driver, **trip_info)
    
    @database_sync_to_async
    def is_driver(self, driver_id):
        """ Checks if the user is the correct driver """
        return Driver.objects.filter(id=driver_id).exists()