from django.urls import path
# from .views import HomeView, RoomView
from . import views
from .views import LoginView, get_rooms, send_message, get_messages



urlpatterns = [
    # path("login/", HomeView.as_view(), name="login"),
    # path("<int:room_id>/<int:user_id>/", RoomView.as_view(), name="room"),
    path('new_room/', views.create_room_for_client, name='create_room'),
    path('send/<int:room_id>/', send_message, name='send_message'),
    #path('send_message/room_id', views.send_message, name='send_message'),
    path('get_room/', views.get_rooms, name='active_room'),
    path('get-messages/<int:room_id>/', get_messages, name='get_messages'),
    path('login/', LoginView.as_view(), name='login'),
]
