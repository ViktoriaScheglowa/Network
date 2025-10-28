from rest_framework import permissions


class IsActiveEmployee(permissions.BasePermission):
    """
    Разрешение только для активных сотрудников.
    """

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.is_active
        )


class IsManager(permissions.BasePermission):
    """
    Разрешение для менеджеров.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_active
            and hasattr(request.user, "role")
            and request.user.role
            in ["manager", "admin"]  # адаптируйте под вашу модель User
        )


class IsAdmin(permissions.BasePermission):
    """
    Разрешение для администраторов.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_active
            and (
                request.user.is_staff
                or (hasattr(request.user, "role") and request.user.role == "admin")
            )
        )
