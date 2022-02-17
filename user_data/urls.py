from django.urls import include, re_path
from .views import ChangePassword, Login, Signup
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'signup', Signup, 'signup')
router.register(r'change-password', ChangePassword, 'change-password')
router.register(r'login', Login, 'login')

urlpatterns = [
    re_path('^', include(router.urls)),
]
