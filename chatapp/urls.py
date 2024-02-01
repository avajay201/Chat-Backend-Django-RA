from django.urls import path
from .views import RoomView, Chat


urlpatterns = [
    path('room-view/', RoomView.as_view(), name='room'),
    path('chat-view/', Chat.as_view(), name='chat'),
    # path('rooms/', RoomList.as_view(), name='room-list'),
    # path('contacts/', ContactsList.as_view(), name='room-list'),
    # path('rooms/<slug:slug>/', RoomDetail.as_view(), name='room-detail'),
    # path('chat-group/', ChatGroup.as_view(), name='chat_group'),
    # path('chat-delete/', ChatDelete.as_view(), name='chat_delete'),
]