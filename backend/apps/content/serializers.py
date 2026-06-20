"""Serializers for content endpoints."""
from rest_framework import serializers

from .models import Category, Language, Story, StoryTranslation


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ["code", "display_name", "is_rtl", "is_active"]


class CategorySerializer(serializers.ModelSerializer):
    """Category with localized name (populated by the view from CategoryTranslation)."""

    name = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "slug", "name", "icon_url", "display_order"]

    def get_name(self, obj: Category) -> str:
        """Return the translation stored on the instance by the view, or fall back to slug."""
        return getattr(obj, "_translated_name", obj.slug)


class StoryTranslationSerializer(serializers.ModelSerializer):
    """Embedded translation fields for a story."""

    class Meta:
        model = StoryTranslation
        fields = ["title", "description", "manifest_url"]


class StorySerializer(serializers.ModelSerializer):
    """Story with embedded translation for the requested language."""

    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    manifest_url = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = [
            "id",
            "slug",
            "category_id",
            "age_group",
            "duration_seconds",
            "cover_url",
            "status",
            "published_at",
            "title",
            "description",
            "manifest_url",
        ]

    def _get_translation(self, obj: Story) -> StoryTranslation | None:
        """Return the translation cached on the instance by the view."""
        return getattr(obj, "_translation", None)

    def get_title(self, obj: Story) -> str:
        t = self._get_translation(obj)
        return t.title if t else ""

    def get_description(self, obj: Story) -> str:
        t = self._get_translation(obj)
        return t.description if t else ""

    def get_manifest_url(self, obj: Story) -> str:
        t = self._get_translation(obj)
        return t.manifest_url if t else ""
