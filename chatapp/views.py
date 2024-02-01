from .models import Room, Message
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Room, Contact, Message, GroupMember
from .serializers import GroupMemberSerializer, MessageSerializer, ContactSerializer, UnsaveContactSerializer
from django.db.models import Q


class RoomView(APIView):
    def post(self, request):
        '''room create'''
        room_name = request.data.get('room_name')
        group_members = request.data.get('members')
        group_admin = request.data.get('group_admin')

        # check room name exists or not
        if not room_name:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # simple chat
        if '_chat_' in room_name:
            type = 'Chat'
            reverse_room_name = room_name.split('_chat_')[1] + '_chat_' + room_name.split('_chat_')[0]
            room = Room.objects.filter(Q(name = room_name) | Q(name = reverse_room_name)).first()
            if room:
                # check room already exists or not
                return Response(status = status.HTTP_200_OK)
            Room.objects.create(name = room_name, type = type)
            return Response(status = status.HTTP_201_CREATED)

        # group chat
        # check group members exists or not
        if not group_members or not group_admin:
            return Response(status = status.HTTP_400_BAD_REQUEST)

        type = 'Group Chat'
        room, created = Room.objects.get_or_create(name = room_name, type = type)
        if not created:
            # if group already exists using this name
            return Response({'error': 'Please use diffrent name'}, status = status.HTTP_400_BAD_REQUEST)

        try:
            context = {'room': room, 'group_admin': group_admin}
            group_member_serializer = GroupMemberSerializer()
            group_member_serializer.create(group_members, context)
            return Response(status = status.HTTP_200_OK)
        except:
            return Response(status = status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        '''get room messages'''
        room_name = request.GET.get('room_name').replace('ooo', ' ')
        reverse_room_name = ''

        # check room name exsits or not
        if not room_name:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        if '_chat_' in room_name:
            reverse_room_name = room_name.split('_chat_')[1] + '_chat_' + room_name.split('_chat_')[0]

        messages = Message.objects.filter(Q(room__name = room_name) | Q(room__name = reverse_room_name))
        message_data = MessageSerializer(messages, many = True).data
        return Response({'message_data': message_data}, status = status.HTTP_200_OK)


class Chat(APIView):
    def get(self, request):
        '''get chat list'''
        user_id = request.GET.get('id')
        mobile_number = request.GET.get('mobile_number')

        # check user_id exists or not
        if not user_id:
            return Response(status = status.HTTP_400_BAD_REQUEST)
        
        contacts = Contact.objects.filter(saved_by = user_id)
        contacts_list = list(Contact.objects.filter(saved_by = user_id).values_list('mobile_number', flat=True))
        contact_serializer = ContactSerializer(contacts, many = True, context={'mobile_number': mobile_number})

        # unsave numbers
        opposite_contacts = list(Contact.objects.filter(mobile_number = mobile_number).values_list('saved_by_mobile_number', flat=True))
        unsave_contacts = []
        for contact in opposite_contacts:
            if contact not in contacts_list:
                u_contact = Contact.objects.filter(saved_by_mobile_number = contact).first()
                unsave_contacts.append(u_contact)
        unsave_contact_serializer = UnsaveContactSerializer(unsave_contacts, many=True, context={'mobile_number': mobile_number})

        chat_list = contact_serializer.data + unsave_contact_serializer.data
        group_members = GroupMember.objects.filter(member=mobile_number)
        group_list = GroupMemberSerializer(group_members, many=True, context={'mobile_number': mobile_number, 'user_id': user_id})
        if group_list:
            chat_list = chat_list + group_list.data
        return Response({'chat_list': chat_list}, status = status.HTTP_200_OK)

    def delete(self, request):
        '''delete chat'''
        chat_id = request.data.get('chat_id')
        mobile_number = request.data.get('mobile_number')
        chat_type = request.data.get('type')
        user_id = request.data.get('user_id')

        if not chat_id or not mobile_number or not chat_type:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # delete chat group
        if chat_type == 'group':
            member = GroupMember.objects.filter(member=mobile_number).first()
            group = Room.objects.filter(id=chat_id).first()
            room_members = len(GroupMember.objects.filter(room=group))

            # delete group
            if member and member.admin:
                group.delete()
                return Response(status=status.HTTP_200_OK)

            # delete group if only you in group
            if room_members < 3:
                group.delete()
                return Response(status=status.HTTP_200_OK)

            # leave group
            member.delete()
            return Response(status=status.HTTP_200_OK)

        # delete chat
        contact = Contact.objects.filter(id=chat_id).first()
        opposite_saved_contact = Contact.objects.filter(user_id=user_id, mobile_number=mobile_number).first()
        room = Room.objects.filter(Q(name__contains=mobile_number) & Q(name__contains=contact.mobile_number)).first()
        if not contact:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if room:
            room.delete()
        contact.delete()
        if opposite_saved_contact:
            opposite_saved_contact.delete()
        return Response(status=status.HTTP_200_OK)

    def post(self, request):
        '''add members in group'''
        group_members = request.data.get('members')
        group_id = request.data.get('group_id')

        if not group_id or not group_members:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        room = Room.objects.filter(id=group_id).first()
        if not room:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        for member in group_members:
            group_member = GroupMember.objects.create(room=room, member=member)
            group_member.save()
        return Response(status=status.HTTP_200_OK)
