from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'network'

router = DefaultRouter()
router.register(r'network-nodes', views.NetworkNodeViewSet, basename='network-node')
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'node-products', views.NetworkNodeProductViewSet, basename='node-product')


urlpatterns = [
    # API endpoints через router
    path('', include(router.urls)),

    # Продукты узла
    path('network-nodes/<int:pk>/products/',
         views.NetworkNodeViewSet.as_view({'get': 'products'}),
         name='network-node-products'),

    path('network-nodes/<int:pk>/add-product/',
         views.NetworkNodeViewSet.as_view({'post': 'add_product'}),
         name='network-node-add-product'),

    path('network-nodes/<int:pk>/remove-product/',
         views.NetworkNodeViewSet.as_view({'delete': 'remove_product'}),
         name='network-node-remove-product'),

    # Поставщики и иерархия
    path('network-nodes/<int:pk>/supplier-chain/',
         views.NetworkNodeViewSet.as_view({'get': 'supplier_chain'}),
         name='network-node-supplier-chain'),

    path('network-nodes/<int:pk>/available-supplier-products/',
         views.NetworkNodeViewSet.as_view({'get': 'available_supplier_products'}),
         name='network-node-available-supplier-products'),

    # Иерархия сети
    path('network-nodes/hierarchy/',
         views.NetworkNodeViewSet.as_view({'get': 'hierarchy'}),
         name='network-hierarchy'),

    # Очистка задолженности
    path('network-nodes/<int:pk>/clear-debt/',
         views.NetworkNodeViewSet.as_view({'post': 'clear_debt'}),
         name='network-node-clear-debt'),

    # Статистика
    path('network-nodes/statistics/',
         views.NetworkNodeViewSet.as_view({'get': 'statistics'}),
         name='network-statistics'),

    # Продукты
    path('products/<int:pk>/assign-to-node/',
         views.ProductViewSet.as_view({'post': 'assign_to_node'}),
         name='product-assign-to-node'),

    path('products/<int:pk>/remove-from-node/',
         views.ProductViewSet.as_view({'post': 'remove_from_node'}),
         name='product-remove-from-node'),

    path('products/in-network/',
         views.ProductViewSet.as_view({'get': 'in_network'}),
         name='products-in-network'),
]
