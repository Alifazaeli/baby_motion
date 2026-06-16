"""Analytics models: viewing sessions per child per story."""
import uuid

from django.db import models

from apps.content.models import Story
from apps.users.models import Child


class ViewingSession(models.Model):
    """Records one viewing attempt of a story by a child."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="viewing_sessions")
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name="viewing_sessions")
    language = models.CharField(max_length=10)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    scenes_watched = models.IntegerField(default=0)

    class Meta:
        db_table = "viewing_sessions"
        indexes = [
            models.Index(fields=["child", "-started_at"]),
            models.Index(fields=["story"]),
        ]

    def __str__(self) -> str:
        return f"{self.child.name} → {self.story.slug} ({self.started_at:%Y-%m-%d})"
