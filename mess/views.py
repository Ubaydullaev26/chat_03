import random
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets 
from .serializers import MessageModelSerializer


from .utils import generate_token_for_user
from .serializers import MessageSerializer, OperatorRegistrationSerializer
from .models import Room, Message, Operator
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
import logging
logger = logging.getLogger(__name__)




# class MessagesViewSet(viewsets.ViewSet):
#     model = Message
#     queryset = Message.objects.all()
#     http_method_names = ['get']
#     serializer_class = MessageModelSerializer


class AllMessagesAPIView(APIView):
    model = Message
    queryset = Message.objects.all()
    serializer_class = MessageModelSerializer
    @swagger_auto_schema(
        operation_summary="Retrieve all messages for a specific room",
        operation_description=(
            "Retrieve all messages for a specific room identified by the room ID. "
            "The authenticated user can view messages if they have access to the room."
        ),
        manual_parameters=[
            openapi.Parameter(
                "room_id",
                openapi.IN_QUERY,
                description="The ID of the room to retrieve messages for.",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successful response with a list of messages.",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description="The ID of the message.",
                            ),
                            "content": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description="The content of the message.",
                            ),
                            "room_id": openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description="The ID of the room the message belongs to.",
                            ),
                            "created_at": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                format=openapi.FORMAT_DATETIME,
                                description="The timestamp when the message was created.",
                            ),
                        },
                    ),
                ),
            ),
            400: openapi.Response(
                description="Bad request due to missing or invalid room_id.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Error message.",
                        ),
                    },
                ),
            ),
            404: openapi.Response(
                description="Room not found.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Error message.",
                        ),
                    },
                ),
            ),
        },
    )

    def get(self, request, *args, **kwargs):
        get_room_id = request.GET.get('room_id')
        if not get_room_id:
            return Response({'error': 'Room id is not specified'})
        
        # if 
        #     return 
        
        room = Room.objects.get(id=get_room_id)
        room_messages = Message.objects.filter(room_id=room)
        msgs = MessageSerializer(room_messages, many=True).data
        # messages = room
        # msgs = MessageModelSerializer(messages, many=True)
        
        return Response(msgs, status=200)
    

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
        message_type = request.data.get('message_type')
        
        # if message_type != 'sender' or message_type != 'receiver':
        #     return Response({"error": "Message Type is invalid either has to be sender or receiver"})
            

        # Проверка наличия content
        if not content:
            return Response({"error": "Content is required."}, status=400)

        # Проверка существования комнаты
        room = get_object_or_404(Room, id=room_id)

        try:
            # Create and save the message
            message = Message.objects.create(
                receiver_id="system",  # Или указать реального получателя
                room=room,
                content=content, 
                message_type=message_type
            )
            return Response({
                "success": True,
                "message_id": message.id
            }, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)    
    
@swagger_auto_schema(
    method='get',
    operation_description="Get messages from a specific room.",
    manual_parameters=[
        openapi.Parameter(
            'room_id',
            openapi.IN_PATH,
            description="ID of the room",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
        openapi.Parameter(
            'sender_id',
            openapi.IN_QUERY,
            description="ID of the sender (optional)",
            type=openapi.TYPE_INTEGER,
            required=False
        ),
        openapi.Parameter(
            'receiver_id',
            openapi.IN_QUERY,
            description="ID of the receiver (optional)",
            type=openapi.TYPE_INTEGER,
            required=False
        ),
    ],
    responses={
        200: openapi.Response('List of messages', schema=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message_type': openapi.Schema(type=openapi.TYPE_STRING, description="Type of message."),
                    'content': openapi.Schema(type=openapi.TYPE_STRING, description="Content of the message."),
                    'author': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'full_name': openapi.Schema(type=openapi.TYPE_STRING, description="Full name of the sender."),
                        }
                    ),
                    'timestamp': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="Timestamp of the message."),
                }
            )
        )),
        404: "Room not found"
    }
)


 
    


@api_view(['GET'])
def get_messages(request, room_id):
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    """
    Retrieve all messages from a specific room, sorted by timestamp in descending order.
    """
    # print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$', room.messages)
    # Fetch the room object or return 404 if not found
    room = get_object_or_404(Room, id=room_id)
    print('****************************************', room)
    message = Message.objects.filter(room_id=room_id )
    print('HERE IS THE MESSAGE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!', message)

    # Retrieve the messages, sorted by timestamp in descending order
    messages = room.messages.all().order_by('-timestamp').values('id', 'message_type', 'sender_id', 'receiver_id', 'content', 'timestamp', 'is_read')

    data = []
    for msg in messages:
        sender_name = "Unknown Sender"
        # message_type=[x for x in room.messages.all()]
        if msg['sender_id']:
            try:
                sender = Operator.objects.get(id=msg['sender_id'])
                sender_name = f"{sender.first_name} {sender.last_name}"
            except Operator.DoesNotExist:
                pass  # Уже задано значение по умолчанию

        data.append({
        'content': msg['content'] or 'No content available',
        'author': {'full_name': sender_name},
        'message_type': {'message_type': message},
        'timestamp': msg['timestamp'].strftime('%Y-%m-%d %H:%M:%S') if msg['timestamp'] else 'Unknown time',
    })

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
                        'pk': openapi.Schema(type=openapi.TYPE_INTEGER, description="Primary key of the room."),
                       
                    }
                )
            )
        ),
        400: "Bad Request"
    }
)
@api_view(['GET'])
def get_rooms(request):
    try:
        # Fetch all rooms
        rooms = Room.objects.all()
        data = [
            {
                'pk': room.pk,  # Adding primary key to the response
                'room_id': str(room.room_id),  # Assuming room_id is stored as a string or UUID
                'room_name': room.room_name  # Example: Adding room name for additional details
            } 
            for room in rooms
        ]
        return Response(data)
    except Exception as e:
        logger.error(f"Error fetching rooms: {e}")  # Logging the error
        return Response({'error': 'Internal Server Error', 'details': str(e)}, status=500)  # Returning error details

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
    manual_parameters=[
        openapi.Parameter('room_id', openapi.IN_QUERY, description="ID of the room", type=openapi.TYPE_INTEGER, required=True)
    ],
    operation_description="Get or create a room.",
    responses={
        200: openapi.Response('Room retrieved or created successfully.', schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'room_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the room."),
                'created': openapi.Schema(type=openapi.TYPE_BOOLEAN, description="True if the room was created."),
                'pk': openapi.Schema(type=openapi.TYPE_INTEGER, description="Primary key of the room."),

            }
        )),
        400: "Bad Request"
    }
)
@api_view(['POST'])
def create_room_for_client(request):
    try:
        # Генерируем уникальный room_id
        while True:
            room_id = random.randint(100000, 999999)  # Шестизначное случайное число
            if not Room.objects.filter(room_id=room_id).exists():
                break

        # Создаем новую комнату с сгенерированным room_id
        room = Room.objects.create(room_id=room_id)

        return JsonResponse({
            'room_id': room.room_id,
            'pk': room.pk,  # Adding primary key to the response

            'created': True  # Комната всегда создается заново
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

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
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description="Имя пользователя для регистрации"),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description="Пароль для нового аккаунта"),
            },
            required=['username', 'password']
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Успешный вход",
                examples={
                    'application/json': {
                        'message': 'Login successful',
                        'access': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
                        'refresh': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
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
            # Генерация токенов
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            login(request, user)  # Авторизуем пользователя
            return Response({
                'message': 'Login successful',
                'access': access_token,
                'refresh': refresh_token
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)