from contextlib import closing
from datetime import datetime, timedelta
import json
import re
from django.db import connection

from django.http import JsonResponse
from django.core import serializers
from user_data.models import Data, User, UserData
from user_data.serializers import GetDataSerializer, UserDataSerializer, UserSerializer
from rest_framework.viewsets import GenericViewSet
from django.contrib.auth.hashers import make_password, check_password
import jwt
import ast


class SignupView(GenericViewSet):
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


class ChangePasswordView(GenericViewSet):
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


class LoginView(GenericViewSet):
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


class UserDataView(GenericViewSet):
    http_method_names = ['post', 'get']
    serializer_class = GetDataSerializer

    def create(self, request):
        file = request.FILES['file']

        validation_response = self.validate_file(file)
        if not validation_response['is_valid']:
            return JsonResponse({'error': validation_response['message']}, status=400)

        user_data = {'user_id': 13, 'name': str(
            file) + str(datetime.now()), 'created_by': 1, 'updated_by': 1}
        user_data_serializer = UserDataSerializer(data=user_data)

        try:
            if user_data_serializer.is_valid():
                user_data_obj = user_data_serializer.create(user_data)
            self.insert_data(
                validation_response['file_contents'], user_data_obj.id)
        except Exception as error:
            return JsonResponse({'error': f'Failed to create records {str(error)}'}, status=500)

        return JsonResponse({'message': 'Inserted successfully'}, status=200)

    def get(self, request):
        user_data_id = request.GET.get('id')
        if user_data_id:
            data_objects = Data.objects.filter(user_data_id=user_data_id).order_by('id').values(
                'data_user_id', 'data_id', 'data_title', 'data_body')
            return JsonResponse({
                'data': list(data_objects)
            }, status=200)

        user_data_objects = UserData.objects.filter(
            user_id=13).order_by('id').values('id', 'name', 'created_at')
        return JsonResponse({
            'data': list(user_data_objects)
        }, status=200)

    def insert_data(self, contents, user_data_id):
        params = []
        for content in contents:
            params.append((user_data_id, int(content['userId']), int(content['id']), str(content['title']).replace("'", ""),
                           str(content['body']).replace("'", ""), 'NOW()', 13, 'NOW()', 13))

        values = ', '.join(map(str, params))
        sql = 'INSERT INTO data (user_data_id, data_user_id, data_id, data_title, data_body, created_at, created_by, updated_at, updated_by) VALUES {}'.format(
            values)

        with closing(connection.cursor()) as cursor:
            cursor.execute(sql, params)

    def validate_file(self, file):
        if not file:
            return {'is_valid': False, 'message': 'File is required'}

        if 'application/json' != str(file.content_type):
            return {'is_valid': False, 'message': f'{file.content_type} type not supported'}

        try:
            file_contents = json.loads(file.read().decode('UTF-8'))
            if not isinstance(file_contents, list):
                raise Exception('File contents should be array of objects')
        except Exception as error:
            return {'is_valid': False, 'message': str(error)}

        for content in file_contents:
            if not set(list(content.keys())).issubset(
                    ['userId', 'id', 'title', 'body']):
                return {'is_valid': False, 'message': 'Invalid data in file'}

        return {'is_valid': True, 'file_contents': file_contents}
