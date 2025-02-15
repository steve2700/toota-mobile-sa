import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "toota.settings")  # Move this to the top
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from trips.routing import websocket_urlpatterns  # Import WebSocket routes

        
application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Handles HTTP requests
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)  # Handles WebSocket requests
    ),
})
