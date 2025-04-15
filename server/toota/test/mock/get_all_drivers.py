import pytest, uuid
import json
from unittest.mock import AsyncMock, MagicMock, patch
from channels.testing import WebsocketCommunicator
from django.test import override_settings
from django.contrib.auth import get_user_model
from trips.consumers import UserGetAvailableDrivers 

User = get_user_model()

@pytest.mark.asyncio
@pytest.mark.django_db
class TestUserGetAvailableDrivers:
    
    async def setup_communicator(self, user=None):
        communicator = WebsocketCommunicator(
            UserGetAvailableDrivers.as_asgi(),
            "ws/trips/drivers/all/"
        )
        if user:
            communicator.scope["user"] = user
        else:
            communicator.scope["user"] = MagicMock(is_authenticated=False)
        return communicator

    async def test_connect_authenticated_user(self):
        email = f"test_{uuid.uuid4().hex}@example.com".lower()
        print(f"Creating user with email: {email}")
        user = await User.objects.acreate(email=email, password="testpass")

        
        communicator = await self.setup_communicator(user)
        
        connected, subprotocol = await communicator.connect()
        assert connected
        assert communicator.scope["user"] == user
        assert communicator.channel_name in communicator.channel_layer.groups[f"user_{user.id}"]
        
        await communicator.disconnect()

    async def test_connect_unauthenticated_user(self):
        communicator = await self.setup_communicator()
        
        connected, subprotocol = await communicator.connect()
        assert not connected
        assert communicator.receive_nothing()
        
        await communicator.disconnect()

    async def test_connect_nonexistent_user(self):
        user = MagicMock(id=999, is_authenticated=True)
        with patch("trips.consumers.UserGetAvailableDrivers.is_user", return_value=False):
            communicator = await self.setup_communicator(user)
            
            connected, subprotocol = await communicator.connect()
            assert not connected
            assert communicator.receive_nothing()
            
            await communicator.disconnect()

    async def test_receive_valid_location(self):
        user = await User.objects.acreate(
            email="test@example.com",
            password="testpass"
        )
        communicator = await self.setup_communicator(user)
        await communicator.connect()

        mock_driver = MagicMock(id=1, latitude=40.0, longitude=-74.0)
        mock_route_data = {"distance": "5km", "duration": "10min"}

        with patch("trips.consumers.find_nearest_drivers", return_value=[mock_driver]), \
             patch("trips.consumers.get_route_data", return_value=mock_route_data):
            
            await communicator.send_json_to({
                "user_latitude": 40.1,
                "user_longitude": -74.1,
            })
            
            response = await communicator.receive_json_from()
            assert response["type"] == "nearest_drivers"
            assert len(response["nearest_drivers"]) == 1
            assert response["nearest_drivers"][0]["route_data"] == mock_route_data
        
        await communicator.disconnect()

    async def test_receive_invalid_json(self):
        user = await User.objects.acreate(
            email="test@example.com",
            password="testpass"
        )
        communicator = await self.setup_communicator(user)
        await communicator.connect()

        await communicator.send_to(text_data="invalid json")
        assert await communicator.receive_nothing()
        
        await communicator.disconnect()

    async def test_receive_missing_location(self):
        user = await User.objects.acreate(
            email="test@example.com",
            password="testpass"
        )
        communicator = await self.setup_communicator(user)
        await communicator.connect()

        await communicator.send_json_to({
        })
        
        response = await communicator.receive_json_from()
        assert response["type"] == "error"
        assert response["message"] == "Missing user location."
        
        await communicator.disconnect()

    async def test_send_driver_location(self):
        user = await User.objects.acreate(
            email="test@example.com",
            password="testpass"
        )
        communicator = await self.setup_communicator(user)
        await communicator.connect()

        mock_driver = MagicMock(id=1, latitude=40.0, longitude=-74.0)
        mock_route_data = {"distance": "5km", "duration": "10min"}

        # Set user_location
        communicator.instance.user_location = (40.1, -74.1)

        with patch("trips.consumers.find_nearest_drivers", return_value=[mock_driver]), \
             patch("trips.consumers.get_route_data", return_value=mock_route_data):
            
            await communicator.instance.send_driver_location({"type": "driver_location"})
            
            response = await communicator.receive_json_from()
            assert response["type"] == "nearest_drivers"
            assert len(response["nearest_drivers"]) == 1
            assert response["nearest_drivers"][0]["route_data"] == mock_route_data
        
        await communicator.disconnect()

    async def test_ping_task(self):
        user = await User.objects.acreate(
            email="test@example.com",
            password="testpass"
        )
        communicator = await self.setup_communicator(user)
        await communicator.connect()

        # Wait for first ping
        response = await communicator.receive_json_from(timeout=1)
        assert response["type"] == "ping"

        await communicator.disconnect()
        assert communicator.instance.ping_task.done()
