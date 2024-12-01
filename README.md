Для реализации реферальной системы с запросами API на Django с использованием Django Rest Framework (DRF) и PostgreSQL, мы можем следовать ниже представленной пошаговой инструкции. Я также опишу, как создать документацию API и Postman коллекцию.

Шаг 1: Настройка проекта
Создание нового Django проекта bash django-admin startproject referral_system cd referral_system
Создание нового приложения, например, users bash python manage.py startapp users
Установка необходимых зависимостей bash pip install djangorestframework psycopg2
Настройка базы данных в settings.py python DATABASES = { 'default': { 'ENGINE': 'django.db.backends.postgresql', 'NAME': 'имя_вашей_базы_данных', 'USER': 'ваш_пользователь', 'PASSWORD': 'ваш_пароль', 'HOST': 'localhost', 'PORT': '', } }
Добавьте rest_framework и ваше приложение в INSTALLED_APPS python INSTALLED_APPS = [ ... 'rest_framework', 'users', ]
Шаг 2: Реализация модели пользователя
В users/models.py создайте модель User:

from django.db import models
import random
import string

class User(models.Model):
    phone_number = models.CharField(max_length=20, unique=True)
    auth_code = models.CharField(max_length=4, blank=True, null=True)
    invite_code = models.CharField(max_length=6, default='', blank=True)
    activated_invite_code = models.CharField(max_length=6, blank=True, default=None)
    
    def generate_invite_code(self):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

    def __str__(self):
        return self.phone_number
Шаг 3: Реализация сервисов для работы с пользователями
Создайте файл users/services.py:

from .models import User
import asyncio

class UserService:
    @staticmethod
    async def authenticate(phone_number):
        user, _ = User.objects.get_or_create(phone_number=phone_number)
        await asyncio.sleep(1)  # Имитация задержки в 1 сек
        if user.invite_code == '':
            user.invite_code = user.generate_invite_code()
            user.save()
        return user

    @staticmethod
    async def verify_auth_code(user, code):
        if user.auth_code == code:
            return user
        raise ValueError("Invalid auth code")

    @staticmethod
    async def activate_invite_code(user, code):
        if User.objects.filter(invite_code=code).exists():
            user.activated_invite_code = code
            user.save()
            return user
        raise ValueError("Invalid invite code")

    @staticmethod
    def get_user_profile(user):
        return {
            "phone": user.phone_number,
            "invite_code": user.invite_code,
            "activated_invite_code": user.activated_invite_code,
            "used_by": User.objects.filter(activated_invite_code=user.invite_code).values_list('phone_number', flat=True)
        }
Шаг 4: Создание API views
В users/views.py создайте API views для авторизации и получения профиля:

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import UserService
from .models import User

class AuthView(APIView):
    async def post(self, request):
        phone_number = request.data.get('phone')
        if not phone_number:
            return Response({"error": "Phone number is required"}, status=status.HTTP_400_BAD_REQUEST)

        user = await UserService.authenticate(phone_number)
        return Response({"message": "Authentication successful", "user_id": user.id, "invite_code": user.invite_code})

class VerifyCodeView(APIView):
    async def post(self, request):
        phone_number = request.data.get('phone')
        code = request.data.get('auth_code')
        
        try:
            user = await User.objects.get(phone_number=phone_number)
            await UserService.verify_auth_code(user, code)
            return Response({"message": "Code verified successfully"})
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class ProfileView(APIView):
    async def get(self, request):
        phone_number = request.query_params.get('phone')
        try:
            user = await User.objects.get(phone_number=phone_number)
            profile = UserService.get_user_profile(user)
            return Response(profile)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class ActivateInviteView(APIView):
    async def post(self, request):
        phone_number = request.data.get('phone')
        code = request.data.get('code')
        
        try:
            user = await User.objects.get(phone_number=phone_number)
            await UserService.activate_invite_code(user, code)
            return Response({"message": "Invite code activated successfully"})
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
Шаг 5: Настройка URL-паттернов
Создайте файл users/urls.py:

from django.urls import path
from .views import AuthView, VerifyCodeView, ProfileView, ActivateInviteView

urlpatterns = [
    path('auth/', AuthView.as_view(), name='auth'),
    path('verify-code/', VerifyCodeView.as_view(), name='verify_code'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('activate-invite/', ActivateInviteView.as_view(), name='activate_invite'),
]
И подключите их в основном urls.py вашего проекта:

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
]
Шаг 6: Документация API
Для документации API можно использовать ReDoc или Swagger.

Например, добавьте drf-yasg в ваш проект:

pip install drf-yasg
Добавьте к вашему urls.py в основном проекте следующее:

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Referral API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="support@yourdomain.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
Шаг 7: Создание Postman коллекции
Запустите сервер: bash python manage.py runserver
Откройте Postman и создайте коллекцию с запросами:
POST /users/auth/: отправить номер телефона.
POST /users/verify-code/: авторизация по коду.
GET /users/profile/?phone=<номер_телефона>: получить профиль пользователя.
POST /users/activate-invite/: активировать инвайт-код.
Протестируйте каждый запрос и сохраните их в коллекции Postman.
Шаг 8: Деплой приложения
Для деплоя можно использовать Heroku или PythonAnywhere. Например, для Heroku:

Установите Heroku CLI.
Выполните вход в свою учетную запись: bash heroku login
Создайте новый проект Heroku: bash heroku create имя_вашего_проекта
Свяжите проект с вашим репозиторием и запустите: bash git init heroku git:remote -a имя_вашего_проекта git add . git commit -m "Initial commit" git push heroku master
