from django.urls import include, re_path
from .views import ChangePasswordView, LoginView, SignupView, UserDataView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'signup', SignupView, 'signup')
router.register(r'change-password', ChangePasswordView, 'change-password')
router.register(r'login', LoginView, 'login')
router.register(r'user-data', UserDataView, 'user-data')

urlpatterns = [
    re_path('^', include(router.urls)),
]
