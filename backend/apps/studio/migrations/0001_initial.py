"""Initial migration for apps.studio."""
import uuid

import django.contrib.postgres.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("content", "0001_initial"),
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="StoryDraft",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("title", models.TextField(blank=True, default="")),
                ("idea_text", models.TextField()),
                (
                    "age_group",
                    models.CharField(
                        choices=[
                            ("12_18m", "12–18 months"),
                            ("18_30m", "18–30 months"),
                            ("30_42m", "30–42 months"),
                            ("42_60m", "42–60 months"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "languages",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=10),
                        default=list,
                        size=None,
                    ),
                ),
                ("style_block", models.TextField(blank=True, default="")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("drafting", "Drafting"),
                            ("generating", "Generating"),
                            ("review", "Review"),
                            ("published", "Published"),
                            ("archived", "Archived"),
                        ],
                        default="drafting",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="story_drafts",
                        to="content.category",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="story_drafts",
                        to="users.adminuser",
                    ),
                ),
                (
                    "linked_story",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="draft",
                        to="content.story",
                    ),
                ),
            ],
            options={"db_table": "story_drafts", "ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="StorySegment",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("index", models.IntegerField()),
                ("image_prompt", models.TextField(blank=True, default="")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("generating", "Generating"),
                            ("ready", "Ready"),
                            ("stale", "Stale"),
                            ("failed", "Failed"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "draft",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="segments",
                        to="studio.storydraft",
                    ),
                ),
            ],
            options={
                "db_table": "story_segments",
                "ordering": ["index"],
            },
        ),
        migrations.AddConstraint(
            model_name="storysegment",
            constraint=models.UniqueConstraint(
                fields=("draft", "index"), name="unique_draft_segment_index"
            ),
        ),
        migrations.CreateModel(
            name="SegmentAsset",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                (
                    "asset_type",
                    models.CharField(
                        choices=[
                            ("text", "Text"),
                            ("image", "Image"),
                            ("audio", "Audio"),
                        ],
                        max_length=10,
                    ),
                ),
                ("status", models.CharField(
                    choices=[
                        ("pending", "Pending"),
                        ("generating", "Generating"),
                        ("ready", "Ready"),
                        ("stale", "Stale"),
                        ("failed", "Failed"),
                    ],
                    default="pending",
                    max_length=20,
                )),
                ("content", models.TextField(blank=True, default="")),
                ("asset_url", models.TextField(blank=True, default="")),
                ("audio_start_sec", models.FloatField(blank=True, null=True)),
                ("audio_end_sec", models.FloatField(blank=True, null=True)),
                ("generation_input", models.JSONField(blank=True, default=dict)),
                (
                    "generation_cost_usd",
                    models.DecimalField(decimal_places=4, default=0, max_digits=10),
                ),
                ("generated_at", models.DateTimeField(blank=True, null=True)),
                ("error_message", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "language",
                    models.ForeignKey(
                        blank=True,
                        db_column="language",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="content.language",
                        to_field="code",
                    ),
                ),
                (
                    "segment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="assets",
                        to="studio.storysegment",
                    ),
                ),
            ],
            options={
                "db_table": "segment_assets",
                "ordering": ["segment__index", "asset_type"],
            },
        ),
        migrations.AddConstraint(
            model_name="segmentasset",
            constraint=models.UniqueConstraint(
                fields=("segment", "asset_type", "language"),
                name="unique_segment_asset_language",
            ),
        ),
        migrations.AddIndex(
            model_name="segmentasset",
            index=models.Index(
                fields=["segment", "asset_type", "language"],
                name="idx_segment_asset_language",
            ),
        ),
        migrations.CreateModel(
            name="GenerationJob",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                (
                    "job_type",
                    models.CharField(
                        choices=[
                            ("segmentation", "Segmentation"),
                            ("image", "Image"),
                            ("audio", "Audio"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("queued", "Queued"),
                            ("running", "Running"),
                            ("completed", "Completed"),
                            ("failed", "Failed"),
                        ],
                        default="queued",
                        max_length=20,
                    ),
                ),
                ("external_provider", models.CharField(
                    blank=True,
                    choices=[
                        ("claude", "Claude"),
                        ("imagen3", "Imagen 3"),
                        ("elevenlabs", "ElevenLabs"),
                    ],
                    max_length=20,
                )),
                ("external_request_id", models.TextField(blank=True, default="")),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
                ("error_message", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "draft",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="jobs",
                        to="studio.storydraft",
                    ),
                ),
                (
                    "segment",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="jobs",
                        to="studio.storysegment",
                    ),
                ),
                (
                    "asset",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="jobs",
                        to="studio.segmentasset",
                    ),
                ),
            ],
            options={
                "db_table": "generation_jobs",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="generationjob",
            index=models.Index(fields=["draft", "status"], name="idx_job_draft_status"),
        ),
        migrations.AddIndex(
            model_name="generationjob",
            index=models.Index(fields=["draft", "job_type"], name="idx_job_draft_type"),
        ),
    ]
