from django.db import models
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q

from . import serializers
from .models import NetworkNode, Product
from .serializers import NetworkNodeSerializer, NetworkNodeCreateSerializer, ProductSerializer
from .filters import NetworkNodeFilter
from .permissions import IsActiveEmployee


class NetworkNodeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с узлами сети.
    """
    permission_classes = [IsActiveEmployee]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = NetworkNodeFilter
    search_fields = ['name', 'email', 'city', 'country']
    ordering_fields = ['name', 'city', 'country', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        queryset = NetworkNode.objects.select_related('supplier').prefetch_related('products')

        # Дополнительная фильтрация по уровню иерархии
        level = self.request.query_params.get('level', None)
        if level is not None:
            if level == '0':
                queryset = queryset.filter(supplier__isnull=True)
            elif level == '1':
                queryset = queryset.filter(supplier__supplier__isnull=True, supplier__isnull=False)
            elif level == '2':
                queryset = queryset.filter(supplier__supplier__isnull=False)

        # Фильтрация по типу узла
        node_type = self.request.query_params.get('node_type', None)
        if node_type:
            queryset = queryset.filter(node_type=node_type)

        return queryset

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return NetworkNodeCreateSerializer
        return NetworkNodeSerializer

    def perform_create(self, serializer):
        """Создание узла сети с валидацией иерархии"""
        instance = serializer.save()
        self._validate_hierarchy(instance)

    def perform_update(self, serializer):
        """Обновление узла сети с валидацией иерархии"""
        instance = serializer.save()
        self._validate_hierarchy(instance)

    def _validate_hierarchy(self, instance):
        """Валидация иерархии сети"""
        if instance.supplier:
            # Проверка на циклические связи
            current = instance.supplier
            visited = {instance.id}

            while current:
                if current.id in visited:
                    raise serializers.ValidationError(
                        "Обнаружена циклическая связь в иерархии сети"
                    )
                visited.add(current.id)
                current = current.supplier

    @action(detail=False, methods=['get'])
    def hierarchy(self, request):
        """
        Получение иерархии сети.
        """
        roots = NetworkNode.objects.filter(supplier__isnull=True)
        hierarchy_data = []

        for root in roots:
            hierarchy_data.append(self._build_hierarchy_tree(root))

        return Response(hierarchy_data)

    def _build_hierarchy_tree(self, node):
        """Рекурсивное построение дерева иерархии"""
        node_data = NetworkNodeSerializer(node).data
        children = NetworkNode.objects.filter(supplier=node)

        if children.exists():
            node_data['children'] = [
                self._build_hierarchy_tree(child) for child in children
            ]

        return node_data

    @action(detail=True, methods=['post'])
    def clear_debt(self, request, pk=None):
        """
        Очистка задолженности для конкретного узла.
        """
        node = self.get_object()
        node.debt = 0
        node.save()

        return Response({
            'status': 'Задолженность очищена',
            'node_id': node.id,
            'node_name': node.name
        })

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Статистика по сети.
        """
        total_nodes = NetworkNode.objects.count()
        factories = NetworkNode.objects.filter(node_type='factory').count()
        retail_chains = NetworkNode.objects.filter(node_type='retail').count()
        entrepreneurs = NetworkNode.objects.filter(node_type='entrepreneur').count()

        # Узлы с задолженностью
        nodes_with_debt = NetworkNode.objects.filter(debt__gt=0).count()
        total_debt = NetworkNode.objects.aggregate(
            total_debt=models.Sum('debt')
        )['total_debt'] or 0

        return Response({
            'total_nodes': total_nodes,
            'factories': factories,
            'retail_chains': retail_chains,
            'entrepreneurs': entrepreneurs,
            'nodes_with_debt': nodes_with_debt,
            'total_debt': float(total_debt)
        })


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с продуктами.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsActiveEmployee]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'model']
    ordering_fields = ['name', 'model', 'release_date']
    ordering = ['name']

    @action(detail=True, methods=['post'])
    def assign_to_node(self, request, pk=None):
        """
        Назначение продукта узлу сети.
        """
        product = self.get_object()
        node_id = request.data.get('node_id')

        try:
            node = NetworkNode.objects.get(id=node_id)
            product.network_nodes.add(node)

            return Response({
                'status': f'Продукт {product.name} назначен узлу {node.name}',
                'product_id': product.id,
                'node_id': node.id
            })
        except NetworkNode.DoesNotExist:
            return Response(
                {'error': 'Узел сети не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def remove_from_node(self, request, pk=None):
        """
        Удаление продукта из узла сети.
        """
        product = self.get_object()
        node_id = request.data.get('node_id')

        try:
            node = NetworkNode.objects.get(id=node_id)
            product.network_nodes.remove(node)

            return Response({
                'status': f'Продукт {product.name} удален из узла {node.name}',
                'product_id': product.id,
                'node_id': node.id
            })
        except NetworkNode.DoesNotExist:
            return Response(
                {'error': 'Узел сети не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
