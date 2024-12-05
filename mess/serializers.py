from rest_framework import serializers
from .models import Message, Operator

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'  # Или укажите конкретные поля, которые хотите включить
        
        
class OperatorRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operator
        fields = ['username', 'password', 'email', 'phone_number']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        operator = Operator.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            phone_number=validated_data.get('phone_number'),
            password=validated_data['password']
        )
        operator.is_operator = True
        operator.save()
        return operator