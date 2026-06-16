"""Views for analytics events and admin analytics dashboard."""
from __future__ import annotations

from django.db.models import Avg, Count
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.content.models import Story
from apps.users.models import AdminUser

from .models import ViewingSession
from .serializers import EndSessionSerializer, StartStorySerializer


class StartStoryView(APIView):
    """POST /stories/{id}/start — open a viewing session."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, story_id: str) -> Response:
        """Create a ViewingSession and return its ID to the client."""
        serializer = StartStorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        child = request.user.children.get(pk=serializer.validated_data["child_id"])
        story = Story.objects.get(pk=story_id, status="published")

        session = ViewingSession.objects.create(
            child=child,
            story=story,
            language=serializer.validated_data["language"],
        )
        return Response({"session_id": str(session.id)}, status=status.HTTP_201_CREATED)


class CompleteSessionView(APIView):
    """POST /sessions/{id}/complete — mark a session as fully watched."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, session_id: str) -> Response:
        """Close a viewing session as completed."""
        serializer = EndSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session = ViewingSession.objects.get(pk=session_id, child__user=request.user)
        session.completed = True
        session.scenes_watched = serializer.validated_data["scenes_watched"]
        session.ended_at = timezone.now()
        session.save(update_fields=["completed", "scenes_watched", "ended_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class AbandonSessionView(APIView):
    """POST /sessions/{id}/abandon — mark a session as abandoned mid-play."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, session_id: str) -> Response:
        """Close a viewing session as abandoned (not completed)."""
        serializer = EndSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session = ViewingSession.objects.get(pk=session_id, child__user=request.user)
        session.completed = False
        session.scenes_watched = serializer.validated_data["scenes_watched"]
        session.ended_at = timezone.now()
        session.save(update_fields=["completed", "scenes_watched", "ended_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminAnalyticsOverviewView(APIView):
    """GET /admin/analytics/overview — DAU and aggregate stats (AP-4)."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        """Return high-level usage stats. Restricted to analyst+ roles."""
        self._check_role(request)
        today = timezone.now().date()
        dau = ViewingSession.objects.filter(started_at__date=today).values("child").distinct().count()
        total_sessions = ViewingSession.objects.count()
        completion_rate = ViewingSession.objects.filter(completed=True).count() / max(total_sessions, 1)
        return Response(
            {
                "dau": dau,
                "total_sessions": total_sessions,
                "completion_rate": round(completion_rate, 4),
            }
        )

    def _check_role(self, request: Request) -> None:
        try:
            role = request.user.admin_profile.role
            if role not in ("super_admin", "content_admin", "analyst"):
                raise PermissionError
        except (AdminUser.DoesNotExist, PermissionError):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied()


class AdminAnalyticsStoriesView(APIView):
    """GET /admin/analytics/stories — per-story view and completion stats (AP-4)."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        """Return view counts and completion rates per story."""
        stories = (
            ViewingSession.objects.values("story__slug", "story_id")
            .annotate(
                total_views=Count("id"),
                completions=Count("id", filter={"completed": True}),
                avg_scenes=Avg("scenes_watched"),
            )
            .order_by("-total_views")[:50]
        )
        return Response(list(stories))
