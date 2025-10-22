from django.contrib import admin
from django.utils.html import format_html
from .models import NetworkNode, Product, NetworkNodeProduct


@admin.register(NetworkNode)
class NetworkNodeAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'node_type', 'city', 'country',
        'supplier_link', 'hierarchy_level', 'debt', 'created_at'
    ]
    list_filter = ['city', 'country', 'node_type', 'created_at']
    search_fields = ['name', 'email', 'city', 'country']
    readonly_fields = ['created_at', 'hierarchy_level']

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'node_type', 'supplier')
        }),
        ('Контакты', {
            'fields': ('email', 'country', 'city', 'street', 'house_number')
        }),
        ('Финансы', {
            'fields': ('debt',)
        }),
        ('Системная информация', {
            'fields': ('created_at', 'hierarchy_level', 'is_active')
        }),
    )

    actions = ['clear_debt_action']

    def supplier_link(self, obj):
        if obj.supplier:
            return format_html(
                '<a href="/admin/electronics/networknode/{}/change/">{}</a>',
                obj.supplier.id,
                obj.supplier.name
            )
        return "-"

    supplier_link.short_description = 'Поставщик'

    def clear_debt_action(self, request, queryset):
        """Admin action для очистки задолженности"""
        updated_count = queryset.update(debt=0)
        self.message_user(
            request,
            f'Задолженность очищена для {updated_count} объектов'
        )

    clear_debt_action.short_description = 'Очистить задолженность перед поставщиком'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'model', 'release_date', 'created_at']
    list_filter = ['release_date', 'created_at']
    search_fields = ['name', 'model']
    readonly_fields = ['created_at']


@admin.register(NetworkNodeProduct)
class NetworkNodeProductAdmin(admin.ModelAdmin):
    list_display = ['network_node', 'product', 'price', 'quantity', 'is_available']
    list_filter = ['is_available', 'added_at']
    search_fields = ['network_node__name', 'product__name']
    readonly_fields = ['added_at']