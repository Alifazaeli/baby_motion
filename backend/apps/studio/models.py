"""Content Studio data model.

StoryDraft → StorySegment → SegmentAsset (one per segment × language × asset_type).
Scenes are first-class DB rows enabling partial regeneration and per-asset status tracking.
On publish the system projects these rows into a manifest JSON file on Arvan Cloud,
then upserts the existing Story + StoryTranslation rows — zero client-side changes needed.
"""
import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models


class StoryDraft(models.Model):
    STATUS_CHOICES = [
        ("drafting", "Drafting"),
        ("generating", "Generating"),
        ("review", "Review"),
        ("published", "Published"),
        ("archived", "Archived"),
    ]

    AGE_GROUP_CHOICES = [
        ("12_18m", "12–18 months"),
        ("18_30m", "18–30 months"),
        ("30_42m", "30–42 months"),
        ("42_60m", "42–60 months"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.TextField(blank=True, default="")
    idea_text = models.TextField()
    age_group = models.CharField(max_length=20, choices=AGE_GROUP_CHOICES)
    category = models.ForeignKey(
        "content.Category", on_delete=models.PROTECT, related_name="story_drafts"
    )
    languages = ArrayField(models.CharField(max_length=10), default=list)
    style_block = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="drafting")
    linked_story = models.ForeignKey(
        "content.Story",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="draft",
    )
    created_by = models.ForeignKey(
        "users.AdminUser",
        on_delete=models.PROTECT,
        related_name="story_drafts",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "story_drafts"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title or self.idea_text[:50]} [{self.status}]"

    @property
    def total_cost_usd(self) -> float:
        """Running generation cost summed across all segment assets."""
        from django.db.models import Sum

        result = SegmentAsset.objects.filter(
            segment__draft=self
        ).aggregate(total=Sum("generation_cost_usd"))
        return float(result["total"] or 0)


class StorySegment(models.Model):
    """One scene in a StoryDraft. Language-neutral — assets per language live in SegmentAsset."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("generating", "Generating"),
        ("ready", "Ready"),
        ("stale", "Stale"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    draft = models.ForeignKey(StoryDraft, on_delete=models.CASCADE, related_name="segments")
    index = models.IntegerField()
    image_prompt = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "story_segments"
        unique_together = [("draft", "index")]
        ordering = ["index"]

    def __str__(self) -> str:
        return f"Draft {self.draft_id} / scene {self.index}"

    def recompute_status(self) -> None:
        """Roll up child SegmentAsset statuses into this segment's status and save."""
        assets = list(self.assets.all())
        if not assets:
            self.status = "pending"
        elif any(a.status == "failed" for a in assets):
            self.status = "failed"
        elif any(a.status == "stale" for a in assets):
            self.status = "stale"
        elif any(a.status in ("pending", "generating") for a in assets):
            self.status = "generating"
        elif all(a.status == "ready" for a in assets):
            self.status = "ready"
        else:
            self.status = "pending"
        self.save(update_fields=["status", "updated_at"])


class SegmentAsset(models.Model):
    """One generated artifact: (segment, asset_type, language).

    image assets are language-neutral (language=None).
    text/audio assets have a language.
    """

    ASSET_TYPE_CHOICES = [
        ("text", "Text"),
        ("image", "Image"),
        ("audio", "Audio"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("generating", "Generating"),
        ("ready", "Ready"),
        ("stale", "Stale"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    segment = models.ForeignKey(StorySegment, on_delete=models.CASCADE, related_name="assets")
    asset_type = models.CharField(max_length=10, choices=ASSET_TYPE_CHOICES)
    language = models.ForeignKey(
        "content.Language",
        on_delete=models.CASCADE,
        to_field="code",
        db_column="language",
        null=True,
        blank=True,
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    content = models.TextField(blank=True, default="")   # narration text (text assets only)
    asset_url = models.TextField(blank=True, default="")  # draft storage URL (image/audio)
    audio_start_sec = models.FloatField(null=True, blank=True)
    audio_end_sec = models.FloatField(null=True, blank=True)
    generation_input = models.JSONField(default=dict, blank=True)
    generation_cost_usd = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    generated_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "segment_assets"
        unique_together = [("segment", "asset_type", "language")]
        ordering = ["segment__index", "asset_type"]

    def __str__(self) -> str:
        lang = self.language_id or "–"
        return f"Segment {self.segment_id} / {self.asset_type} / {lang} [{self.status}]"


class GenerationJob(models.Model):
    """Audit log for every async generation call dispatched to Claude/Imagen3/ElevenLabs."""

    JOB_TYPE_CHOICES = [
        ("segmentation", "Segmentation"),
        ("image", "Image"),
        ("audio", "Audio"),
    ]

    STATUS_CHOICES = [
        ("queued", "Queued"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    PROVIDER_CHOICES = [
        ("claude", "Claude"),
        ("imagen3", "Imagen 3"),
        ("elevenlabs", "ElevenLabs"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    draft = models.ForeignKey(StoryDraft, on_delete=models.CASCADE, related_name="jobs")
    segment = models.ForeignKey(
        StorySegment, on_delete=models.CASCADE, null=True, blank=True, related_name="jobs"
    )
    asset = models.ForeignKey(
        SegmentAsset, on_delete=models.CASCADE, null=True, blank=True, related_name="jobs"
    )
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="queued")
    external_provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, blank=True)
    external_request_id = models.TextField(blank=True, default="")
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "generation_jobs"
        indexes = [
            models.Index(fields=["draft", "status"]),
            models.Index(fields=["draft", "job_type"]),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.job_type} / {self.external_provider} [{self.status}]"
