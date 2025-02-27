import json
import logging
import re
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from authentication.models import User, Driver
from .models import Trip
from .utils import get_route_data, find_nearest_drivers

logger = logging.getLogger(__name__)

class DriverLocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Connect driver to WebSocket for location updates and trip notifications."""
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
        """Handle driver location updates and trip responses."""
        try:
            data = json.loads(text_data)
            if "latitude" in data and "longitude" in data:
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
            elif "trip_id" in data and "response" in data:
                trip_id = data.get("trip_id")
                response = data.get("response")
                trip = await self.get_trip(trip_id)
                
                if trip and trip.driver and trip.driver.id == self.driver_id and trip.status == "pending":
                    if response == "accept":
                        trip.status = "accepted"
                        await self.save_trip(trip)
                        trip_details = await self.get_trip_details(trip)
                        driver_details = await self.get_driver_details(trip.driver)
                        
                        await self.channel_layer.group_send(
                            f"user_{trip.user.id}",
                            {
                                "type": "trip_status_update",
                                "data": {
                                    "message": "Driver accepted your trip",
                                    "trip_id": str(trip.id),
                                    "status": "accepted",
                                    "driver_info": driver_details,
                                    "trip_details": trip_details
                                }
                            }
                        )
                        await self.send(
                            text_data=json.dumps({
                                "type": "trip_accepted_confirmation",
                                "trip_id": str(trip.id),
                                "trip_details": trip_details
                            })
                        )
                    elif response == "reject":
                        trip.driver = None
                        trip.status = "pending"
                        await self.save_trip(trip)
                        await self.channel_layer.group_send(
                            f"user_{trip.user.id}",
                            {
                                "type": "trip_status_update",
                                "data": {
                                    "message": "Driver rejected your trip - select another driver",
                                    "trip_id": str(trip.id),
                                    "status": "pending",
                                    "available_drivers": await self.get_available_drivers(trip)
                                }
                            }
                        )
                        await self.send(
                            text_data=json.dumps({
                                "message": "Trip request rejected",
                                "trip_id": str(trip.id)
                            })
                        )
            else:
                logger.warning(f"Unknown message type from driver: {data}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from driver: {e}")
            await self.send(text_data=json.dumps({"error": "Invalid JSON format"}))
        except Exception as e:
            logger.error(f"Error processing driver message: {e}", exc_info=True)
            await self.send(text_data=json.dumps({"error": "Internal server error"}))

    async def driver_location_update(self, event):
        """Send updated location to all connected clients."""
        await self.send(
            text_data=json.dumps(
                {
                    "latitude": event["latitude"],
                    "longitude": event["longitude"],
                    "driver_id": event["driver_id"],
                }
            )
        )

    async def trip_request_notification(self, event):
        """Send trip request notification to driver."""
        await self.send(
            text_data=json.dumps({
                "type": "new_trip_request",
                "trip_details": event["data"]
            })
        )

    async def trip_status_update(self, event):
        """Send trip status updates to driver."""
        await self.send(
            text_data=json.dumps(event["data"])
        )

    @database_sync_to_async
    def is_driver(self, driver_id):
        return str(self.scope["user"].id) == driver_id

    @database_sync_to_async
    def get_driver(self, driver_id):
        try:
            return Driver.objects.get(id=driver_id)
        except Driver.DoesNotExist:
            return None

    @database_sync_to_async
    def save_driver(self, driver):
        driver.save()

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
        route_data = get_route_data(trip.pickup_lat, trip.pickup_long, trip.dest_lat, trip.dest_long)
        distance_km = route_data.get("distance_km", 0.0)
        duration_str = route_data.get("duration", "0 min")
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
            "distance_km": distance_km,
            "estimated_time": duration_str,
            "created_at": trip.created_at.isoformat() if hasattr(trip, 'created_at') else None
        }

    @database_sync_to_async
    def get_driver_details(self, driver):
        return {
            "id": str(driver.id),
            "name": f"{driver.first_name} {driver.last_name}".strip() or driver.email,
            "first_name": driver.first_name,
            "last_name": driver.last_name,
            "phone": str(driver.phone_number) if driver.phone_number else None,
            "vehicle_type": driver.vehicle_type,
            "rating": float(driver.rating) if driver.rating else None,
        }

    @database_sync_to_async
    def get_available_drivers(self, trip):
        drivers = find_nearest_drivers(trip.pickup_lat, trip.pickup_long, [trip.vehicle_type])
        return [driver["driver"] for driver in drivers]

class PassengerGetLocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
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
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def driver_location_update(self, event):
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
        return User.objects.filter(id=user.id).exists()

class TripRequestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.driver_id = self.scope["url_route"]["kwargs"]["driver_id"]
        self.user_id = self.scope["user"].id if hasattr(self.scope["user"], 'id') else None
        self.user_group_name = f"user_{self.user_id}"
        logger.info(f"User connect attempt: {self.user_id}, User: {self.scope['user']}")

        if isinstance(self.scope["user"], User) and self.scope["user"].is_authenticated and await self.is_user(self.user_id):
            await self.channel_layer.group_add(self.user_group_name, self.channel_name)
            await self.accept()
            logger.info("User connection accepted")
        else:
            logger.warning("User connection rejected")
            await self.close(code=4403)

    async def disconnect(self, close_code):
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(self.user_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
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
                logger.info(f"Route data received: {route_data}")

                distance_km = route_data.get("distance_km", 0.0)
                duration_str = route_data.get("duration", "0 min")

                def parse_duration_to_minutes(duration_str):
                    try:
                        hours = re.search(r"(\d+)\s*hour", duration_str)
                        minutes = re.search(r"(\d+)\s*min", duration_str)
                        seconds = re.search(r"(\d+)\s*sec", duration_str)
                        total_minutes = 0.0
                        if hours:
                            total_minutes += float(hours.group(1)) * 60
                        if minutes:
                            total_minutes += float(minutes.group(1))
                        if seconds:
                            total_minutes += float(seconds.group(1)) / 60
                        return total_minutes
                    except Exception as e:
                        logger.error(f"Failed to parse duration '{duration_str}': {e}")
                        return 0.0

                estimated_time_minutes = parse_duration_to_minutes(duration_str)
                duration_formatted = duration_str

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

                available_drivers = await database_sync_to_async(find_nearest_drivers)(
                    pickup_lat, pickup_lon, [vehicle_type]
                )
                drivers_list = [driver["driver"] for driver in available_drivers]

                user_data = await self.get_user_details(self.scope["user"])
                
                response_data = {
                    "message": "Trip created successfully - select a driver",
                    "trip_id": str(trip.id),
                    "estimated_fare": fare,
                    "distance_km": distance_km,
                    "estimated_time": duration_formatted,
                    "pickup": pickup,
                    "destination": destination,
                    "vehicle_type": vehicle_type,
                    "load_description": load_description,
                    "user_info": user_data,
                    "available_drivers": drivers_list,
                    "status": "pending"
                }
                
                await self.send(text_data=json.dumps(response_data))

            elif action == "confirm_driver":
                trip_id = data.get("trip_id")
                selected_driver_id = data.get("driver_id")
                
                trip = await self.get_trip(trip_id)
                driver = await self.get_driver(selected_driver_id)
                
                if trip and driver and trip.status == "pending":
                    trip.driver = driver
                    await self.save_trip(trip)

                    trip_details = await self.get_trip_details(trip)
                    driver_details = await self.get_driver_details(driver)
                    
                    await self.send(text_data=json.dumps({
                        "message": "Awaiting driver response",
                        "trip_id": str(trip.id),
                        "status": "pending",
                        "driver_info": driver_details
                    }))
                    
                    await self.channel_layer.group_send(
                        f"driver_{selected_driver_id}",
                        {
                            "type": "trip_request_notification",
                            "data": {
                                "trip_id": str(trip.id),
                                "estimated_fare": float(trip.accepted_fare),
                                "distance_km": trip_details["distance_km"],
                                "estimated_time": trip_details["estimated_time"],
                                "pickup": trip.pickup,
                                "destination": trip.destination,
                                "vehicle_type": trip.vehicle_type,
                                "load_description": trip.load_description,
                                "user_info": await self.get_user_details(trip.user)
                            }
                        }
                    )

                    await asyncio.sleep(30)  # 30-second timeout
                    trip = await self.get_trip(trip_id)  # Refresh trip
                    if trip.status == "pending":
                        trip.driver = None
                        await self.save_trip(trip)
                        await self.send(text_data=json.dumps({
                            "message": "Driver did not respond - select another driver",
                            "trip_id": str(trip.id),
                            "status": "pending",
                            "available_drivers": await self.get_available_drivers(trip)
                        }))
            else:
                logger.warning(f"Unknown action: {action}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            await self.send(text_data=json.dumps({"error": "Invalid JSON format"}))
        except Exception as e:
            logger.error(f"Error processing trip request: {e}", exc_info=True)
            await self.send(text_data=json.dumps({"error": "Internal server error"}))

    async def trip_status_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))

    async def trip_request_notification(self, event):
        await self.send(text_data=json.dumps({
            "type": "new_trip_request",
            "trip_details": event["data"]
        }))

    @database_sync_to_async
    def is_user(self, user_id):
        return User.objects.filter(id=user_id).exists()

    @database_sync_to_async
    def get_user_details(self, user):
        return {
            "id": str(user.id),
            "name": f"{user.first_name} {user.last_name}".strip() or user.email,
            "phone": str(user.phone_number) if user.phone_number else None,
            "rating": None
        }

    @database_sync_to_async
    def get_trip(self, trip_id):
        try:
            return Trip.objects.get(id=trip_id)
        except Trip.DoesNotExist:
            return None

    @database_sync_to_async
    def get_driver(self, driver_id):
        try:
            return Driver.objects.get(id=driver_id)
        except Driver.DoesNotExist:
            return None

    @database_sync_to_async
    def save_trip(self, trip):
        trip.save()

    @database_sync_to_async
    def get_trip_details(self, trip):
        route_data = get_route_data(trip.pickup_lat, trip.pickup_long, trip.dest_lat, trip.dest_long)
        distance_km = route_data.get("distance_km", 0.0)
        duration_str = route_data.get("duration", "0 min")
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
            "distance_km": distance_km,
            "estimated_time": duration_str,
            "created_at": trip.created_at.isoformat() if hasattr(trip, 'created_at') else None
        }

    @database_sync_to_async
    def get_driver_details(self, driver):
        return {
            "id": str(driver.id),
            "name": f"{driver.first_name} {driver.last_name}".strip() or driver.email,
            "first_name": driver.first_name,
            "last_name": driver.last_name,
            "phone": str(driver.phone_number) if driver.phone_number else None,
            "vehicle_type": driver.vehicle_type,
            "rating": float(driver.rating) if driver.rating else None,
        }

    @database_sync_to_async
    def get_available_drivers(self, trip):
        drivers = find_nearest_drivers(trip.pickup_lat, trip.pickup_long, [trip.vehicle_type])
        return [driver["driver"] for driver in drivers]

class DriverTripConsumer(AsyncWebsocketConsumer):
    async def connect(self):
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
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
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
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            await self.send(text_data=json.dumps({"error": "Invalid JSON format"}))
        except Exception as e:
            logger.error(f"Error processing trip response: {e}", exc_info=True)
            await self.send(text_data=json.dumps({"error": "Internal server error"}))

    async def trip_rejected(self, event):
        await self.send(
            text_data=json.dumps({
                "status": event["status"],
                "trip_id": event.get("trip_id")
            })
        )

    async def trip_status_update(self, event):
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
        await self.send(
            text_data=json.dumps({
                "type": "trip_cancelled",
                "user_id": event.get("user_id"), 
                "trip_id": event.get("trip_id"),
                "status": "cancelled"
            })
        )

    async def trip_request_notification(self, event):
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
        route_data = get_route_data(trip.pickup_lat, trip.pickup_long, trip.dest_lat, trip.dest_long)
        distance_km = route_data.get("distance_km", 0.0)
        duration_str = route_data.get("duration", "0 min")
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
            "distance_km": distance_km,
            "estimated_time": duration_str,
            "created_at": trip.created_at.isoformat() if hasattr(trip, 'created_at') else None
        }

    @database_sync_to_async
    def get_driver_details(self, driver):
        return {
            "id": str(driver.id),
            "name": f"{driver.first_name} {driver.last_name}".strip() or driver.email,
            "first_name": driver.first_name,
            "last_name": driver.last_name,
            "phone": str(driver.phone_number) if driver.phone_number else None,
            "vehicle_type": driver.vehicle_type,
            "rating": float(driver.rating) if driver.rating else None,
        }

    @database_sync_to_async
    def is_driver(self, driver_id):
        return str(self.scope["user"].id) == driver_id
