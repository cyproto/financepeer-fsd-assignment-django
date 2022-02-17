import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from django.conf import settings
from ..models import User


class CustomJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        authorization_header = request.headers.get('Authorization')
        if not authorization_header:
            return None
        try:
            access_token = authorization_header.split(' ')[1]
            if 'null' == access_token or not access_token:
                raise exceptions.AuthenticationFailed('Auth token invalid')
            payload = jwt.decode(
                access_token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Auth token expired')
        except IndexError:
            raise exceptions.AuthenticationFailed(
                'Auth token\'s prefix missing')

        user = User.objects.filter(id=payload['user_id']).first()
        if user is None:
            raise exceptions.AuthenticationFailed('User not found')
        user.is_authenticated = True
        print(payload)
        request.data.update({'user_id': payload['user_id']})
        return (user, None)
