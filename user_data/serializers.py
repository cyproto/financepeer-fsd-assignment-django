from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Data, User, UserData


class UserSerializer(serializers.Serializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField()

    def create(self, validated_data):
        instance = User(**validated_data)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        instance.password = validated_data.get('password', instance.password)
        instance.save()
        return instance


class UserDataSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    name = serializers.CharField()
    created_by = serializers.IntegerField()
    updated_by = serializers.IntegerField()

    def create(self, validated_data):
        instance = UserData(**validated_data)
        instance.save()
        return instance
