from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from rest_framework.response import Response
from rest_framework import status

from .utils import generate_token_for_user
from .serializers import MessageSerializer, OperatorRegistrationSerializer
from .models import Room, Message
from rest_framework.views import APIView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.db import models
from django.http import JsonResponse
from django.contrib.auth import authenticate, login

from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi



# Create your views here.


# class HomeView(APIView):
#     @swagger_auto_schema(
#     request_body=openapi.Schema(
#         type=openapi.TYPE_OBJECT,
#         properties= {
#     'username': openapi.Schema(type=openapi.TYPE_STRING, description="Имя пользователя для регистрации"),
#     'chat': openapi.Schema(type=openapi.TYPE_STRING, format='chat', description="Чат"),
# },
#         required=['username',  'chat']
#     ),
#     responses={
#         status.HTTP_201_CREATED: openapi.Response(
#             description="Operator registered successfully!",
#             examples={
#                 'application/json': {'message': 'Operator registered successfully!'}
#             }
#         ),
#         status.HTTP_400_BAD_REQUEST: openapi.Response(
#             description="Invalid data"
#         ),
#     }
# )
#     def post(self, request):
#         username = request.data.get("username")
#         room = request.data.get("room")



#         if username and room:
#             try:
#                 existing_room = Room.objects.get(room_name__icontains=room)
#             except Room.DoesNotExist:
#                 existing_room = Room.objects.create(room_name=room)

#             # Перенаправление на комнату
#             return redirect("room", room_name=room, username=username)
        
#         return render(request, "home.html")

# Представление для комнаты
# class RoomView(APIView):
#     def get(self, request, room_id, user_id):
#         try:
#             existing_room = Room.objects.get(id=room_id)  # Используем id для поиска комнаты
#             get_messages = Message.objects.filter(room=existing_room)
#             serializer = MessageSerializer(get_messages, many=True)  # Сериализация данных
#             context = {
#                 "messages": serializer.data,
#                 "user": user_id,  # Здесь предполагается, что user_id — это идентификатор пользователя
#                 "room_name": existing_room.room_name,
#             }
#             return Response(context, status=status.HTTP_200_OK)
#         except Room.DoesNotExist:
#             return Response({"error": "Room not found."}, status=status.HTTP_404_NOT_FOUND)
        
        
# @swagger_auto_schema(
#     request_body=openapi.Schema(
#         type=openapi.TYPE_OBJECT,
#         properties= {
#     'sender_id': openapi.Schema(type=openapi.TYPE_STRING, description="Айди пользователя "),
#     'receiver_id': openapi.Schema(type=openapi.TYPE_STRING, format='chat', description="айди оператора"),
#     'content': openapi.Schema(type=openapi.TYPE_STRING, format='chat', description="сообщения"),
# },
#         required=['sender_id',  'receiver_id', 'content' ]
#     ),
#     responses={
#         status.HTTP_201_CREATED: openapi.Response(
#             description="Operator registered successfully!",
#             examples={
#                 'application/json': {'message': 'Operator registered successfully!'}
#             }
#         ),
#         status.HTTP_400_BAD_REQUEST: openapi.Response(
#             description="Invalid data"
#         ),
#     }
# )   

@swagger_auto_schema(
    method='post',
    operation_description="Send a message to a room.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'content': openapi.Schema(type=openapi.TYPE_STRING, description="Content of the message."),
        },
        required=['content']
    ),
    responses={
        200: openapi.Response('Message sent successfully.', schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Request success status."),
                'message_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the created message."),
            }
        )),
        400: "Bad Request"
    }
)
@api_view(['POST'])
def send_message(request, room_id):
    """
    Sends a message to a specific room.
    """
    if request.method == "POST":
        content = request.data.get('content')

        if not content:
            return JsonResponse({'error': 'Content is required.'}, status=400)

        # Use the authenticated user's ID as the sender.
        sender = request.user

        # if not sender.is_authenticated:
        #     return JsonResponse({'error': 'Authentication required.'}, status=401)

        # Create and save the message
        message = Message.objects.create(sender=sender, room_id=room_id, content=content)

        return JsonResponse({'success': True, 'message_id': message.id})
    
