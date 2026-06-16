"""Serializers for Google OAuth and JWT refresh endpoints."""
from rest_framework import serializers


class GoogleAuthSerializer(serializers.Serializer):
    """Input serializer for POST /auth/google."""

    id_token = serializers.CharField(help_text="Google ID token from client-side Sign-In flow.")


class TokenRefreshSerializer(serializers.Serializer):
    """Input serializer for POST /auth/refresh."""

    refresh = serializers.CharField(help_text="JWT refresh token.")
