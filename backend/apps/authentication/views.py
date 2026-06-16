"""Google OAuth authentication views.

Flow:
  1. Client sends Google ID token (obtained via Google Sign-In SDK).
  2. Backend verifies the token with Google's public keys.
  3. Backend upserts a User record keyed on google_sub.
  4. Backend issues its own JWT access + refresh pair.
"""
from __future__ import annotations

from django.conf import settings
from django.utils import timezone
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User
from apps.users.serializers import UserSerializer

from .serializers import GoogleAuthSerializer, TokenRefreshSerializer


class AuthRateThrottle(AnonRateThrottle):
    """10 requests/minute per IP for auth endpoints (FR-B4)."""
    rate = "10/min"


class GoogleAuthView(APIView):
    """POST /auth/google — exchange a Google ID token for a BabyMotion JWT pair."""

    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request: Request) -> Response:
        """Verify Google ID token and return access + refresh JWTs."""
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            claims = google_id_token.verify_oauth2_token(
                serializer.validated_data["id_token"],
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        google_sub = claims["sub"]
        email = claims.get("email", "")

        # Look up by google_sub first; fall back to email to handle token rotation edge cases.
        user = User.objects.filter(google_sub=google_sub).first()
        if user is None and email:
            user = User.objects.filter(email=email).first()
        if user is None:
            user = User(google_sub=google_sub, email=email)
        else:
            user.google_sub = google_sub
            user.email = email or user.email

        user.display_name = claims.get("name", "") or user.display_name
        user.last_login_at = timezone.now()
        user.save()

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class TokenRefreshView(APIView):
    """POST /auth/refresh — rotate a refresh token and return a new pair."""

    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request: Request) -> Response:
        """Issue a new access + refresh token pair from a valid refresh token."""
        serializer = TokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            refresh = RefreshToken(serializer.validated_data["refresh"])
            return Response(
                {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                status=status.HTTP_200_OK,
            )
        except TokenError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """POST /auth/logout — blacklist the provided refresh token."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        """Blacklist the refresh token, invalidating the session."""
        refresh_token = request.data.get("refresh")
        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except TokenError:
                pass
        return Response(status=status.HTTP_204_NO_CONTENT)
