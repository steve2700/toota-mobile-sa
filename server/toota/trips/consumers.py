import json
import logging
from datetime import datetime
from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer
import re
from asyncio import sleep, create_task
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from authentication.models import User, Driver
from .models import Trip
from channels.exceptions import StopConsumer
from payments.models import Payment
from django.db.models import Q
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
            self.ping_task = asyncio.create_task(self.send_ping())
            self.ping_task.add_done_callback(self._handle_task_result)

        else:
            logger.warning("User connection rejected")
            await self.close()

    def _handle_task_result(self, task):
        """Handle any exceptions from completed tasks"""
        try:
            task.result()  # This will raise the exception if the task failed
        except asyncio.CancelledError:
            pass  # Task was cancelled, which is expected during disconnect
        except Exception as e:
            logger.error(f"Task failed with exception: {e}", exc_info=True)

    async def disconnect(self, close_code):
        logger.info(f"Driver disconnecting with code: {close_code}")
        
        # Cancel ping task if it exists and is still running
        if hasattr(self, 'ping_task') and not self.ping_task.done():
            self.ping_task.cancel()
        
        # Remove from channel group
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(self.driver_group_name, self.channel_name)
        
        logger.info(f"User disconnected with code: {close_code}")

    async def receive(self, text_data):
        if not self.driver.is_online:
            return
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
                "driver_details": driver_info
            }
            await self.channel_layer.group_send(self.room_group_name, message)

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from driver: {e}")
            await self.send(text_data=json.dumps({"type":"error", "message": "Invalid JSON format"}))
        except Exception as e:
            logger.error(f"Error processing driver message: {e}", exc_info=True)
            await self.send(text_data=json.dumps({"type":"error", "message": "Internal server error"}))

    async def driver_location_update(self, event):
        await self.send(
            text_data=json.dumps({
                "type": "driver_location_update",
                "message": "location updated successfully"
            })
        )


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
            "rating": float(driver.average_rating),
            "latitude": driver.latitude,
            "longitude": driver.longitude,
            "is_available": driver.is_available,
            "profile_pic": driver.profile_pic.url if driver.profile_pic else None,
            "car_images": [img.image.url for img in driver.car_images.all()],
            "number_plate": driver.number_plate
        }

    async def send_ping(self):
        try:
            while True:
                await self.send(text_data=json.dumps({"type": "ping"}))
                await asyncio.sleep(30)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Ping loop stopped with error: {e}", exc_info=True)

