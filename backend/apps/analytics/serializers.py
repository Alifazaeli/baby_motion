"""Serializers for analytics endpoints."""
from rest_framework import serializers


class StartStorySerializer(serializers.Serializer):
    """Input for POST /stories/{id}/start."""

    child_id = serializers.UUIDField()
    language = serializers.CharField(max_length=10)


class EndSessionSerializer(serializers.Serializer):
    """Input for POST /sessions/{id}/complete and /sessions/{id}/abandon."""

    scenes_watched = serializers.IntegerField(min_value=0)