@swagger_auto_schema(
    method='get',
    operation_description="Get messages from a specific room.",
    responses={
        200: openapi.Response('List of messages', schema=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'content': openapi.Schema(type=openapi.TYPE_STRING, description="Content of the message."),
                    'full_name': openapi.Schema(type=openapi.TYPE_STRING, description="Full name of the sender."),                       
                    'timestamp': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="Timestamp of the message."),
                }
            )
        )),
        404: "Room not found"
    }
)
@api_view(['GET'])
def get_messages(request, room_id):
    """
    Retrieve all messages from a specific room, sorted by timestamp in descending order.
    """
    room = get_object_or_404(Room, id=room_id)
    messages = room.messages.order_by('-timestamp')

    data = [
        {
            'content': msg.content,
            'author': {
                'full_name': msg.sender.get_full_name(),
            },
            'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        }
        for msg in messages
    ]

    return JsonResponse(data, safe=False)

@swagger_auto_schema(
    method='get',
    operation_description="Get active rooms.",
    responses={
        200: openapi.Response(
            description="List of active rooms.",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'room_id': openapi.Schema(type=openapi.TYPE_STRING, description="ID of the room."),
                    }
                )
            )
        ),
        400: "Bad Request"
    }
)
@api_view(['GET'])
def get_rooms(request):
    rooms = Room.objects.all().order_by('-created_at')
    data = [{'room_id': room.id} for room in rooms]
    return Response(data)


@swagger_auto_schema(
    method='get',
    operation_description="Retrieve a list of items.",
    responses={200: openapi.Response('List of items')}
)
@api_view(['GET']) 
def get_operator_messages(request):
    operator_id = 'operator_123'
    messages = Message.objects.filter(receiver_id=operator_id).order_by('-timestamp')
    data = [{'sender': msg.sender_id, 'content': msg.content, 'timestamp': msg.timestamp} for msg in messages]
    return JsonResponse(data, safe=False)

@swagger_auto_schema(
    method='get',
    operation_description="Retrieve a list of items.",
    responses={200: openapi.Response('List of items')}
)
@api_view(['GET']) 
def get_client_messages(request):
    session_id = request.session.get('session_id')
    if not session_id:
        return JsonResponse({'error': 'Session not found'}, status=404)

    messages = Message.objects.filter(models.Q(sender_id=session_id) | models.Q(receiver_id=session_id)).order_by('-timestamp')
    data = [{'sender': msg.sender_id, 'receiver': msg.receiver_id, 'content': msg.content, 'timestamp': msg.timestamp} for msg in messages]
    return JsonResponse(data, safe=False)




@swagger_auto_schema(
    method='post',
    operation_description="Send a message.",
    
    responses={
        200: openapi.Response('Message sent successfully.', schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Request success status."),
                'room_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the created room."),
            }
        )),
        400: "Bad Request"
    }
)
@api_view(['POST'])
def create_room_for_client(request):
    room_id = request.data.get('room_id')
    if not room_id:
        return JsonResponse({'error': 'Room not found'}, status=404)

    # Проверяем, существует ли уже комната
    room, created = Room.objects.get_or_create(room_id=room_id)
    return JsonResponse({
        'room_id': str(room.room_id),
        'created': created  # True, если комната создана заново
    })


class RegisterOperatorView(APIView):
    def post(self, request):
        # Use the serializer to validate and save the data
        serializer = OperatorRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Operator registered successfully!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class LoginView(APIView):
    
    @swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties= {
    'username': openapi.Schema(type=openapi.TYPE_STRING, description="Имя пользователя для регистрации"),
    'password': openapi.Schema(type=openapi.TYPE_STRING, description="Пароль для нового аккаунта"),

},
        required=['username', 'password',]
    ),
responses={
    status.HTTP_201_CREATED: openapi.Response(
        description="Operator registered successfully!",
        examples={
            'application/json': {
                'message': 'Operator registered successfully!',
                'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'  # Пример токена
            }
        }
    ),
    status.HTTP_400_BAD_REQUEST: openapi.Response(
        description="Invalid data"
    ),
}
)   
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
        # Генерация токена
            token = generate_token_for_user(user)  # Ваша функция генерации токена
        
            login(request, user)
            return Response({
            'message': 'Login successful',
            'token': token  # Возвращаем токен
        }, status=200)
        else:
            return Response({'error': 'Invalid credentials'}, status=401)
