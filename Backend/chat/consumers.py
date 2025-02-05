import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Message, Conversation
from .models  import User


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        username = data['username']
        # room = data['room']

        # Save message to database
        await self.save_message(username, self.room_name, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                # 'room': room,
            },
        )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        # room = event['room']

        # Send message to WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    'message': message,
                    'username': username,
                    # 'room': room,
                }
            )
        )

    @sync_to_async
    def save_message(self, username, room, message):
        user = User.objects.get(username=username)
        room = Conversation.objects.get(name=room)
        Message.objects.create(sender=user, conversation=room, content=message)
