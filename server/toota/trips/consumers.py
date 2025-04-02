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
                  logger.debug(f"Ping sent to user {self.scope['user'].id}")
                  await sleep(30)  # Ping every 30 seconds

       
        except Exception as e:
            logger.error(f"Ping loop stopped for user {self.scope['user'].id}: {e}")

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

