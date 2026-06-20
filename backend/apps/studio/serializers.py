"""Serializers for the Content Studio API."""
from rest_framework import serializers

from apps.content.models import Category, CategoryTranslation, Language, UIString
from apps.content.serializers import CategorySerializer

from .models import GenerationJob, SegmentAsset, StoryDraft, StorySegment


class SegmentAssetSerializer(serializers.ModelSerializer):
    language = serializers.CharField(source="language_id", allow_null=True)

    class Meta:
        model = SegmentAsset
        fields = [
            "id",
            "asset_type",
            "language",
            "status",
            "content",
            "asset_url",
            "audio_start_sec",
            "audio_end_sec",
            "generation_cost_usd",
            "generated_at",
            "error_message",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "asset_url",
            "audio_start_sec",
            "audio_end_sec",
            "generation_cost_usd",
            "generated_at",
            "error_message",
            "updated_at",
        ]


class StorySegmentSerializer(serializers.ModelSerializer):
    assets = SegmentAssetSerializer(many=True, read_only=True)

    class Meta:
        model = StorySegment
        fields = ["id", "index", "image_prompt", "status", "assets", "updated_at"]
        read_only_fields = ["id", "index", "status", "assets", "updated_at"]


class StoryDraftListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for the story list view."""

    category_slug = serializers.CharField(source="category.slug", read_only=True)
    total_cost_usd = serializers.SerializerMethodField()
    segment_count = serializers.SerializerMethodField()

    class Meta:
        model = StoryDraft
        fields = [
            "id",
            "title",
            "age_group",
            "category_slug",
            "languages",
            "status",
            "total_cost_usd",
            "segment_count",
            "created_at",
            "updated_at",
        ]

    def get_total_cost_usd(self, obj):
        return obj.total_cost_usd

    def get_segment_count(self, obj):
        return obj.segments.count()


class StoryDraftDetailSerializer(serializers.ModelSerializer):
    """Full serializer including segments for the story editor view."""

    category_slug = serializers.CharField(source="category.slug", read_only=True)
    segments = StorySegmentSerializer(many=True, read_only=True)
    total_cost_usd = serializers.SerializerMethodField()

    class Meta:
        model = StoryDraft
        fields = [
            "id",
            "title",
            "idea_text",
            "age_group",
            "category",
            "category_slug",
            "languages",
            "style_block",
            "status",
            "linked_story",
            "segments",
            "total_cost_usd",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "status", "linked_story", "segments", "total_cost_usd", "created_at", "updated_at"]

    def get_total_cost_usd(self, obj):
        return obj.total_cost_usd


class StoryDraftCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoryDraft
        fields = ["title", "idea_text", "age_group", "category", "languages"]

    def validate_languages(self, value):
        if not value:
            raise serializers.ValidationError("At least one language is required.")
        active = set(Language.objects.filter(is_active=True).values_list("code", flat=True))
        bad = [l for l in value if l not in active]
        if bad:
            raise serializers.ValidationError(f"Inactive or unknown languages: {bad}")
        return value


class GenerationJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenerationJob
        fields = [
            "id",
            "job_type",
            "status",
            "external_provider",
            "segment",
            "asset",
            "started_at",
            "finished_at",
            "error_message",
            "created_at",
        ]


# ── CMS: Categories ──────────────────────────────────────────────────────────

class CategoryTranslationWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryTranslation
        fields = ["language", "name"]


class CategoryWriteSerializer(serializers.ModelSerializer):
    translations = CategoryTranslationWriteSerializer(many=True, required=False)

    class Meta:
        model = Category
        fields = ["slug", "icon_url", "display_order", "translations"]

    def create(self, validated_data):
        translations = validated_data.pop("translations", [])
        category = Category.objects.create(**validated_data)
        for t in translations:
            CategoryTranslation.objects.create(category=category, **t)
        return category

    def update(self, instance, validated_data):
        translations = validated_data.pop("translations", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if translations is not None:
            for t in translations:
                CategoryTranslation.objects.update_or_create(
                    category=instance, language=t["language"], defaults={"name": t["name"]}
                )
        return instance


# ── CMS: UI Strings ──────────────────────────────────────────────────────────

class UIStringSerializer(serializers.ModelSerializer):
    language = serializers.CharField(source="language_id")

    class Meta:
        model = UIString
        fields = ["id", "key", "language", "value"]
        read_only_fields = ["id", "key", "language"]
