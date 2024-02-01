from rest_framework import serializers
from .models import Message, Contact, GroupMember
from django.db.models import Q

class GroupMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMember
        fields = '__all__'
    
    def to_representation(self, instance):
        # last message of group
        msg = Message.objects.filter(room=instance.room).last()
        last_msg = None
        if msg:
            last_msg = MessageSerializer(msg).data
        else:
            last_msg = {'created_on': instance.room.created_on}

        # all members of group
        user_id = self.context.get('user_id')
        group_members = list(GroupMember.objects.filter(room=instance.room).values_list('id', 'member', 'admin'))
        members = []
        for mebr in group_members:
            mebr = list(mebr)
            saved_member = Contact.objects.filter(mobile_number=mebr[1].replace('+91', ''), saved_by=user_id).first()
            mebr.append(saved_member.name if saved_member else '')
            members.append(mebr)

        return {
            'id': instance.room.id,
            'group_name': instance.room.name,
            'group_members': members,
            'last_msg': last_msg,
            'admin': instance.admin
        }

    def create(self, validated_data, context):
        room = context.get('room')
        group_admin = context.get('group_admin')
        group_members = []
        for data in validated_data:
            group_member = GroupMember.objects.create(room = room, member = data['member'], admin = group_admin == data['member'])
            group_members.append(group_member)
        return group_members


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'


class ContactSerializer(serializers.ModelSerializer):
    last_msg = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = ('id', 'name', 'saved_by', 'mobile_number', 'profile', 'last_msg')
    
    def get_last_msg(self, instance):
        self_number = self.context.get('mobile_number')
        room_name = f'{self_number}_chat_{instance.mobile_number}'
        reverse_room_name = f'{instance.mobile_number}_chat_{self_number}'
        last_msg = Message.objects.filter(Q(room__name=room_name) | Q(room__name=reverse_room_name)).last()
        return MessageSerializer(last_msg).data if last_msg else None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user_id'] = instance.user_id
        return data


class UnsaveContactSerializer(serializers.ModelSerializer):
    last_msg = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = ('id', 'name', 'saved_by', 'mobile_number', 'saved_by_mobile_number', 'profile', 'user_id', 'last_msg')

    def get_last_msg(self, instance):
        self_number = self.context.get('mobile_number')
        room_name = f'{self_number}_chat_{instance.saved_by_mobile_number}'
        reverse_room_name = f'{instance.saved_by_mobile_number}_chat_{self_number}'
        last_msg = Message.objects.filter(Q(room__name=room_name) | Q(room__name=reverse_room_name)).last()
        return MessageSerializer(last_msg).data if last_msg else None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user_id'] = instance.saved_by
        data['name'] = instance.saved_by_mobile_number
        data['mobile_number'] = instance.saved_by_mobile_number
        data['saved_by'] = instance.user_id
        return data
    
    # def get_mobile_number(self, instance):
    #     self_number = self.context.get('mobile_number')
    #     room_name = f'{self_number}_chat_{instance.}'

# class RoomSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Room
#         fields = '__all__'


# class MessageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Message
#         fields = '__all__'


# class ContactSerializer(serializers.ModelSerializer):
#     last_msg = serializers.SerializerMethodField()
#     mobile_number = serializers.SerializerMethodField()

#     class Meta:
#         model = Contact
#         fields = ('id', 'name', 'mobile_number', 'user_id', 'last_msg')

#     def get_last_msg(self, instance):
#         last_msg = Message.objects.filter(room__name__contains=instance.mobile_number).last()
#         return MessageSerializer(last_msg).data if last_msg else None

#     def get_mobile_number(self, instance):
#         m_num = self.context.get('m_num')
#         if m_num == instance.mobile_number:
#             room = Room.objects.filter(name__contains=instance.mobile_number).first()
#             num = room.name.split('_chat_')
#             num = num[1] if num[0] == instance.mobile_number else num[0]
#         else:
#             num = instance.mobile_number
#         return num


# class GroupMemberSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = GroupMember
#         fields = '__all__'

#     def to_representation(self, instance):
#         msg = Message.objects.filter(room=instance.room).last()
#         last_msg = None
#         if msg:
#             last_msg = MessageSerializer(msg).data
#         mobile_number = self.context.get('mobile_number')
#         user_id = self.context.get('user_id')
#         member = GroupMember.objects.filter(member=mobile_number, room=instance.room).first()
#         group_members = list(GroupMember.objects.filter(room=instance.room).values_list('id', 'member', 'admin'))
#         members = []
#         for mebr in group_members:
#             mebr = list(mebr)
#             saved_member = Contact.objects.filter(mobile_number=mebr[1].replace('+91', ''), user_id=user_id).first()
#             mebr.append(saved_member.name if saved_member else '')
#             members.append(mebr)

#         return {
#             'id': instance.room.id,
#             'group_name': instance.room.name,
#             'mobile_number': mobile_number,
#             'group_members': members,
#             'last_msg': last_msg,
#             'admin': member.admin if member else False
#         }