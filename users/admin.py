from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = [
        'username', 'email', 'first_name', 'last_name',
        'is_employee', 'department', 'is_active', 'is_staff'
    ]
    list_filter = ['is_employee', 'is_active', 'is_staff', 'department']
    search_fields = ['username', 'email', 'first_name', 'last_name']

    fieldsets = UserAdmin.fieldsets + (
        ('Информация о сотруднике', {
            'fields': ('is_employee', 'department', 'position', 'phone', 'hire_date')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Информация о сотруднике', {
            'fields': ('is_employee', 'department', 'position', 'phone', 'hire_date')
        }),
    )
