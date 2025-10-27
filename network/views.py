
from django.views.generic import TemplateView
from rest_framework import viewsets, permissions, status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Sum
from .models import NetworkNode, Product, NetworkNodeProduct
from .serializers import (
    NetworkNodeSerializer,
    NetworkNodeCreateSerializer,
    ProductSerializer,
    NetworkNodeProductSerializer
)
from .filters import NetworkNodeFilter
from .permissions import IsActiveEmployee, IsManager, IsAdmin


class NetworkNodeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с узлами сети.
    """
    permission_classes = [IsActiveEmployee]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = NetworkNodeFilter
    search_fields = ['name', 'email', 'city', 'country']
    ordering_fields = ['name', 'city', 'country', 'created_at', 'hierarchy_level']
    ordering = ['name']

    def get_queryset(self):
        return NetworkNode.objects.select_related('supplier').prefetch_related(
            'networknodeproduct_set__product'
        )

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsActiveEmployee(), IsManager()]
        elif self.action in ['clear_debt', 'add_product', 'remove_product']:
            return [IsActiveEmployee(), IsManager()]
        else:
            return [IsActiveEmployee()]

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
            current = instance.supplier
            visited = {instance.id}

            while current:
                if current.id in visited:
                    from django.db import transaction
                    transaction.set_rollback(True)
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

        if node.debt == 0:
            return Response(
                {'error': 'Задолженность уже равна нулю'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if node.debt < 0:
            return Response(
                {'error': 'Некорректная задолженность'},
                status=status.HTTP_400_BAD_REQUEST
            )

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
            total_debt=Sum('debt')
        )['total_debt'] or 0

        return Response({
            'total_nodes': total_nodes,
            'factories': factories,
            'retail_chains': retail_chains,
            'entrepreneurs': entrepreneurs,
            'nodes_with_debt': nodes_with_debt,
            'total_debt': float(total_debt)
        })

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """
        Получение продуктов конкретного узла сети.
        """
        node = self.get_object()
        products = node.networknodeproduct_set.select_related('product').all()
        serializer = NetworkNodeProductSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_product(self, request, pk=None):
        """
        Добавление продукта в узел сети.
        """
        node = self.get_object()
        product_id = request.data.get('product_id')
        price = request.data.get('price')
        quantity = request.data.get('quantity', 0)
        is_available = request.data.get('is_available', True)

        try:
            product = Product.objects.get(id=product_id)

            # Создаем связь через промежуточную модель
            node_product, created = NetworkNodeProduct.objects.get_or_create(
                network_node=node,
                product=product,
                defaults={
                    'price': price,
                    'quantity': quantity,
                    'is_available': is_available
                }
            )

            if not created:
                # Обновляем существующую запись
                node_product.price = price
                node_product.quantity = quantity
                node_product.is_available = is_available
                node_product.save()

            serializer = NetworkNodeProductSerializer(node_product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Product.DoesNotExist:
            return Response(
                {'error': 'Продукт не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['delete'])
    def remove_product(self, request, pk=None):
        """
        Удаление продукта из узла сети.
        """
        node = self.get_object()
        product_id = request.data.get('product_id')

        try:
            product = Product.objects.get(id=product_id)
            node_product = NetworkNodeProduct.objects.get(
                network_node=node,
                product=product
            )
            node_product.delete()

            return Response({
                'status': f'Продукт {product.name} удален из узла {node.name}'
            })

        except (Product.DoesNotExist, NetworkNodeProduct.DoesNotExist):
            return Response(
                {'error': 'Продукт не найден в узле сети'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'])
    def supplier_chain(self, request, pk=None):
        """
        Получение цепочки поставщиков для конкретного узла.
        Показывает всех поставщиков от текущего узла до завода.
        """
        node = self.get_object()
        chain = []
        current = node.supplier

        while current:
            chain.append(NetworkNodeSerializer(current).data)
            current = current.supplier

        return Response({
            'node': NetworkNodeSerializer(node).data,
            'supplier_chain': chain,
            'chain_length': len(chain)
        })

    @action(detail=True, methods=['get'])
    def available_supplier_products(self, request, pk=None):
        """
        Получение продуктов, доступных у поставщика данного узла.
        """
        node = self.get_object()

        if not node.supplier:
            return Response({
                'message': 'У данного узла нет поставщика',
                'available_products': []
            })

        # Получаем продукты поставщика через промежуточную модель
        supplier_products = NetworkNodeProduct.objects.filter(
            network_node=node.supplier,
            is_available=True
        ).select_related('product')

        serializer = NetworkNodeProductSerializer(supplier_products, many=True)

        return Response({
            'supplier': NetworkNodeSerializer(node.supplier).data,
            'available_products': serializer.data,
            'products_count': supplier_products.count()
        })

    def update(self, request, *args, **kwargs):
        """Запрет обновления поля debt через API"""
        # Удаляем debt из данных запроса перед обновлением
        if 'debt' in request.data:
            # Создаем копию данных без поля debt
            data = request.data.copy()
            data.pop('debt')

            # Используем partial=True для PATCH запросов
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            return Response(serializer.data)

        return super().update(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def by_country(self, request):
        """
        Фильтрация узлов по стране.
        Пример: /api/network-nodes/by_country/?country=Россия
        """
        country = request.query_params.get('country')
        if not country:
            return Response(
                {'error': 'Параметр country обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        nodes = self.get_queryset().filter(country__iexact=country)
        serializer = self.get_serializer(nodes, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с продуктами.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsActiveEmployee]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'model']
    ordering_fields = ['name', 'model', 'release_date', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        queryset = Product.objects.all()

        # Только поиск по названию и модели
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(model__icontains=search)
            )

        return queryset

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [IsActiveEmployee(), IsAdmin()]
        elif self.action in ['update', 'partial_update', 'assign_to_node', 'remove_from_node']:
            return [IsActiveEmployee(), IsManager()]
        else:
            return [IsActiveEmployee()]

    @action(detail=True, methods=['post'])
    def assign_to_node(self, request, pk=None):
        """
        Назначение продукта узлу сети.
        """
        product = self.get_object()
        node_id = request.data.get('node_id')
        price = request.data.get('price')
        quantity = request.data.get('quantity', 0)
        is_available = request.data.get('is_available', True)

        try:
            node = NetworkNode.objects.get(id=node_id)

            node_product, created = NetworkNodeProduct.objects.get_or_create(
                network_node=node,
                product=product,
                defaults={
                    'price': price,
                    'quantity': quantity,
                    'is_available': is_available
                }
            )

            status_msg = 'назначен' if created else 'обновлен'
            return Response({
                'status': f'Продукт {product.name} {status_msg} узлу {node.name}',
                'product_id': product.id,
                'node_id': node.id,
                'price': node_product.price,
                'quantity': node_product.quantity
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

            node_product = NetworkNodeProduct.objects.get(
                network_node=node,
                product=product
            )
            node_product.delete()

            return Response({
                'status': f'Продукт {product.name} удален из узла {node.name}',
                'product_id': product.id,
                'node_id': node.id
            })

        except (NetworkNode.DoesNotExist, NetworkNodeProduct.DoesNotExist):
            return Response(
                {'error': 'Продукт не найден в узле сети'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def in_network(self, request):
        """
        Получение продуктов с информацией в каких узлах они есть.
        """
        products = Product.objects.prefetch_related('networknodeproduct_set__network_node').all()

        result = []
        for product in products:
            product_data = ProductSerializer(product).data
            nodes_data = []

            for node_product in product.networknodeproduct_set.all():
                nodes_data.append({
                    'node_id': node_product.network_node.id,
                    'node_name': node_product.network_node.name,
                    'price': node_product.price,
                    'quantity': node_product.quantity,
                    'is_available': node_product.is_available
                })

            product_data['network_nodes'] = nodes_data
            result.append(product_data)

        return Response(result)


class NetworkNodeProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы со связями узел-продукт.
    """
    queryset = NetworkNodeProduct.objects.select_related('network_node', 'product').all()
    serializer_class = NetworkNodeProductSerializer
    permission_classes = [IsActiveEmployee]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['network_node', 'product', 'is_available']
    search_fields = ['product__name', 'product__model', 'network_node__name']
    ordering_fields = ['price', 'quantity', 'added_at']
    ordering = ['-added_at']


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            # Получаем реальные города из базы данных
            cities_queryset = NetworkNode.objects.filter(
                city__isnull=False
            ).exclude(
                city__exact=''
            ).values_list(
                'city', flat=True
            ).distinct()

            # Преобразуем в список и сортируем
            cities_list = []
            for city in cities_queryset:
                if city:  # Проверяем что город не пустой
                    normalized_city = city.strip()  # Убираем пробелы в начале/конце
                    if normalized_city and normalized_city not in cities_list:
                        cities_list.append(normalized_city)
            cities_list.sort()

            context['cities'] = cities_list

            print(f"Найдено уникальных городов: {len(cities_list)}")
            print(f"Города: {cities_list}")

        except Exception as e:
            print(f"Ошибка при получении городов: {e}")
            context['cities'] = ['Москва', 'Санкт-Петербург', 'Новосибирск']
            print("Используем fallback города")

        print("=== HomeView DEBUG END ===")
        return context


class NetworkNodesView(TemplateView):
    template_name = 'network_nodes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print("=== NetworkNodesView DEBUG ===")

        try:
            # Получаем реальные города из базы данных
            cities_queryset = NetworkNode.objects.filter(
                city__isnull=False
            ).exclude(
                city__exact=''
            ).values_list(
                'city', flat=True
            ).distinct()

            # Нормализуем и убираем дубликаты
            cities_list = []
            for city in cities_queryset:
                if city:
                    normalized_city = city.strip()
                    if normalized_city and normalized_city not in cities_list:
                        cities_list.append(normalized_city)

            cities_list.sort()
            context['cities'] = cities_list

            print(f"NetworkNodesView - найдено городов: {len(cities_list)}")
            print(f"NetworkNodesView - города: {cities_list}")

        except Exception as e:
            print(f"Ошибка в NetworkNodesView: {e}")
            context['cities'] = ['Москва', 'Санкт-Петербург', 'Новосибирск']

        print("=== NetworkNodesView DEBUG END ===")
        return context


class ProductsView(TemplateView):
    template_name = 'products.html'
