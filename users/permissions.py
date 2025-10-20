from rest_framework import permissions


class IsActiveEmployee(permissions.BasePermission):
    """
    Разрешение только для активных сотрудников.
    Проверяет как is_active, так и is_employee.
    """

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_active and
            request.user.is_employee
        )
    