class UserGetLocationConsumer(AsyncWebsocketConsumer):
    """Gets the location of the driver and sends it to the user in real-time."""
    async def connect(self):
        self.driver_id = self.scope["url_route"]["kwargs"]["driver_id"]
        self.driver_group_name = f"driver_{self.driver_id}"

        if self.scope["user"].is_authenticated and await self.is_passenger(self.scope["user"]):
            await self.channel_layer.group_add(self.driver_group_name, self.channel_name)
            await self.accept()
            logger.info("User connection accepted")
            self.ping_task = asyncio.create_task(self.send_ping())
            self.ping_task.add_done_callback(self._handle_task_result)
        else:
            logger.warning("User connection rejected")
            await self.close()

    def _handle_task_result(self, task):
        """Handle any exceptions from completed tasks"""
        try:
            task.result()  # This will raise the exception if the task failed
        except asyncio.CancelledError:
            pass  # Task was cancelled, which is expected during disconnect
        except Exception as e:
            logger.error(f"Task failed with exception: {e}", exc_info=True)

    async def disconnect(self, close_code):
        logger.info(f"User disconnecting with code: {close_code}")
        
        # Cancel ping task if it exists and is still running
        if hasattr(self, 'ping_task') and not self.ping_task.done():
            self.ping_task.cancel()
        
        # Remove from channel group
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(self.driver_group_name, self.channel_name)
        
        logger.info(f"User disconnected with code: {close_code}")
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            self.user_latitude = data.get("user_latitude")
            self.user_longitude = data.get("user_longitude")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from user: {e}")
            await self.send(text_data=json.dumps({"type": "error", "message": "Invalid JSON format"}))
        except Exception as e:
            logger.error(f"Error processing user message: {e}", exc_info=True)
            await self.send(text_data=json.dumps({"type": "error", "message": "Internal server error"}))

    async def driver_location_update(self, event):
        driver_details = event["driver_details"]
        route_data = await asyncio.wait_for(
                    get_route_data(self.user_latitude, self.user_longitude, driver_details['latitude'], driver_details['longitude']),
                    timeout=20
                )
        driver_details["duration"] = route_data['duration']
        driver_details["distance"] = route_data['distance']
        
        await self.send(
            text_data=json.dumps({
                "type": "driver_location_update",
                "driver_details": event["driver_details"]
            })
        )

        await self.channel_layer.group_send(
            "user_{}".format(self.scope["user"].id),
            {
                "type": "send_driver_location",
                "driver_details": driver_details
            }
        )

    @database_sync_to_async
    def is_passenger(self, user):
        return User.objects.filter(id=user.id).exists()

    async def send_ping(self):
        try:
            while True:
                await self.send(text_data=json.dumps({"type": "ping"}))
                await asyncio.sleep(30)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Ping loop stopped with error: {e}", exc_info=True)

        
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
                self.ping_task = asyncio.create_task(self.send_ping())
                self.ping_task.add_done_callback(self._handle_task_result)

            else:
                logger.warning("User connection rejected")
                await self.close(code=4403)
        except Exception as e:
            logger.error(f"Error during connect: {e}", exc_info=True)
            await self.close()

    def _handle_task_result(self, task):
        """Handle any exceptions from completed tasks"""
        try:
            task.result()  # This will raise the exception if the task failed
        except (asyncio.TimeoutError, asyncio.CancelledError):
            pass  # Task was cancelled, which is expected during disconnect
        except Exception as e:
            logger.error(f"Task failed with exception: {e}", exc_info=True)
    
    async def disconnect(self, close_code):
        logger.info(f"User disconnecting with code: {close_code}")
        
        # Cancel ping task if it exists and is still running
        if hasattr(self, 'ping_task') and not self.ping_task.done():
            self.ping_task.cancel()
        
        # Remove from channel group
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(self.user_group_name, self.channel_name)
        
        logger.info(f"User disconnected with code: {close_code}")

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
                pickup_latitude = data.get("pickup_latitude")
                pickup_longitude = data.get("pickup_longitude")
                dest_latitude = data.get("dest_latitude")
                dest_longitude = data.get("dest_longitude")
                load_description = data.get("load_description", "")

                route_data = await asyncio.wait_for(
                    get_route_data(pickup_latitude, pickup_longitude, dest_latitude, dest_longitude),
                    timeout=20
                )
                distance = route_data['distance']
                duration = route_data['duration']

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
                        logger.error(f"Failed to parse duration '{duration}': {e}")
                        return 0.0

                estimated_time_minutes = parse_duration_to_minutes(duration)

                trip = await database_sync_to_async(Trip.objects.create)(
                    user=self.user,
                    vehicle_type=vehicle_type,
                    pickup=pickup,
                    destination=destination,
                    pickup_latitude=pickup_latitude,
                    pickup_longitude=pickup_longitude,
                    dest_latitude=dest_latitude,
                    dest_longitude=dest_longitude,
                    load_description=load_description
                )

                fare = trip.calculate_fare(distance, estimated_time_minutes, surge)
                trip.accepted_fare = fare
                await database_sync_to_async(trip.save)()

                user_data = await self.get_user_details(self.user)

                response_data = {
                    "type": "trip_created",
                    "trip_id": str(trip.id),
                    "estimated_fare": fare,
                    "distance": distance,
                    "estimated_time": duration,
                    "status": "pending"
                }
                await self.send(text_data=json.dumps(response_data))

            except asyncio.TimeoutError:
                logger.error("Timeout getting route data")
                await self.send(text_data=json.dumps({"type": "error", "message": "Route calculation timed out"}))
            except Exception as e:
                logger.error(f"Error creating trip: {e}", exc_info=True)
                await self.send(text_data=json.dumps({"type": "error", "message": "Failed to create trip"}))

        elif action == "confirm_driver":
            try:
                trip_id = data.get("trip_id")
                selected_driver_id = data.get("driver_id")

                trip = await self.get_trip(trip_id)

                driver = await self.get_driver(selected_driver_id)

                if trip and driver and trip.status == "pending":
                    if not driver.is_available or not driver.is_online:
                        available_drivers = await self.get_available_drivers(trip)
                        await self.send(text_data=json.dumps({
                            "type": "select_new_driver",
                            "message": "Driver is not available. Please select another driver.",
                            "available_drivers": available_drivers
                        }))
                    else:

                        payment = await self.get_payment_for_trip(trip_id)           

                        if not payment:
                            await self.send(text_data=json.dumps({"type": "error", "message": "Payment not found. Please complete payment before requesting a driver."}))
                            return

                        if payment.payment_method != "cash" and (payment.status != "success" or payment.amount != trip.accepted_fare or not trip.is_paid):
                            await self.send(text_data=json.dumps({"type": "error", "message": "Card payment not completed. Please complete payment before requesting a driver."}))
                            return

                        trip_details = await self.get_trip_details(trip)
                        driver_details = await self.get_driver_details(driver)
                        trip_user = await sync_to_async(lambda: trip.user)()
                        user_details = await self.get_user_details(trip_user)

                        await self.send(text_data=json.dumps({
                            "type": "awaiting_driver_response",
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

                        await self.await_driver_response(trip_id=str(trip.id), selected_driver_id=selected_driver_id)
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
                available_drivers = await self.get_available_drivers(trip)
                await self.send(text_data=json.dumps({
                    "type": "select_new_driver",
                    "message": "Driver is not available. Please select another driver.",
                    "available_drivers": available_drivers
                }))

                logger.info(f"Driver {selected_driver_id} did not respond for trip {trip_id}. Trip reset.")
            else:
                logger.info(f"Driver {selected_driver_id} responded for trip {trip_id} with status '{trip.status}'.")

        except asyncio.CancelledError:
            logger.warning(f"Await driver response task cancelled for trip {trip_id}")
        except Exception as e:
            logger.error(f"Error in await_driver_response for trip {trip_id}: {e}", exc_info=True)

    async def trip_request_notification(self, event):
        await self.send(text_data=json.dumps({
            "type": "new_trip_request",
            "trip_details": event["data"]
        }))

    async def trip_rejected(self, event):
        trip_id = event.get("trip_id")
        selected_driver_id = event.get("driver_id")
        trip = await self.get_trip(trip_id)

        if trip.status == "pending":
            # Reset the assigned driver
            trip.driver = None
            await self.save_trip(trip)

            # Get a fresh list of available drivers
            available_drivers = await self.get_available_drivers(trip)

            # Notify the rider to select another driver
            await self.send(text_data=json.dumps({
                "type": "select_new_driver",
                "message": "Driver is not available. Please select another driver.",
                "available_drivers": available_drivers
            }))

            logger.info(f"Driver {selected_driver_id} did not respond for trip {trip_id}. Trip reset.")
        else:
            logger.info(f"Driver {selected_driver_id} responded for trip {trip_id} with status '{trip.status}'.")


    async def trip_status_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "trip_status_update",
            "trip_id": event.get("trip_id"), 
            "status": event.get("status"),
        }))

    @database_sync_to_async
    def get_user_details(self, user):
        return {
            "id": str(user.id),
            "name": f"{user.first_name} {user.last_name}",
            "phone": str(user.phone_number) if user.phone_number else None,
        }

    @database_sync_to_async
    def is_user(self, user):
        return User.objects.filter(id=user.id).exists()

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
        return {
            "id": str(trip.id),
            "pickup": trip.pickup,
            "destination": trip.destination,
            "pickup_latitude": trip.pickup_latitude,
            "pickup_longitude": trip.pickup_longitude,
            "dest_latitude": trip.dest_latitude,
            "dest_longitude": trip.dest_longitude,
            "vehicle_type": trip.vehicle_type,
            "load_description": trip.load_description or "",
            "fare": float(trip.accepted_fare) if trip.accepted_fare else None,
            "status": trip.status,
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
        drivers = find_nearest_drivers(trip.pickup_latitude, trip.pickup_longitude, [trip.vehicle_type])
        return drivers

    @database_sync_to_async
    def get_payment_for_trip(self, trip_id):
        return (
            Payment.objects
            .filter(
                trip_id=trip_id,
                user=self.user
            )
            .filter(Q(status="success") | Q(payment_method="cash"))
            .first()
        )

    async def send_ping(self):
        try:
            while True:
                await self.send(text_data=json.dumps({"type": "ping"}))
                await asyncio.sleep(30)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Ping loop stopped with error: {e}", exc_info=True)


class DriverTripConsumer(AsyncWebsocketConsumer):
    """Handles trip requests to drivers in real-time with improved stability."""
    
    async def connect(self):
        user = self.scope["user"]
        
        if user.is_authenticated and await self.is_driver(user):
            self.driver = user
            self.driver_group_name = f"driver_{self.driver.id}"
            
            await self.channel_layer.group_add(self.driver_group_name, self.channel_name)
            await self.accept()

            logger.info(f"Driver {self.driver.id} connection accepted")
            
            # Start heartbeat / ping loop
            self.ping_task = asyncio.create_task(self.send_ping())
            self.ping_task.add_done_callback(self._handle_task_result)

        else:
            logger.warning("Driver connection rejected")
            await self.close(code=4403)

    def _handle_task_result(self, task):
        """Handle any exceptions from completed tasks"""
        try:
            task.result()  # This will raise the exception if the task failed
        except (asyncio.TimeoutError, asyncio.CancelledError):
            pass  # Task was cancelled, which is expected during disconnect
        except Exception as e:
            logger.error(f"Task failed with exception: {e}", exc_info=True)

    async def disconnect(self, close_code):        
        logger.info(f"Driver disconnecting with code: {close_code}")
        
        # Cancel ping task if it exists and is still running
        if hasattr(self, 'ping_task') and not self.ping_task.done():
            self.ping_task.cancel()
        
        # Remove from channel group
        if hasattr(self, 'driver_group_name'):
            await self.channel_layer.group_discard(self.driver_group_name, self.channel_name)
        
        logger.info(f"Driver disconnected with code: {close_code}")

    async def receive(self, text_data):
        if not self.driver.is_available or not self.driver.is_online:
            return
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return
        trip_id = data.get("trip_id")
        driver_response = data.get("driver_response")

        if not trip_id:
            await self.send(text_data=json.dumps({"error": "trip_id is required"}))
            return

        trip = await self.get_trip(trip_id)
        if not trip:
            await self.send(text_data=json.dumps({"error": "Trip not found"}))
            return

        if driver_response == "reject":
            user_id = (await sync_to_async(lambda: trip.user.id)())
            await self.channel_layer.group_send(
                f"user_{user_id}",
                {
                    "type": "trip_rejected",
                    "trip_id": str(trip.id),
                    "driver_id": str(self.driver.id)
                }
            )

            await self.send(text_data=json.dumps({
                "type": "trip_rejected",
                "message": f"Trip {trip.id} rejected"
            }))

        elif driver_response == "accept":
            user_id = (await sync_to_async(lambda: trip.user.id)())

            payment = await self.get_payment_for_trip(trip_id)

            if payment and payment.payment_method != "cash" and payment.status != "success" and not trip.is_paid:
                await self.send(text_data=json.dumps({
                    "error": "Card payment not completed. Cannot accept trip."
                }))
                return

            trip.driver = self.driver
            trip.status = "accepted"
            self.driver.is_available = False

            await self.save_driver(self.driver)
            await self.save_trip(trip)

            await self.channel_layer.group_send(
                f"user_{user_id}",
                {
                    "type": "trip_status_update",
                    "trip_id": str(trip.id),
                    "status": "accepted",
                }
            )
            await self.send(text_data=json.dumps({"type": "trip_status_update", "message": f"Trip {trip.id} accepted"}))

        else:
            logger.warning(f"Unknown driver response status: {driver_response}")
            await self.send(text_data=json.dumps({
                "error": f"Unknown response status: {driver_response}"
            }))


    async def trip_request_notification(self, event):
        if not self.driver.is_available or not self.driver.is_online:
            return
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
    def get_available_drivers(self, trip):
        drivers = find_nearest_drivers(trip.pickup_lat, trip.pickup_long, [trip.vehicle_type])
        return drivers

    @database_sync_to_async
    def get_payment_for_trip(self, trip_id):
        return (
            Payment.objects
            .filter(
                trip_id=trip_id,
            )
            .filter(Q(status="success") | Q(payment_method="cash"))
            .first()
        )


    @database_sync_to_async
    def is_driver(self, driver):
        return Driver.objects.filter(id=driver.id).exists()
    
    async def send_ping(self):
        try:
            while True:
                await self.send(text_data=json.dumps({"type": "ping"}))
                await asyncio.sleep(30)
        except (asyncio.TimeoutError, asyncio.CancelledError):
            pass
        except Exception as e:
            logger.error(f"Ping loop stopped with error: {e}", exc_info=True)

class UpdateTripStatusConsumer(AsyncWebsocketConsumer):
    """Updates the status of the trip in real-time, notifying both driver and user."""
    
    async def connect(self):
        self.trip_id = self.scope["url_route"]["kwargs"]["trip_id"]
        user = self.scope["user"]

        if user.is_authenticated:
            self.trip_group_name = f'trip_{self.trip_id}'
            await self.channel_layer.group_add(self.trip_group_name, self.channel_name)
            await self.accept()

            if await self.is_driver(user):
                self.user_role = "driver"
                logger.info("Driver connection accepted")
            else:
                self.user_role = "user"
                logger.info("User connection accepted")
            self.ping_task = asyncio.create_task(self.send_ping())
            self.ping_task.add_done_callback(self._handle_task_result)
        else:
            logger.warning("Unauthenticated connection rejected")
            await self.close(code=4403)

    def _handle_task_result(self, task):
        try:
            task.result()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Task failed with exception: {e}", exc_info=True)

    async def disconnect(self, close_code):
        logger.info(f"User disconnecting with code: {close_code}")
        if hasattr(self, 'ping_task') and not self.ping_task.done():
            self.ping_task.cancel()
        if hasattr(self, 'trip_group_name'):
            await self.channel_layer.group_discard(self.trip_group_name, self.channel_name)
        logger.info(f"User disconnected with code: {close_code}")

    async def receive(self, text_data):
        if self.user_role == 'driver' and not self.scope["user"].is_online:
            return

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        self.trip = await self.get_trip(self.trip_id)
        if self.trip is None:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Trip not found"
            }))
            return

        payment = await self.get_payment_for_trip(self.trip_id)
        if payment is None:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Payment not found"
            }))
            return

        trip_status = data.get('status')

        if self.user_role == "driver":
            await self.update_trip_status(trip_status)

            if trip_status == "arrived at pickup" and payment.payment_method == "cash" and payment.status == "pending":
                await self.update_trip_status(trip_status)
                await self.channel_layer.group_send(
                    self.trip_group_name,
                    {
                        'type': 'trip_payment_update',
                        "payment_amount": str(payment.amount),
                    })
                await self.send(text_data=json.dumps({
                    "type": "trip_payment_update",
                    "message": f"You must collect {payment.currency}{payment.amount} from user before pickup"
                }))
            else:
                await self.update_trip_status(trip_status)
                await self.channel_layer.group_send(
                    self.trip_group_name,
                    {
                        'type': 'trip_status_update',
                        'trip_status': trip_status,
                    }
                )
                await self.send(text_data=json.dumps({
                    "type": "trip_status_update",
                    "message": f"Trip status updated"
                }))
        else:
            await self.send(text_data=json.dumps({
                "type": "info",
                "message": "User cannot update trip status"
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
        return (
            Payment.objects
            .filter(trip_id=trip_id)
            .filter(Q(status="success") | Q(payment_method="cash"))
            .first()
        )

    @database_sync_to_async
    def is_driver(self, user):
        return Driver.objects.filter(id=user.id).exists()

    async def send_ping(self):
        try:
            while True:
                await self.send(text_data=json.dumps({"type": "ping"}))
                await asyncio.sleep(30)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Ping loop stopped with error: {e}", exc_info=True)

    async def trip_status_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "trip_status_update",
            "message": f"status updated to {event['trip_status']}"
        }))


