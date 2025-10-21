from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from . import views

# Создание router для API
router = DefaultRouter()
router.register(r'network-nodes', views.NetworkNodeViewSet, basename='network-node')
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'node-products', views.NetworkNodeProductViewSet, basename='node-product')

# Настройка документации API
schema_view = get_schema_view(
    openapi.Info(
        title="Electronics Network API",
        default_version='v1',
        description="API для управления сетью по продаже электроники",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@electronics.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # API endpoints через router
    path('api/', include(router.urls)),

    # Документация API
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Аутентификация
    path('api/auth/', include('rest_framework.urls')),

    # Продукты узла
    path('api/network-nodes/<int:pk>/products/',
         views.NetworkNodeViewSet.as_view({'get': 'products'}),
         name='network-node-products'),

    path('api/network-nodes/<int:pk>/add-product/',
         views.NetworkNodeViewSet.as_view({'post': 'add_product'}),
         name='network-node-add-product'),

    path('api/network-nodes/<int:pk>/remove-product/',
         views.NetworkNodeViewSet.as_view({'delete': 'remove_product'}),
         name='network-node-remove-product'),

    # Поставщики и иерархия
    path('api/network-nodes/<int:pk>/supplier-chain/',
         views.NetworkNodeViewSet.as_view({'get': 'supplier_chain'}),
         name='network-node-supplier-chain'),

    path('api/network-nodes/<int:pk>/available-supplier-products/',
         views.NetworkNodeViewSet.as_view({'get': 'available_supplier_products'}),
         name='network-node-available-supplier-products'),

    # Иерархия сети
    path('api/network-nodes/hierarchy/',
         views.NetworkNodeViewSet.as_view({'get': 'hierarchy'}),
         name='network-hierarchy'),

    # Очистка задолженности
    path('api/network-nodes/<int:pk>/clear-debt/',
         views.NetworkNodeViewSet.as_view({'post': 'clear_debt'}),
         name='network-node-clear-debt'),

    # Статистика
    path('api/network-nodes/statistics/',
         views.NetworkNodeViewSet.as_view({'get': 'statistics'}),
         name='network-statistics'),

    # Продукты
    path('api/products/<int:pk>/assign-to-node/',
         views.ProductViewSet.as_view({'post': 'assign_to_node'}),
         name='product-assign-to-node'),

    path('api/products/<int:pk>/remove-from-node/',
         views.ProductViewSet.as_view({'post': 'remove_from_node'}),
         name='product-remove-from-node'),

    path('api/products/in-network/',
         views.ProductViewSet.as_view({'get': 'in_network'}),
         name='products-in-network'),
]
