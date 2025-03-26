import json
import logging
from datetime import datetime
from asgiref.sync import sync_to_async
import re
from asyncio import sleep, create_task
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from authentication.models import User, Driver
from .models import Trip
from channels.exceptions import StopConsumer
from payments.models import Payment
from .utils import get_route_data, find_nearest_drivers, is_peak_hour_or_festive


logger = logging.getLogger(__name__)


class DriverLocationConsumer(AsyncWebsocketConsumer):
    """Updates the location of the driver in real-time."""
    async def connect(self):

        if self.scope["user"].is_authenticated and await self.is_driver(self.scope["user"]):
            self.driver = self.scope.get("user")
            self.driver_id = self.driver.id
            self.room_group_name = f"driver_{self.driver_id}"
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            logger.info("User connection accepted")
            self.ping_task = create_task(self.send_ping())

        else:
            logger.warning("User connection rejected")
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        if hasattr(self, 'ping_task'):
            self.ping_task.cancel()
        raise StopConsumer()

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            latitude = data.get("latitude")
            longitude = data.get("longitude")

            self.driver.latitude = latitude
            self.driver.longitude = longitude
            await self.save_driver(self.driver)
            driver_info = await self.get_driver_details(self.driver)  # Returns payload of driver details

            # Ensure message is serializable
            message = {
                "type": "driver_location_update",
                "latitude": latitude,
                "longitude": longitude,
                "driver_details": driver_info
            }
            await self.channel_layer.group_send(self.room_group_name, message)

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from driver: {e}")
            await self.send(text_data=json.dumps({"error": "Invalid JSON format"}))
        except Exception as e:
            logger.error(f"Error processing driver message: {e}", exc_info=True)
            await self.send(text_data=json.dumps({"error": "Internal server error"}))


    async def driver_location_update(self, event):
        await self.send(
            text_data=json.dumps({
                "latitude": event["latitude"],
                "longitude": event["longitude"],
                "driver_details": event["driver_details"]
            })
        )

    async def send_ping(self):
        """Periodically sends a ping to the client to keep the connection alive."""
        try:
            while True:
                await self.send(text_data=json.dumps({"type": "ping"}))
                logger.debug(f"Ping sent to driver {self.driver_id}")
                await sleep(30)  # Ping every 30 seconds
        except Exception as e:
            logger.error(f"Ping loop stopped for driver {self.driver_id}: {e}")

    @database_sync_to_async
    def is_driver(self, driver):
        return Driver.objects.filter(id=driver.id).exists()

    @database_sync_to_async
    def save_driver(self, driver):
        driver.save()

    @database_sync_to_async
    def get_driver_details(self, driver):
        return {
            "id": str(driver.id),
            "name": f"{driver.first_name} {driver.last_name}",
            "email": driver.email,
            "phone": str(driver.phone_number),
            "vehicle_type": driver.vehicle_type,
            "rating": float(driver.rating),
            "is_available": driver.is_available,
            "profile_pic": driver.profile_pic.url if driver.profile_pic else None,
            "car_image": driver.car_images.url if driver.car_images else None,
        }


class UserGetLocationConsumer(AsyncWebsocketConsumer):
    """Gets the location of the driver and sends it to the user in real-time."""
    async def connect(self):
        self.driver_id = self.scope["url_route"]["kwargs"]["driver_id"]
        self.room_group_name = f"driver_{self.driver_id}"

        if self.scope["user"].is_authenticated and await self.is_passenger(self.scope["user"]):
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            logger.info("User connection accepted")
            self.ping_task = create_task(self.send_ping())
        else:
            logger.warning("User connection rejected")
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        if hasattr(self, 'ping_task'):
            self.ping_task.cancel()
        raise StopConsumer()

    async def driver_location_update(self, event):
        await self.send(
            text_data=json.dumps({
                "latitude": event["latitude"],
                "longitude": event["longitude"],
                "driver_details": event["driver_details"]
            })
        )

    async def send_ping(self):
        """Periodically sends a ping to the client to keep the connection alive."""
    try:
        while True:
            await self.send(text_data=json.dumps({"type": "ping"}))
            logger.debug(f"Ping sent to user {self.scope['user'].id}")  # FIXED LINE
            await sleep(30)  # Ping every 30 seconds
    except Exception as e:
        logger.error(f"Ping loop stopped for user {self.scope['user'].id}: {e}")  # FIXED LINE


    @database_sync_to_async
    def is_passenger(self, user):
        return User.objects.filter(id=user.id).exists()

