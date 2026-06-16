"""Views for /me and /children endpoints."""
from __future__ import annotations

from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Child
from .serializers import ChildSerializer, MeSerializer
from .services import compute_age_group


class MeView(APIView):
    """GET /me — returns authenticated user + their children with computed age fields."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        """Return the current user and all child profiles."""
        serializer = MeSerializer(
            {"user": request.user, "children": request.user.children.all()}
        )
        return Response(serializer.data)


class ChildListCreateView(APIView):
    """POST /children — create a child profile for the authenticated user."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        """Create a child profile linked to the authenticated user."""
        serializer = ChildSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        child = serializer.save(user=request.user)
        return Response(ChildSerializer(child).data, status=status.HTTP_201_CREATED)


class ChildDetailView(APIView):
    """PATCH /children/{id} — update a child profile."""

    permission_classes = [IsAuthenticated]

    def _get_child(self, request: Request, child_id: str) -> Child:
        """Return the child if it belongs to the authenticated user."""
        return request.user.children.get(pk=child_id)

    def patch(self, request: Request, child_id: str) -> Response:
        """Partially update a child profile."""
        child = self._get_child(request, child_id)
        serializer = ChildSerializer(child, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        child = serializer.save()
        return Response(ChildSerializer(child).data)


class AcknowledgeAgeGroupView(APIView):
    """POST /children/{id}/acknowledge-age-group — dismiss the transition banner."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, child_id: str) -> Response:
        """Set last_seen_age_group to the current computed age group.

        Called when the parent dismisses the age-progression banner (FR-A11).
        After this, has_pending_age_group_transition returns False until the
        child crosses into another age group.
        """
        child = request.user.children.get(pk=child_id)
        current_group = compute_age_group(child.birth_year, child.birth_month)
        child.last_seen_age_group = current_group
        child.save(update_fields=["last_seen_age_group"])
        return Response(status=status.HTTP_204_NO_CONTENT)
