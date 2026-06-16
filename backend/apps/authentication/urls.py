"""URL patterns for authentication endpoints."""
from django.urls import path

from .views import GoogleAuthView, LogoutView, TokenRefreshView

urlpatterns = [
    path("google", GoogleAuthView.as_view(), name="auth-google"),
    path("refresh", TokenRefreshView.as_view(), name="auth-refresh"),
    path("logout", LogoutView.as_view(), name="auth-logout"),
]