class TripRequestConsumer(AsyncWebsocketConsumer):
    """Handles trip requests from users in real-time."""

    async def connect(self):
        try:
            if self.scope["user"].is_authenticated and await self.is_user(self.scope['user']):
                self.user = self.scope.get("user")
                self.user_id = self.user.id
                self.user_group_name = f"user_{self.user_id}"
                await self.channel_layer.group_add(self.user_group_name, self.channel_name)
                await self.accept()
                logger.info("User connection accepted")
                self.ping_task = create_task(self.send_ping())

            else:
                logger.warning("User connection rejected")
                await self.close(code=4403)
        except Exception as e:
            logger.error(f"Error during connect: {e}", exc_info=True)
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        logger.info(f"User disconnected with code: {close_code}")
        if hasattr(self, 'ping_task'):
            self.ping_task.cancel()
        raise StopConsumer()

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get("action")
        except json.JSONDecodeError:
            return
        if action == "create_trip":
            try:
                now = datetime.now()
                surge = is_peak_hour_or_festive(now)
                vehicle_type = data.get("vehicle_type")
                pickup = data.get("pickup")
                destination = data.get("destination")
                pickup_lat = data.get("pickup_lat")
                pickup_lon = data.get("pickup_lon")
                dest_lat = data.get("dest_lat")
                dest_lon = data.get("dest_lon")
                load_description = data.get("load_description", "")

                route_data = await asyncio.wait_for(
                    database_sync_to_async(get_route_data)(pickup_lat, pickup_lon, dest_lat, dest_lon),
                    timeout=10
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
                    user=self.user,
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

                available_drivers = await self.get_available_drivers(trip)
                user_data = await self.get_user_details(self.user)

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
                    "available_drivers": available_drivers,
                    "status": "pending"
                }

                await self.send(text_data=json.dumps(response_data))

            except asyncio.TimeoutError:
                logger.error("Timeout getting route data")
                await self.send(text_data=json.dumps({"error": "Route calculation timed out"}))
            except Exception as e:
                logger.error(f"Error creating trip: {e}", exc_info=True)
                await self.send(text_data=json.dumps({"error": "Failed to create trip"}))

        elif action == "confirm_driver":
            try:
                trip_id = data.get("trip_id")
                print(f"this is the trip id: {trip_id}")
                selected_driver_id = data.get("driver_id")

                trip = await self.get_trip(trip_id)

                driver = await self.get_driver(selected_driver_id)

                if trip and driver and trip.status == "pending":

                    payment = await asyncio.wait_for(
                        self.get_payment_for_trip(trip_id),
                        timeout=10
                    )

                    if not payment:
                        await self.send(text_data=json.dumps({"error": "Payment not found. Please complete payment before requesting a driver."}))
                        return

                    if payment.payment_method == "card" and (payment.status != "success" or payment.amount != trip.accepted_fare or not trip.is_paid):
                        await self.send(text_data=json.dumps({"error": "Card payment not completed. Please complete payment before requesting a driver."}))
                        return

                    trip_details = await self.get_trip_details(trip)
                    driver_details = await self.get_driver_details(driver)
                    trip_user = await sync_to_async(lambda: trip.user)()
                    user_details = await self.get_user_details(trip_user)

                    await self.send(text_data=json.dumps({
                        "message": "Awaiting driver response",
                        "trip_id": str(trip.id),
                        "status": "pending",
                        "driver_info": driver_details,
                        "payment_info": {
                            "payment_method": payment.payment_method,
                            "payment_status": payment.status,
                            "amount": float(payment.amount),
                            "currency": payment.currency,
                        }
                    }))

                    # Send driver notification
                    await self.channel_layer.group_send(
                        f"driver_{selected_driver_id}",
                        {
                            "type": "trip_request_notification",
                            "data": {
                                "trip_id": str(trip.id),
                                "distance_km": trip_details["distance_km"],
                                "estimated_time": trip_details["estimated_time"],
                                "pickup": trip.pickup,
                                "destination": trip.destination,
                                "vehicle_type": trip.vehicle_type,
                                "load_description": trip.load_description,
                                "user_info": user_details,
                                "payment_info": {
                                    "payment_method": payment.payment_method,
                                    "payment_status": payment.status,
                                    "amount": float(payment.amount),
                                    "currency": payment.currency,
                                }
                            }
                        }
                    )

                    try:
                        await self.await_driver_response(trip_id=str(trip.id), selected_driver_id=selected_driver_id)
                    except asyncio.TimeoutError:
                        logger.warning(f"No driver response for trip {trip_id} after 30s")
                        trip.driver = None
                        await self.save_trip(trip)
                        available_drivers = await self.get_available_drivers(trip)
                        await self.send(text_data=json.dumps({
                            "message": "Driver did not respond - select another driver",
                            "trip_id": str(trip.id),
                            "status": "pending",
                            "available_drivers": available_drivers
                        }))

                else:
                    await self.send(text_data=json.dumps({"error": "Invalid trip or driver"}))

            except asyncio.TimeoutError:
                logger.error("Timeout waiting for payment info or driver response")
                await self.send(text_data=json.dumps({"error": "Operation timed out"}))
            except Exception as e:
                logger.error(f"Error confirming driver: {e}", exc_info=True)
                await self.send(text_data=json.dumps({"error": "Failed to confirm driver"}))
        else:
            await self.send(text_data=json.dumps({"error": f"Unknown action: {action}"}))


    async def await_driver_response(self, trip_id: str, selected_driver_id: str, wait_time: int = 30):
        """
        Waits for a driver response for the given trip within wait_time seconds.
        If the driver does not respond, resets the trip and notifies the client.
        """
        try:
            # Wait asynchronously for the driver's response
            await asyncio.sleep(wait_time)

            # Re-fetch the trip to get the updated status
            trip = await self.get_trip(trip_id)

            # If still pending after wait_time seconds, handle no-response
            if trip.status == "pending":
                # Reset the assigned driver
                trip.driver = None
                await self.save_trip(trip)

                # Get a fresh list of available drivers
                available_drivers = await self.get_available_drivers(trip)

                # Notify the client (rider) that the driver didn't respond
                await self.send(text_data=json.dumps({
                    "message": "Driver did not respond - select another driver",
                    "trip_id": str(trip.id),
                    "status": "pending",
                    "available_drivers": available_drivers
                }))

                logger.info(f"Driver {selected_driver_id} did not respond for trip {trip_id}. Trip reset.")
            else:
                logger.info(f"Driver {selected_driver_id} responded for trip {trip_id} with status '{trip.status}'.")

        except asyncio.CancelledError:
            logger.warning(f"Await driver response task cancelled for trip {trip_id}")
        except Exception as e:
            logger.error(f"Error in await_driver_response for trip {trip_id}: {e}", exc_info=True)


    async def send_ping(self):
        """Periodically sends a ping to the client to keep the connection alive."""
        try:
            while True:
                await self.send(text_data=json.dumps({"type": "ping"}))
                logger.debug(f"Ping sent to user {self.user_id}")
                await sleep(30)  # Ping every 30 seconds
        except Exception as e:
            logger.error(f"Ping loop stopped for user {self.user_id}: {e}")

    async def trip_status_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "trip_status_update",
            "trip_id": event.get("trip_id"), 
            "status": event.get("status"),
            "driver_info": event.get("driver_info", {}),
            "trip_details": event.get("trip_details", {}),
            "payment_info": event.get("payment_info", {})
        }))

    async def trip_request_notification(self, event):
        await self.send(text_data=json.dumps({
            "type": "new_trip_request",
            "trip_details": event["data"]
        }))

    @database_sync_to_async
    def is_user(self, user):
        return User.objects.filter(id=user.id).exists()

    @database_sync_to_async
    def get_user_details(self, user):
        return {
            "id": str(user.id),
            "name": f"{user.first_name} {user.last_name}",
            "phone": str(user.phone_number) if user.phone_number else None,
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
            "phone": str(driver.phone_number) if driver.phone_number else None,
            "vehicle_type": driver.vehicle_type,
            "rating": float(driver.rating) if driver.rating else None,
        }

    @database_sync_to_async
    def get_available_drivers(self, trip):
        drivers = find_nearest_drivers(trip.pickup_lat, trip.pickup_long, [trip.vehicle_type])
        return [driver_data["driver"] for driver_data in drivers]

    @database_sync_to_async
    def get_payment_for_trip(self, trip_id):
        try:
            return Payment.objects.get(trip_id=trip_id, user=self.user)
        except Payment.DoesNotExist:
            return None


