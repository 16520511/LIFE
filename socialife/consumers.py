from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
import json
from .models import MyUser, Message, ChatRoom
from rest_framework_simplejwt.tokens import AccessToken
import requests_async as requests
from asgiref.sync import async_to_sync, sync_to_async
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async
from .serializers import MessageSerializer
from django.utils import timezone

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_uuid']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join websocket
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        print(self.channel_name)
        await self.accept()

        # Send message to room group
    async def chat_message(self, event):
        message = event['message']
        uuid = event['uuid']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'uuid': uuid,
        }))

    # Fetch message for room group
    async def fetch_messages(self, event):
        messages = event['messages']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'fetch_messages',
            'message': messages
        }))

    async def error(self, event):
        await self.send(text_data=json.dumps({
            'type': 'error',
        }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    @database_sync_to_async
    def get_chat_room(self, room_uuid):
        return ChatRoom.objects.filter(uuid=room_uuid)

    @database_sync_to_async
    def get_user(self, user_profile_name):
        return MyUser.objects.filter(profile_name=user_profile_name)

    @database_sync_to_async
    def get_messages(self, room, user):
        messages = Message.objects.filter(chat_room = room)
        for message in messages:
            message.read_by_users.add(user)
            message.save()
        room.notice_by_users.add(user)
        room.save()
        return messages
        

    @database_sync_to_async
    def save_message(self, user, content, room):
        message = Message.objects.create(user = user, chat_room = room, content = content)
        message.read_by_users.add(user)
        room.notice_by_users.clear()
        room.notice_by_users.add(user)
        room.last_interaction = timezone.now()
        room.save()
        message.save()
        return message

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)

        email = data['email']
        message = data['message']
        token = data['token']


        url = "http://127.0.0.1:8000/api/check_logged_in"

        payload = {"email": email, 'for_channels': 'channels'}

        header = {"Content-type": "application/json",
                'Authorization': "Bearer " + token}


        response = await requests.post(url, data=json.dumps(payload), headers=header)
        # data = json.loads(response.decode('utf-8'))
        response_json = response.json()

        if response_json['message'] == 'Authorized':
            room = await self.get_chat_room(self.room_name)
            user = await self.get_user(response_json['user']['profile_name'])
            if len(room) > 0 and len(user) > 0:
                if user[0] in room[0].users.all():
                    if data['type'] == 'chat_message':
                        # Save message to db
                        saved_message = await self.save_message(user[0], data['message'], room[0])
                        # Send message to room group
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                'type': 'chat_message',
                                'message': MessageSerializer(saved_message).data,
                                'uuid': str(room[0].uuid)
                            }
                        )
                    elif data['type'] == 'fetch_messages':
                        messages = await self.get_messages(room[0], user[0])

                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                'type': 'fetch_messages',
                                'messages': MessageSerializer(messages, many=True).data
                            }
                        )
            else:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'error',
                        'messages': 'Error'
                    }
                )