from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя с дополнительными полями для сотрудников"""

    groups = models.ManyToManyField(
        "auth.Group",
        verbose_name="groups",
        blank=True,
        help_text="Группы, к которым принадлежит пользователь. "
        "Пользователь получит все разрешения, "
        "предоставленные каждой из его групп.",
        related_name="custom_user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        verbose_name="user permissions",
        blank=True,
        help_text="Особые разрешения для этого пользователя.",
        related_name="custom_user_set",
        related_query_name="user",
    )

    is_employee = models.BooleanField(default=True, verbose_name="Является сотрудником")
    department = models.CharField(max_length=100, blank=True, verbose_name="Отдел")
    position = models.CharField(max_length=100, blank=True, verbose_name="Должность")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    hire_date = models.DateField(
        null=True, blank=True, verbose_name="Дата приема на работу"
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.username} ({self.get_full_name() or self.email})"

    @property
    def is_active_employee(self):
        """Проверка, является ли пользователь активным сотрудником"""
        return self.is_active and self.is_employee
