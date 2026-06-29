from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/event/<int:event_id>/', consumers.EventConsumer.as_asgi()),
]
