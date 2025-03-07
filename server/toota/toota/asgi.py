import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "toota.settings")
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from toota.middleware import JWTMiddleware  # Import custom JWT middleware
from trips.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Handles HTTP requests
    "websocket": JWTMiddleware(
        URLRouter(websocket_urlpatterns)  # Handles WebSocket requests with JWT
    ),
})
