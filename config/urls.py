from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from django.views.generic import TemplateView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Electronics Network API",
        default_version="v1",
        description="API для управления сетью по продаже электроники",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@electronics.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("admin/", admin.site.urls),
    path('network-nodes/', TemplateView.as_view(template_name='network_nodes.html'), name='network_nodes'),
    path('products/', TemplateView.as_view(template_name='products.html'), name='products'),
    path('api/', include('network.urls')),
    path('users/', include('users.urls', namespace='users')),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path('api/auth/', include('rest_framework.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
