from django.db import models
import uuid
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AbstractUser, Group, Permission



class Room(models.Model):
    room_id = models.IntegerField()  # Или CharField, если нужнo
    room_name = models.CharField(max_length=50)

    def __str__(self):
        return self.room_name


class Message(models.Model):
    sender_id = models.CharField(max_length=100)  # ID отправителя (может быть оператор или клиент)
    receiver_id = models.CharField(max_length=100)  # ID получателя
    content = models.TextField()  # Содержание сообщения
    timestamp = models.DateTimeField(auto_now_add=True)  # Время отправки
    is_read = models.BooleanField(default=False)  # Прочитано или нет

    def __str__(self):
        return f"Message from {self.sender_id} to {self.receiver_id}"
    
    
class ClientSession(models.Model):
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)  # Когда сессия создана
    is_active = models.BooleanField(default=True)  # Активная сессия


class ClientSessionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if 'session_id' not in request.COOKIES:
            session_id = str(uuid.uuid4())
            request.set_cookies['session_id'] = session_id
        else:
            session_id = request.COOKIES['session_id']
        request.session_id = session_id
        
        
class ClientRoomMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if 'session_id' not in request.session:
            # Создаем уникальный session_id
            session_id = str(uuid.uuid4())
            request.session['session_id'] = session_id
            
            # Создаем комнату для нового клиента
            Room.objects.create(client_session_id=session_id)
        else:
            session_id = request.session['session_id']
        
        # Добавляем session_id в request для использования
        request.session_id = session_id
        
        
class Operator(AbstractUser):
    # Устанавливаем уникальные related_name для конфликтующих полей
    groups = models.ManyToManyField(
        Group,
        related_name="operator_groups",  # Уникальное имя
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="operator_permissions",  # Уникальное имя
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )
    phone_number = models.CharField(
        max_length=15, 
        blank=True, 
        null=True, 
        verbose_name="Номер телефона"
    )