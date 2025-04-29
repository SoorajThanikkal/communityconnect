import os

# ✅ Set this early — before importing anything from Django or your apps
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'communityconnect.settings')

import django
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import com.routing  # Now safe to import

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(
            com.routing.websocket_urlpatterns
        )
})
print("ASGI application started.")