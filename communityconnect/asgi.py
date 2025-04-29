import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import com.routing  # Import your chat app's routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'communityconnect.settings')
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            com.routing.websocket_urlpatterns
        )
    ),
})
