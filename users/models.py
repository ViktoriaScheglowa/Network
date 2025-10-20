from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователя с дополнительными полями для сотрудников"""

    # Дополнительные поля для сотрудников
    is_employee = models.BooleanField(
        default=True,
        verbose_name='Является сотрудником'
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Отдел'
    )
    position = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Должность'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Телефон'
    )
    hire_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата приема на работу'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.username} ({self.get_full_name() or self.email})"

    @property
    def is_active_employee(self):
        """Проверка, является ли пользователь активным сотрудником"""
        return self.is_active and self.is_employee
    