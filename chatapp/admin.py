from django.contrib import admin
from .models import Room, Message, Contact, GroupMember

admin.site.register(Room)
admin.site.register(Message)
admin.site.register(Contact)
admin.site.register(GroupMember)