from django.conf import settings
import jwt
from datetime import datetime, timedelta

def generate_token_for_user(user):
    """
    Генерация JWT токена для пользователя.
    """
    payload = {
        'user_id': user.id,
        'username': user.username,
        'exp': datetime.utcnow() + timedelta(hours=168),  # Срок действия токена — 24 часа * 7
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')
    return token