class UserGetAvailableDrivers(AsyncWebsocketConsumer):
    """Handles requests for available drivers in real-time."""

    async def connect(self):
        try:
            if self.scope["user"].is_authenticated and await self.is_user(self.scope['user']):
                self.user = self.scope.get("user")
                self.user_id = self.user.id
                self.user_group_name = f"user_{self.user_id}"
                await self.channel_layer.group_add(self.user_group_name, self.channel_name)
                await self.accept()
                logger.info(f"{self.user} connection accepted")
                self.ping_task = asyncio.create_task(self.send_ping())
                # Keep track of the task to properly cancel it later
                self.ping_task.add_done_callback(self._handle_task_result)
            else:
                logger.warning("User connection rejected")
                await self.close(code=4403)
        except Exception as e:
            logger.error(f"Error during connect: {e}", exc_info=True)
            await self.close()

    def _handle_task_result(self, task):
        """Handle any exceptions from completed tasks"""
        try:
            task.result()  # This will raise the exception if the task failed
        except asyncio.CancelledError:
            pass  # Task was cancelled, which is expected during disconnect
        except Exception as e:
            logger.error(f"Task failed with exception: {e}", exc_info=True)

    async def disconnect(self, close_code):
        logger.info(f"User disconnecting with code: {close_code}")
        
        # Cancel ping task if it exists and is still running
        if hasattr(self, 'ping_task') and not self.ping_task.done():
            self.ping_task.cancel()
        
        # Remove from channel group
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(self.user_group_name, self.channel_name)
        
        logger.info(f"User disconnected with code: {close_code}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            logger.warning("Invalid JSON received.")
            return

        user_latitude = data.get('user_latitude')
        user_longitude = data.get('user_longitude')
        vehicle_type = data.get('vehicle_type', [])

        if not user_latitude or not user_longitude:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Missing user location."
            }))
            return

        # Store location for later use
        self.user_location = (user_latitude, user_longitude)
        
        # Find drivers
        drivers = await sync_to_async(find_nearest_drivers)(user_latitude, user_longitude, vehicle_type)
        if not drivers:
            await self.send(text_data=json.dumps({
                "type": "nearest_drivers",
                "nearest_drivers": []
            }))
            return

        # Process driver data with proper error handling
        nearest_drivers = []
        for driver in drivers:
            print(driver)
            try:
                # Now we can call the async function directly
                route_data = await asyncio.wait_for(
                    get_route_data(user_latitude, user_longitude, driver['latitude'], driver['longitude']),
                    timeout=20  # 5-second timeout per request
                )
                nearest_drivers.append({
                    "driver": driver,
                    "route_data": route_data
                })
            except asyncio.TimeoutError:
                logger.warning(f"Timeout getting route data for driver ")
            except Exception as e:
                logger.error(f"Error processing driver: {e}", exc_info=True)
        
        # Send results
        await self.send(text_data=json.dumps({
            "type": "nearest_drivers",
            "nearest_drivers": nearest_drivers
        }))

    async def send_driver_location(self, event):
        if not hasattr(self, 'user_location'):
            return

        user_lat, user_lon = self.user_location
        vehicle_type = [] 

        try:
            drivers = await sync_to_async(find_nearest_drivers)(user_lat, user_lon, vehicle_type)
            
            nearest_drivers = []
            for driver in drivers:
                try:
                    # Now we can call the async function directly
                    route_data = await asyncio.wait_for(
                        get_route_data(user_latitude, user_longitude, driver['latitude'], driver['longitude']),
                        timeout=20 
                    )
                    nearest_drivers.append({
                        "driver": driver,
                        "route_data": route_data
                    })
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout getting route data for driver {driver.id}")
                except Exception as e:
                    logger.error(f"Error processing driver {driver.id}: {e}", exc_info=True)
            
            await self.send(text_data=json.dumps({
                "type": "nearest_drivers",
                "nearest_drivers": nearest_drivers
            }))
        except Exception as e:
            logger.error(f"Error in send_driver_location: {e}", exc_info=True)

    @database_sync_to_async
    def is_user(self, user):
        return User.objects.filter(id=user.id).exists()

    async def send_ping(self):
        try:
            while True:
                await self.send(text_data=json.dumps({"type": "ping"}))
                await asyncio.sleep(30)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Ping loop stopped with error: {e}", exc_info=True)