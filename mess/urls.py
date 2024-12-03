from django.urls import path
# from .views import HomeView, RoomView
from . import views
from .views import create_room_for_client


urlpatterns = [
    # path("login/", HomeView.as_view(), name="login"),
    # path("<int:room_id>/<int:user_id>/", RoomView.as_view(), name="room"),
    path('create_room/', views.create_room_for_client, name='create_room'),
    path('send_message/', views.send_message, name='send_message'),
    path('get_messages/<str:room_id>/', views.get_messages, name='get_messages'),

    
]
