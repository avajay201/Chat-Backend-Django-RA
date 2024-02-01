import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.db.models import Q
from chatapp.models import Room, Message, Contact

class ChatConsumer(AsyncWebsocketConsumer):
    connected_users = set()

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_slug']
        self.reverse_room_name = self.room_name
        if '_chat_' in self.room_name:
            self.reverse_room_name = f"{self.room_name.split('_chat_')[1]}_chat_{self.room_name.split('_chat_')[0]}"
        else:
            self.room_name = self.room_name.replace('ooo', ' ')
            self.reverse_room_name = self.room_name
        self.roomGroupName = await self.getRoomName()

        await self.channel_layer.group_add(
            self.roomGroupName,
            self.channel_name
        )
        await self.accept()
        if self.channel_name not in self.connected_users:
            self.connected_users.add(self.channel_name)
        self.room_members = len(self.connected_users)
        await self.channel_layer.group_send(
            self.roomGroupName, {
                "type": "sendMessage",
                "status": "Online",
                "online_members": self.room_members,
            }
        )


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.roomGroupName,
            self.channel_name
        )
        self.connected_users.discard(self.channel_name)
        self.room_members = len(self.connected_users)
        await self.channel_layer.group_send(
            self.roomGroupName, {
                "type": "sendMessage",
                "status": False,
                "online_members": self.room_members,
            }
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if text_data_json.get('sender'):
            chat_type = text_data_json["type"]
            message = text_data_json['message']
            contact_name = text_data_json["contact_name"]
            sender = text_data_json["sender"]
            mobile_number = text_data_json["mobile_number"]
            sender_number = text_data_json["sender_number"]
            receiver = text_data_json["receiver"]
            await self.save_message(message, sender, receiver, chat_type)
            if '_chat_' in self.room_name:
                await self.saveContacts(sender, contact_name, mobile_number, receiver, sender_number)
            message = text_data_json
            await self.channel_layer.group_send(
                self.roomGroupName, {
                    "type": "sendMessage",
                    "message": message,
                    "username": sender,
                    "room_name": self.roomGroupName.replace('ooo', ' '),
                }
            )
        elif text_data_json.get('typing_status'):
            message = text_data_json
            await self.channel_layer.group_send(
                self.roomGroupName, {
                    "type": "sendMessage",
                    "message": message,
                }
            )


    async def sendMessage(self, event):
        message = event.get("message")
        if event.get("status"):
            await self.send(text_data=json.dumps({"status": event.get("status"), "online_members": event.get("online_members")}))
        else:
            await self.send(text_data=json.dumps(message))

    @sync_to_async
    def save_message(self, message, sender, receiver, chat_type):
        try:
            room = Room.objects.get(name=self.roomGroupName.replace('ooo', ' '))
            if chat_type == 'chat':
                Message.objects.create(sender=sender,room=room,message=message,receiver=receiver)
            else:
                Message.objects.create(sender=sender,room=room,message=message,receiver='group')
        except Exception as err:
            '''print('Error while saving message -', err)'''


    async def get_group_members_count(self):
        group_members = await self.channel_layer.group_channels(self.roomGroupName)
        members_count = len(group_members)
        return members_count


    @sync_to_async
    def getRoomName(self):
        room = Room.objects.filter(Q(name=self.room_name) | Q(name=self.reverse_room_name)).first()
        return room.name.replace(' ', 'ooo') if room else None


    @sync_to_async
    def saveContacts(self, sender, contact_name, mobile_number, receiver, sender_number):
        contact = Contact.objects.filter(Q(saved_by=sender) & Q(mobile_number=mobile_number)).first()
        if not contact and contact_name != mobile_number:
            Contact.objects.create(saved_by=sender, mobile_number=mobile_number, name=contact_name, user_id=receiver, saved_by_mobile_number=sender_number)


