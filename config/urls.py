from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from network.views import HomeView, NetworkNodesView, ProductsView

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
    # Веб-страницы (HTML)
    path('', HomeView.as_view(), name='home'),
    path('network-nodes/', NetworkNodesView.as_view(), name='network_nodes'),
    path('products/', ProductsView.as_view(), name='products'),
    path('users/', include('users.urls', namespace='users')),  # пространство имён users


    # API endpoints
    path('api/', include('network.urls')),

    # Документация API
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Аутентификация
    path('api/auth/', include('rest_framework.urls')),

    # Админ-панель
    path('admin/', admin.site.urls),
]
