from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import update_session_auth_hash
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
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            # Создание пользователей могут только админы
            return [IsAuthenticated(), IsActiveEmployee()]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Получение информации о текущем пользователе"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'])
    def update_me(self, request):
        """Обновление информации о текущем пользователе"""
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    