from datetime import datetime, timedelta
import json

from django.http import JsonResponse
from user_data.models import User
from user_data.serializers import UserSerializer
from rest_framework.viewsets import GenericViewSet
from django.contrib.auth.hashers import make_password, check_password
import jwt


class Signup(GenericViewSet):
    http_method_names = ['post']
    serializer_class = UserSerializer

    def create(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        if not 'email' in body or not 'password' in body:
            return JsonResponse({'error': 'Email/Password missing'}, status=400)

        body['password'] = make_password(body['password'])
        user_serializer = UserSerializer(data=body)
        if user_serializer.is_valid():
            user_serializer.create(body)
            return JsonResponse({'message': 'Signed up successfully'}, status=201)
        return JsonResponse({'error': user_serializer.errors}, status=400)


class ChangePassword(GenericViewSet):
    http_method_names = ['put']
    serializer_class = UserSerializer

    def update(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        if not 'password' in body:
            return JsonResponse({'error': 'Password missing'}, status=400)

        user = User.objects.get(id=kwargs['pk'])
        if not user:
            return JsonResponse({'error': 'User not found'}, status=400)
        body['password'] = make_password(body['password'])
        user_serializer = UserSerializer(data=body, partial=True)
        if user_serializer.is_valid():
            user_serializer.update(user, body)
            return JsonResponse({'message': 'Password changed successfully'}, status=201)
        return JsonResponse({'error': user_serializer.errors}, status=400)


class Login(GenericViewSet):
    http_method_names = ['post']

    def create(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        if not 'email' in body or not 'password' in body:
            return JsonResponse({'error': 'Email/Password missing'}, status=400)

        user = User.objects.filter(email=body['email'])
        if not user:
            return JsonResponse({'error': 'User not found'}, status=400)

        password_validation = check_password(
            body['password'], user.values('password')[0]['password'])
        if password_validation:
            exp_date = datetime.utcnow() + timedelta(hours=24)
            token = jwt.encode({'email': body['email'], 'user_id': user.values('id')[
                0]['id'], 'exp': exp_date}, 'MySecretKey', algorithm='HS256')
            return JsonResponse({'token': token.decode('UTF-8')})
        return JsonResponse({'error': 'Password is incorrect'})
