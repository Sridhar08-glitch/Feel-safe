import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from .models import Room, Message

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.channel_layer = get_channel_layer()  # ✅ Ensure channel_layer is set
        self.room_name = f"room_{self.scope['url_route']['kwargs']['room_name']}"
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        data_json = json.loads(text_data)
        event = {"type": "send_message", "message": data_json}
        await self.channel_layer.group_send(self.room_name, event)

    async def send_message(self, event):
        data = event["message"]
        message = await self.create_message(data=data)

        if message:
            response = {
                "sender": message.sender.username if hasattr(message.sender, "username") else str(message.sender),
                "message": message.message,
                "timestamp": str(message.timestamp),
            }
            await self.send(text_data=json.dumps({"message": response}))

    @database_sync_to_async
    def create_message(self, data):
        try:
            get_room = Room.objects.get(room_name=data["room_name"])
            sender = User.objects.filter(username=data["sender"]).first()
            if not sender:
                return None  # ✅ Prevents crash if user does not exist
        except Room.DoesNotExist:
            return None

        if not Message.objects.filter(message=data["message"], sender=sender, room=get_room).exists():
            return Message.objects.create(room=get_room, message=data["message"], sender=sender)
        return None


from django.urls import re_path
from safetyapp.consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', ChatConsumer.as_asgi()),
]