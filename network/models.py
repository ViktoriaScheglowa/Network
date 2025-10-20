from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class Product(models.Model):
    """
    Модель продукта, которая теперь НЕ содержит связь с узлами сети.
    Продукты будут связаны через промежуточную модель NetworkNodeProduct.
    """
    name = models.CharField(max_length=255, verbose_name='Название')
    model = models.CharField(max_length=255, verbose_name='Модель')
    release_date = models.DateField(verbose_name='Дата выхода на рынок')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.model})"


class NetworkNode(models.Model):
    NODE_TYPES = (
        ('factory', 'Завод'),
        ('retail', 'Розничная сеть'),
        ('entrepreneur', 'Индивидуальный предприниматель'),
    )

    name = models.CharField(max_length=255, verbose_name='Название')
    node_type = models.CharField(max_length=20, choices=NODE_TYPES, verbose_name='Тип звена')

    # Контакты
    email = models.EmailField(verbose_name='Email')
    country = models.CharField(max_length=100, verbose_name='Страна')
    city = models.CharField(max_length=100, verbose_name='Город')
    street = models.CharField(max_length=255, verbose_name='Улица')
    house_number = models.CharField(max_length=10, verbose_name='Номер дома')

    # Продукты (связь через промежуточную модель)
    products = models.ManyToManyField(
        Product,
        through='NetworkNodeProduct',
        through_fields=('network_node', 'product'),
        related_name='network_nodes',
        verbose_name='Продукты'
    )

    # Иерархия
    supplier = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Поставщик',
        related_name='children'
    )

    debt = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='Задолженность перед поставщиком'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    is_active = models.BooleanField(default=True, verbose_name='Активный')

    class Meta:
        verbose_name = 'Узел сети'
        verbose_name_plural = 'Узлы сети'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_node_type_display()})"

    def clean(self):
        """Валидация иерархии сети"""
        if self.supplier and self.supplier == self:
            raise ValidationError("Узел не может быть своим собственным поставщиком")

        # Проверка на циклические связи
        if self.supplier:
            visited = {self.id}
            current = self.supplier

            while current:
                if current.id in visited:
                    raise ValidationError("Обнаружена циклическая связь в иерархии сети")
                visited.add(current.id)
                current = current.supplier

    @property
    def hierarchy_level(self):
        """Автоматическое определение уровня иерархии"""
        if self.supplier is None:
            return 0  # Завод

        level = 1
        current = self.supplier

        while current and current.supplier:
            level += 1
            current = current.supplier

            if level > 10:  # Защита от бесконечного цикла
                break

        return level

    def get_products_info(self):
        """Получение информации о продуктах узла"""
        return self.networknodeproduct_set.select_related('product')


class NetworkNodeProduct(models.Model):
    """
    Промежуточная модель для связи узла сети с продуктами.
    Позволяет добавить дополнительную информацию о продукте в контексте узла.
    """
    network_node = models.ForeignKey(
        NetworkNode,
        on_delete=models.CASCADE,
        verbose_name='Узел сети'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Продукт'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена',
        null=True,
        blank=True
    )
    quantity = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество на складе'
    )
    is_available = models.BooleanField(
        default=True,
        verbose_name='Доступен для продажи'
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )

    class Meta:
        verbose_name = 'Продукт узла сети'
        verbose_name_plural = 'Продукты узлов сети'
        unique_together = ['network_node', 'product']

    def __str__(self):
        return f"{self.product.name} в {self.network_node.name}"
