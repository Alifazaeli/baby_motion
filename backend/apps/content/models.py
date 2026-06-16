"""Content models: Language, Category, Story and their translations.

Stories are language-neutral; translated text and manifests live in
StoryTranslation. UI strings (button labels, etc.) live in UIString.
"""
import uuid

from django.db import models


class Language(models.Model):
    """Supported content languages. Adding a row is all that's needed to support a new language."""

    code = models.CharField(max_length=10, primary_key=True)
    display_name = models.CharField(max_length=50)
    is_rtl = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "languages"

    def __str__(self) -> str:
        return f"{self.display_name} ({self.code})"


class Category(models.Model):
    """Story category (bedtime, routine, emotion, adventure)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(unique=True)
    icon_url = models.TextField(blank=True, default="")
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "categories"
        ordering = ["display_order"]

    def __str__(self) -> str:
        return self.slug


class CategoryTranslation(models.Model):
    """Translated name for a Category in a specific language."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="translations")
    language = models.ForeignKey(Language, on_delete=models.CASCADE, to_field="code", db_column="language")
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "category_translations"
        unique_together = [("category", "language")]

    def __str__(self) -> str:
        return f"{self.category.slug}/{self.language_id}: {self.name}"


class Story(models.Model):
    """A story entry — language-neutral metadata.

    `age_group` here IS stored because it is a property of the content itself
    (written for a specific developmental stage), not a property of the child.
    Only the child's current age group is computed at runtime.
    """

    AGE_GROUP_CHOICES = [
        ("12_18m", "12–18 months"),
        ("18_30m", "18–30 months"),
        ("30_42m", "30–42 months"),
        ("42_60m", "42–60 months"),
    ]

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("review", "Review"),
        ("published", "Published"),
        ("archived", "Archived"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="stories")
    age_group = models.CharField(max_length=20, choices=AGE_GROUP_CHOICES)
    duration_seconds = models.IntegerField(null=True, blank=True)
    cover_url = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "stories"
        indexes = [
            models.Index(fields=["status", "age_group"]),
            models.Index(fields=["category", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.slug} [{self.age_group}] ({self.status})"


class StoryTranslation(models.Model):
    """Translated text + manifest URL for a Story in a specific language."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name="translations")
    language = models.ForeignKey(Language, on_delete=models.CASCADE, to_field="code", db_column="language")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    manifest_url = models.TextField()

    class Meta:
        db_table = "story_translations"
        unique_together = [("story", "language")]
        indexes = [models.Index(fields=["language", "story"])]

    def __str__(self) -> str:
        return f"{self.story.slug}/{self.language_id}: {self.title}"


class UIString(models.Model):
    """A single UI string key + translation. Source of truth for all client UI text."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=200)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, to_field="code", db_column="language")
    value = models.TextField()

    class Meta:
        db_table = "ui_strings"
        unique_together = [("key", "language")]
        indexes = [models.Index(fields=["language"])]

    def __str__(self) -> str:
        return f"{self.key}/{self.language_id}"
