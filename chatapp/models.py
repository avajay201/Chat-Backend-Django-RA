from django.db import models

class Room(models.Model):
    class RoomType(models.TextChoices):
        CHAT = 'Chat', 'Chat'
        GROUP_CHAT = 'Group Chat', 'Group Chat'
    name = models.CharField(max_length=150)
    type = models.CharField(max_length=20, choices=RoomType.choices)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Room : "+ self.name


class Message(models.Model):
    sender = models.CharField(max_length=30)
    receiver = models.CharField(max_length=30)
    message = models.TextField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    read_message = models.BooleanField(default=False)

    def __str__(self):
        return "Message is :- "+ self.message


class Contact(models.Model):
    name = models.CharField(max_length=150)
    mobile_number = models.CharField(max_length=13)
    saved_by = models.CharField(max_length=30)
    saved_by_mobile_number = models.CharField(max_length=13)
    user_id = models.CharField(max_length=30)
    profile = models.ImageField(upload_to='profile_pics', null=True, blank=True)

    def __str__(self):
        return self.name + ' -> ' + self.mobile_number


class GroupMember(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    member = models.CharField(max_length=13)
    admin = models.BooleanField(default=False)

    def __str__(self):
        return self.member