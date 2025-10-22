from rest_framework import permissions


class IsActiveEmployee(permissions.BasePermission):
    """
    Разрешение только для активных сотрудников.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_active


class IsManager(permissions.BasePermission):
    """Разрешение для менеджеров"""
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and
                request.user.is_active and request.user.groups.filter(name='Managers').exists())


class IsAdmin(permissions.BasePermission):
    """Разрешение для администраторов"""
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and
                request.user.is_active and request.user.is_staff)
