import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from authentication.models import User, Driver
from .models import Trip
from .utils import get_route_data

logger = logging.getLogger(__name__)

class DriverLocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Accepts WebSocket connection if the user is an authenticated driver."""
        self.driver_id = self.scope["url_route"]["kwargs"]["driver_id"]
        self.room_group_name = f"driver_{self.driver_id}"
        logger.info(f"Driver connect attempt: {self.driver_id}, User: {self.scope['user']}")
        
        if isinstance(self.scope["user"], Driver) and self.scope["user"].is_authenticated and await self.is_driver(self.driver_id):
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            logger.info("Driver connection accepted")
        else:
            logger.warning("Driver connection rejected")
            await self.close(code=4403)

    async def disconnect(self, close_code):
        """Remove driver from group when disconnected."""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Handle incoming location updates from the driver."""
        try:
            data = json.loads(text_data)
            latitude = data.get("latitude")
            longitude = data.get("longitude")

            driver = await self.get_driver(self.driver_id)
            if driver:
                driver.latitude = latitude
                driver.longitude = longitude
                await self.save_driver(driver)

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "driver_location_update",
                        "latitude": latitude,
                        "longitude": longitude,
                        "driver_id": self.driver_id,
                    },
                )
        except Exception as e:
            logger.error(f"Error processing location update: {e}", exc_info=True)

    async def driver_location_update(self, event):
        """Send updated location to all connected passengers."""
        await self.send(
            text_data=json.dumps(
                {
                    "latitude": event["latitude"],
                    "longitude": event["longitude"],
                    "driver_id": event["driver_id"],
                }
            )
        )

    @database_sync_to_async
    def is_driver(self, driver_id):
        """Check if the authenticated user matches the driver_id."""
        return str(self.scope["user"].id) == driver_id

    @database_sync_to_async
    def get_driver(self, driver_id):
        """Fetch driver synchronously."""
        try:
            return Driver.objects.get(id=driver_id)
        except Driver.DoesNotExist:
            return None

    @database_sync_to_async
    def save_driver(self, driver):
        """Save driver location synchronously."""
        driver.save()

class PassengerGetLocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Connect passenger to the WebSocket group for the selected driver."""
        self.driver_id = self.scope["url_route"]["kwargs"]["driver_id"]
        self.room_group_name = f"driver_{self.driver_id}"
        logger.info(f"Passenger connect attempt: User: {self.scope['user']}")

        if isinstance(self.scope["user"], User) and self.scope["user"].is_authenticated and await self.is_passenger(self.scope["user"]):
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            logger.info("Passenger connection accepted")
        else:
            logger.warning("Passenger connection rejected")
            await self.close(code=4403)

    async def disconnect(self, close_code):
        """Remove passenger from the WebSocket group when they disconnect."""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def driver_location_update(self, event):
        """Receive driver location updates and forward them to the passenger."""
        await self.send(
            text_data=json.dumps(
                {
                    "latitude": event["latitude"],
                    "longitude": event["longitude"],
                    "driver_id": event["driver_id"],
                }
            )
        )

    @database_sync_to_async
    def is_passenger(self, user):
        """Check if the user is a registered User."""
        return User.objects.filter(id=user.id).exists()

class TripRequestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Connect user to WebSocket for trip creation."""
        self.driver_id = self.scope["url_route"]["kwargs"]["driver_id"]
        self.user_id = self.scope["user"].id if hasattr(self.scope["user"], 'id') else None
        self.user_group_name = f"user_{self.user_id}"
        self.driver_group_name = f"driver_{self.driver_id}"
        logger.info(f"User connect attempt: {self.user_id}, User: {self.scope['user']}")

        if isinstance(self.scope["user"], User) and self.scope["user"].is_authenticated and await self.is_user(self.user_id):
            await self.channel_layer.group_add(self.user_group_name, self.channel_name)
            await self.channel_layer.group_add(self.driver_group_name, self.channel_name)
            await self.accept()
            logger.info("User connection accepted")
        else:
            logger.warning("User connection rejected")
            await self.close(code=4403)

    async def disconnect(self, close_code):
        """Disconnect user from WebSocket."""
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(self.user_group_name, self.channel_name)
        if hasattr(self, 'driver_group_name'):
            await self.channel_layer.group_discard(self.driver_group_name, self.channel_name)

    async def receive(self, text_data):
        """Receive trip creation request from passenger and process fare estimation."""
        data = json.loads(text_data)
        action = data.get("action")

        if action == "create_trip":
            vehicle_type = data.get("vehicle_type")
            pickup = data.get("pickup")
            destination = data.get("destination")
            pickup_lat = data.get("pickup_lat")
            pickup_lon = data.get("pickup_lon")
            dest_lat = data.get("dest_lat")
            dest_lon = data.get("dest_lon")
            surge = data.get("surge", False)
            load_description = data.get("load_description", "")

            route_data = await database_sync_to_async(get_route_data)(
                pickup_lat, pickup_lon, dest_lat, dest_lon
            )
            distance_km = route_data["distance_km"]
            estimated_time_minutes = route_data["duration_min"]

            trip = await database_sync_to_async(Trip.objects.create)(
                user=self.scope["user"],
                vehicle_type=vehicle_type,
                pickup=pickup,
                destination=destination,
                pickup_lat=pickup_lat,
                pickup_long=pickup_lon,
                dest_lat=dest_lat,
                dest_long=dest_lon,
                load_description=load_description
            )
            fare = trip.calculate_fare(distance_km, estimated_time_minutes, surge)
            trip.accepted_fare = fare
            await database_sync_to_async(trip.save)()

            user_data = await self.get_user_details(self.scope["user"])
            
            response_data = {
                "message": "Trip created successfully",
                "trip_id": str(trip.id),
                "estimated_fare": fare,
                "distance_km": distance_km,
                "estimated_time_minutes": estimated_time_minutes,
                "pickup": pickup,
                "destination": destination,
                "vehicle_type": vehicle_type,
                "load_description": load_description,
                "user_info": user_data
            }
            
            await self.channel_layer.group_send(
                self.user_group_name, {"type": "trip_status_update", "data": response_data}
            )
            await self.channel_layer.group_send(
                self.driver_group_name, 
                {"type": "trip_request_notification", "data": response_data}
            )
        else:
            pass

    async def trip_status_update(self, event):
        """Send trip status update to WebSocket client."""
        await self.send(text_data=json.dumps(event["data"]))

    async def trip_request_notification(self, event):
        """Send trip request notification to driver with all necessary details."""
        await self.send(text_data=json.dumps({
            "type": "new_trip_request",
            "trip_details": event["data"]
        }))

    @database_sync_to_async
    def is_user(self, user_id):
        """Check if the user exists."""
        return User.objects.filter(id=user_id).exists()

    @database_sync_to_async
    def get_user_details(self, user):
        """Get user details to share with the driver."""
        return {
            "id": str(user.id),
            "name": f"{user.first_name} {user.last_name}".strip() or user.email,
            "phone": str(user.phone_number) if user.phone_number else None,
            "rating": None  # User model doesn't have rating
        }

class DriverTripConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Connect driver to WebSocket for trip responses."""
        self.driver_id = self.scope["url_route"]["kwargs"]["driver_id"]
        self.room_group_name = f"driver_{self.driver_id}"
        logger.info(f"Driver connect attempt: {self.driver_id}, User: {self.scope['user']}")

        if isinstance(self.scope["user"], Driver) and self.scope["user"].is_authenticated and await self.is_driver(self.driver_id):
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            logger.info("Driver connection accepted")
        else:
            logger.warning("Driver connection rejected")
            await self.close(code=4403)

    async def disconnect(self, close_code):
        """Disconnect driver from WebSocket."""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Receive driver's acceptance/rejection response."""
        data = json.loads(text_data)
        user_id = data.get("user_id")
        trip_id = data.get("trip_id")
        trip_response_status = data.get("trip_response_status")
        
        if trip_response_status == "rejected":
            await self.channel_layer.group_send(
                f"user_{user_id}", {
                    "type": "trip_rejected", 
                    "status": "rejected",
                    "trip_id": trip_id
                }
            )
        elif trip_response_status == "accepted":
            trip = await self.get_trip(trip_id)
            driver = await self.get_driver(self.driver_id)
            
            if trip and driver:
                trip.driver = driver
                trip.status = "accepted"
                await self.save_trip(trip)
                
                trip_details = await self.get_trip_details(trip)
                driver_details = await self.get_driver_details(driver)
                
                await self.channel_layer.group_send(
                    f"user_{user_id}",
                    {
                        "type": "trip_status_update", 
                        "trip_id": str(trip.id), 
                        "status": "accepted",
                        "driver_info": driver_details,
                        "trip_details": trip_details
                    }
                )
                
                await self.send(
                    text_data=json.dumps({
                        "type": "trip_accepted_confirmation",
                        "trip_id": str(trip.id),
                        "trip_details": trip_details
                    })
                )

    async def trip_rejected(self, event):
        """Notify user that the driver has rejected the trip."""
        await self.send(
            text_data=json.dumps({
                "status": event["status"],
                "trip_id": event.get("trip_id")
            })
        )

    async def trip_status_update(self, event):
        """Send trip status update to user."""
        await self.send(
            text_data=json.dumps({
                "type": "trip_status_update",
                "trip_id": event.get("trip_id"), 
                "status": event.get("status"),
                "driver_info": event.get("driver_info", {}),
                "trip_details": event.get("trip_details", {})
            })
        )

    async def trip_cancelled(self, event):
        """Notify driver that the trip has been cancelled."""
        await self.send(
            text_data=json.dumps({
                "type": "trip_cancelled",
                "user_id": event.get("user_id"), 
                "trip_id": event.get("trip_id"),
                "status": "cancelled"
            })
        )

    async def trip_request_notification(self, event):
        """Send trip request to the driver with all necessary details."""
        await self.send(
            text_data=json.dumps({
                "type": "new_trip_request",
                "trip_details": event["data"]
            })
        )

    @database_sync_to_async
    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    @database_sync_to_async
    def get_driver(self, driver_id):
        try:
            return Driver.objects.get(id=driver_id)
        except Driver.DoesNotExist:
            return None

    @database_sync_to_async
    def get_trip(self, trip_id):
        try:
            return Trip.objects.get(id=trip_id)
        except Trip.DoesNotExist:
            return None

    @database_sync_to_async
    def save_trip(self, trip):
        trip.save()

    @database_sync_to_async
    def get_trip_details(self, trip):
        """Get detailed trip information."""
        return {
            "id": str(trip.id),
            "pickup": trip.pickup,
            "destination": trip.destination,
            "pickup_lat": trip.pickup_lat,
            "pickup_long": trip.pickup_long,
            "dest_lat": trip.dest_lat,
            "dest_long": trip.dest_long,
            "vehicle_type": trip.vehicle_type,
            "load_description": trip.load_description or "",
            "fare": float(trip.accepted_fare) if trip.accepted_fare else None,
            "status": trip.status,
            "created_at": trip.created_at.isoformat() if hasattr(trip, 'created_at') else None
        }

    @database_sync_to_async
    def get_driver_details(self, driver):
        """Get driver details to share with the user."""
        return {
            "id": str(driver.id),
            "name": f"{driver.first_name} {driver.last_name}".strip() or driver.email,
            "phone": str(driver.phone_number) if driver.phone_number else None,
            "vehicle_type": driver.vehicle_type,
            "rating": float(driver.rating) if driver.rating else None,
        }

    @database_sync_to_async
    def is_driver(self, driver_id):
        """Check if the authenticated user matches the driver_id."""
        return str(self.scope["user"].id) == driver_id
