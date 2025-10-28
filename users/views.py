from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import update_session_auth_hash, authenticate, login
from .models import User
from .serializers import UserSerializer, UserCreateSerializer
from .permissions import IsActiveEmployee


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления пользователями.
    """

    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsActiveEmployee]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == "create":
            # Создание пользователей могут только админы
            return [IsAuthenticated(), IsActiveEmployee()]
        return super().get_permissions()

    @action(detail=False, methods=["get"])
    def me(self, request):
        """Получение информации о текущем пользователе"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["put", "patch"])
    def update_me(self, request):
        """Обновление информации о текущем пользователе"""
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


def email_verification(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.token = ""
    user.save()
    messages.success(request, "Email успешно подтвержден! Теперь вы можете войти.")
    return redirect("user:login")


@method_decorator(csrf_protect, name="dispatch")
class CustomLoginView(View):
    template_name = "user/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("/")
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get("username")
        password = request.POST.get("password")

        print(f"Попытка входа с email: {email}")

        # Аутентифицируем пользователя
        user = authenticate(request, username=email, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f"Добро пожаловать, {user.email}!")
                print(f"Успешный вход для пользователя: {user.email}")
                return redirect("main")
            else:
                messages.error(
                    request,
                    "Ваш аккаунт не активирован. Проверьте email для подтверждения.",
                )
                print("Вход не удался: аккаунт не активен")
        else:
            messages.error(request, "Неверный email или пароль.")
            print("Вход не удался: неверные учетные данные")

        return render(request, self.template_name)
