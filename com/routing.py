
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/com/$', consumers.ChatConsumer.as_asgi()),  # Ensure this is correct
]