class DriverTripConsumer(AsyncWebsocketConsumer):
    """Handles trip requests to drivers in real-time with improved stability."""
    
    async def connect(self):
        user = self.scope["user"]
        
        if user.is_authenticated and await self.is_driver(user):
            self.driver = user
            self.room_group_name = f"driver_{self.driver.id}"
            
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()

            logger.info(f"Driver {self.driver.id} connection accepted")
            
            # Start heartbeat / ping loop
            self.ping_task = create_task(self.send_ping())
            
            # Send welcome message
            await self.send(text_data=json.dumps({
                "message": "Connection established",
                "status": "connected",
                "driver_id": str(self.driver.id)
            }))

        else:
            logger.warning("Driver connection rejected")
            await self.close(code=4403)

    async def disconnect(self, close_code):        
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        logger.info(f"Driver {self.driver.id} disconnected with code: {close_code}")
        if hasattr(self, 'ping_task'):
            self.ping_task.cancel()
        raise StopConsumer()

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)

            # Handle pong (response to ping)
        except json.JSONDecodeError:
            return

        trip_id = data.get("trip_id")
        driver_response_status = data.get("driver_response_status")

        if not trip_id:
            await self.send(text_data=json.dumps({"error": "trip_id is required"}))
            return

        trip = await self.get_trip(trip_id)
        if not trip:
            await self.send(text_data=json.dumps({"error": "Trip not found"}))
            return

        if driver_response_status == "rejected":
            user_id = (await sync_to_async(lambda: trip.user.id)())
            await self.channel_layer.group_send(
                f"user_{user_id}",
                {
                    "type": "trip_rejected",
                    "status": "rejected",
                    "trip_id": trip_id
                }
            )

        elif driver_response_status == "accepted":
            user_id = (await sync_to_async(lambda: trip.user.id)())

            payment = await self.get_payment_for_trip(trip_id)

            if payment and payment.payment_method == "card" and payment.status != "success" and not trip.is_paid:
                await self.send(text_data=json.dumps({
                    "error": "Card payment not completed. Cannot accept trip."
                }))
                return

            trip.driver = self.driver
            trip.status = "accepted"
            self.driver.is_available = False

            await self.save_driver(self.driver)
            await self.save_trip(trip)

            trip_details = await self.get_trip_details(trip)
            driver_details = await self.get_driver_details(self.driver)

            payment_info = {}
            if payment:
                payment_info = {
                    "payment_method": payment.payment_method,
                    "payment_status": payment.status,
                    "amount": float(payment.amount),
                    "currency": payment.currency,
                }

            await self.channel_layer.group_send(
                f"user_{user_id}",
                {
                    "type": "trip_status_update",
                    "trip_id": str(trip.id),
                    "status": "accepted",
                    "driver_info": driver_details,
                    "trip_details": trip_details,
                    "payment_info": payment_info
                }
            )

            await self.send(text_data=json.dumps({"message": f"Trip {trip.id} accepted"}))

        else:
            logger.warning(f"Unknown driver response status: {driver_response_status}")
            await self.send(text_data=json.dumps({
                "error": f"Unknown response status: {driver_response_status}"
            }))

    async def send_ping(self):
        """Periodically sends a ping to the client to keep the connection alive."""
        try:
            while True:
                await self.send(text_data=json.dumps({"type": "ping"}))
                logger.debug(f"Ping sent to driver {self.driver.id}")
                await sleep(30)  # Ping every 30 seconds
        except Exception as e:
            logger.error(f"Ping loop stopped for driver {self.driver.id}: {e}")

    async def trip_rejected(self, event):
        await self.send(text_data=json.dumps({
            "status": event["status"],
            "trip_id": event.get("trip_id")
        }))

    async def trip_status_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "trip_status_update",
            "trip_id": event.get("trip_id"), 
            "status": event.get("status"),
            "driver_info": event.get("driver_info", {}),
            "trip_details": event.get("trip_details", {}),
            "payment_info": event.get("payment_info", {})
        }))

    async def trip_request_notification(self, event):
        await self.send(text_data=json.dumps({
            "type": "new_trip_request",
            "trip_details": event["data"]
        }))

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
    def save_driver(self, driver):
        driver.save()

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
        return [driver_data["driver"] for driver_data in drivers]

    @database_sync_to_async
    def get_payment_for_trip(self, trip_id):
        try:
            return Payment.objects.get(trip_id=trip_id)
        except Payment.DoesNotExist:
            return None

    @database_sync_to_async
    def is_driver(self, driver):
        return Driver.objects.filter(id=driver.id).exists()

