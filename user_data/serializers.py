from rest_framework import serializers
from rest_framework.validators import UniqueValidator
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User

class UserSerializer(serializers.Serializer):
    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField()
    
    def create(self, validated_data):
        instance = User(**validated_data)
        instance.save()
        return instance
    
    def update(self, instance, validated_data):
        instance.password = validated_data.get('password', instance.password)
        instance.save()
        return instance