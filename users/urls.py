from django.contrib.auth.views import LogoutView
from django.urls import path, include
from .views import UserViewSet, CustomLoginView, email_verification
from django.contrib.auth import views as auth_views

app_name = "users"

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
]