class DriverUpdateTripStatusConsumer(AsyncWebsocketConsumer):
    """(Driver socket): updates the status of the trip in real-time, notifying both driver and user."""
    async def connect(self):
        self.trip_id = self.scope["url_route"]["kwargs"]["trip_id"]
        if self.scope["user"].is_authenticated and await self.is_driver(self.scope['user']):
            self.trip_group_name = f'trip_{self.trip_id}'
            await self.channel_layer.group_add(self.trip_group_name, self.channel_name)
            await self.accept()
            logger.info("Driver connection accepted")
            self.ping_task = create_task(self.send_ping())

        else:
            logger.warning("Driver connection rejected")
            await self.close(code=4403)

    async def disconnect(self, close_code):
        if hasattr(self, 'trip_group_name'):
            await self.channel_layer.group_discard(self.trip_group_name, self.channel_name)
            logger.info(f"Driver disconnected with code: {close_code}")
        if hasattr(self, 'ping_task'):
            self.ping_task.cancel()
        raise StopConsumer()

    async def receive(self, text_data):
        data = json.loads(text_data)
        self.trip = await self.get_trip(self.trip_id)
        if self.trip is None:
            await self.send(text_data=json.dumps({
                "error": "Trip not found"
            }))
            return
        payment = await self.get_payment_for_trip(self.trip_id)
        if payment is None:
            await self.send(text_data=json.dumps({
                "error": "Payment not found"
            }))
            return

        trip_status = data.get('trip_status')

        await self.update_trip_status(trip_status)
        if trip_status == "arrived at pickup" and payment.payment_method == "cash" and payment.status == "pending":
            await self.channel_layer.group_send(
                self.trip_group_name,
                {
                    'type': 'trip_payment_update',
                    'payment_status': trip_status,
                    'trip_id': self.trip_id,
                })
        else:
            await self.channel_layer.group_send(
                    self.trip_group_name,
                    {
                        'type': 'trip_status_update',
                        'trip_status': trip_status,
                        'trip_id': self.trip_id
                    }
                )

    async def trip_status_update(self, event):
        pass

    async def trip_payment_update(self, event):
        payment_status = event['payment_status']
        trip_id = event['trip_id']
        await self.send(text_data=json.dumps({
            "payment_status": payment_status,
            "trip_id": trip_id,
            "message": "You must collect payment from user before pickup"
        }))

    @database_sync_to_async
    def update_trip_status(self, status):
        self.trip.status = status
        self.trip.save()

    @database_sync_to_async
    def get_trip(self, trip_id):
        try:
            return Trip.objects.get(id=trip_id)
        except Trip.DoesNotExist:
            return None
    
    @database_sync_to_async
    def get_payment_for_trip(self, trip_id):
        try:
            return Payment.objects.get(trip_id=trip_id)
        except Payment.DoesNotExist:
            return None
        
    @database_sync_to_async
    def is_driver(self, driver):
        return Driver.objects.filter(id=driver.id).exists()
    
    async def send_ping(self):
        """Periodically sends a ping to the client to keep the connection alive."""
        try:
            while True:
                await self.send(text_data=json.dumps({"type": "ping"}))
                logger.debug(f"Ping sent to driver {self.scope['user'].id}")
                await sleep(30)  # Ping every 30 seconds
        except Exception as e:
            logger.error(f"Ping loop stopped for driver {self.scope['user'].id}: {e}")


class UserGetTripStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.trip_id = self.scope['url_route']['kwargs']['trip_id']
        if self.scope["user"].is_authenticated and await self.is_user(self.scope["user"]):
            self.trip_group_name = f"trip_{self.trip_id}"
            await self.channel_layer.group_add(
                self.trip_group_name,
                self.channel_name
            )
            await self.accept()
            logger.info("User connection accepted")
            self.ping_task = create_task(self.send_ping())

        else:
            logger.warning("User connection rejected")
            await self.close(code=4403)

    async def disconnect(self, close_code):
        if hasattr(self, 'trip_group_name'):
            await self.channel_layer.group_discard(self.trip_group_name, self.channel_name)
            logger.info(f"User disconnected with code: {close_code}")
        if hasattr(self, 'ping_task'):
            self.ping_task.cancel()
        raise StopConsumer()

    async def receive(self, text_data):
        # User doesn't need to send anything (optional)
        pass

    async def trip_payment_update(self, event):
        payment_status = event['payment_status']
        trip_id = event['trip_id']
        await self.send(text_data=json.dumps({
            "payment_status": payment_status,
            "trip_id": trip_id,
            "message": "You must make payment before trip starts"
        }))

    # Receive broadcast from the driver
    async def trip_status_update(self, event):
        status = event['trip_status']
        trip_id = event['trip_id']

        await self.send(text_data=json.dumps({
            'trip_id': trip_id,
            'trip_status': status
        }))

    @database_sync_to_async
    def is_user(self, user):
        return User.objects.filter(id=user.id).exists()

    async def send_ping(self):
        """Periodically sends a ping to the client to keep the connection alive."""
        try:
            while True:
                await self.send(text_data=json.dumps({"type": "ping"}))
                logger.debug(f"Ping sent to user {self.scope['user'].id}")
                await sleep(30)  # Ping every 30 seconds
        except Exception as e:
            logger.error(f"Ping loop stopped for user {self.scope['user'].id}: {e}")
