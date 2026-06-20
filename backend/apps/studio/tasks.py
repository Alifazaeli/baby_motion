"""Celery tasks for async generation jobs.

Each task:
1. Marks the GenerationJob as running.
2. Calls the appropriate service.
3. Uploads result to Arvan Cloud draft path.
4. Updates SegmentAsset status + cost.
5. Rolls up StorySegment status.
6. Marks the GenerationJob completed/failed.

Tasks are individually retryable — a single failure does not affect siblings (CS-16).
"""
from __future__ import annotations

import io
import logging
import uuid
from decimal import Decimal

import boto3
from celery import shared_task
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


def _s3():
    return boto3.client(
        "s3",
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        region_name=settings.AWS_S3_REGION_NAME,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )


def _draft_url(key: str) -> str:
    cdn = settings.AWS_S3_CUSTOM_DOMAIN
    bucket = settings.AWS_STORAGE_BUCKET_NAME
    if cdn:
        return f"https://{cdn}/{key}"
    return f"{settings.AWS_S3_ENDPOINT_URL}/{bucket}/{key}"


# ---------------------------------------------------------------------------
# Segmentation task (Claude)
# ---------------------------------------------------------------------------

@shared_task(bind=True, max_retries=0, name="studio.run_segmentation")
def run_segmentation(self, draft_id: str, job_id: str) -> None:
    from apps.studio.models import GenerationJob, SegmentAsset, StoryDraft, StorySegment
    from apps.studio.services.claude_service import ClaudeService

    job = GenerationJob.objects.get(pk=job_id)
    job.status = "running"
    job.started_at = timezone.now()
    job.save(update_fields=["status", "started_at"])

    draft = StoryDraft.objects.select_related("category").get(pk=draft_id)
    draft.status = "generating"
    draft.save(update_fields=["status"])

    try:
        svc = ClaudeService()
        result = svc.segment_story(
            idea_text=draft.idea_text,
            age_groups=draft.age_groups,
            languages=draft.languages,
            category_slug=draft.category.slug,
        )
    except Exception as exc:
        job.status = "failed"
        job.finished_at = timezone.now()
        job.error_message = str(exc)
        job.save(update_fields=["status", "finished_at", "error_message"])
        draft.status = "drafting"
        draft.save(update_fields=["status"])
        logger.exception("Segmentation failed for draft %s", draft_id)
        raise

    # Persist style block on draft
    draft.style_block = result.get("style_block", "")
    draft.status = "review"
    draft.save(update_fields=["style_block", "status", "updated_at"])

    # Create segment rows + text assets
    for scene in result["scenes"]:
        segment, _ = StorySegment.objects.get_or_create(
            draft=draft,
            index=scene["index"],
            defaults={"image_prompt": scene.get("image_prompt", ""), "status": "pending"},
        )
        segment.image_prompt = scene.get("image_prompt", "")
        segment.save(update_fields=["image_prompt", "updated_at"])

        for lang_code, narration_text in scene.get("narration", {}).items():
            SegmentAsset.objects.update_or_create(
                segment=segment,
                asset_type="text",
                language_id=lang_code,
                defaults={
                    "status": "ready",
                    "content": narration_text,
                    "generation_input": {"idea": draft.idea_text, "age_groups": draft.age_groups},
                    "generated_at": timezone.now(),
                },
            )

        segment.recompute_status()

    job.status = "completed"
    job.finished_at = timezone.now()
    job.save(update_fields=["status", "finished_at"])
    logger.info("Segmentation completed for draft %s: %d scenes", draft_id, len(result["scenes"]))


# ---------------------------------------------------------------------------
# Image generation task (Imagen 3)
# ---------------------------------------------------------------------------

@shared_task(bind=True, max_retries=2, name="studio.generate_image")
def generate_image(self, asset_id: str, job_id: str) -> None:
    from apps.studio.models import GenerationJob, SegmentAsset
    from apps.studio.services.imagen_service import ImagenService

    job = GenerationJob.objects.get(pk=job_id)
    job.status = "running"
    job.started_at = timezone.now()
    job.save(update_fields=["status", "started_at"])

    asset = SegmentAsset.objects.select_related("segment__draft").get(pk=asset_id)
    asset.status = "generating"
    asset.save(update_fields=["status"])

    segment = asset.segment
    draft = segment.draft

    full_prompt = f"{draft.style_block}\n\n{segment.image_prompt}".strip()

    try:
        svc = ImagenService()
        image_bytes = svc.generate_image(full_prompt)
    except Exception as exc:
        _fail_asset(asset, job, exc)
        raise self.retry(exc=exc, countdown=10) if self.request.retries < self.max_retries else exc

    # Upload to draft path
    key = f"{settings.STUDIO_DRAFT_PATH_PREFIX}/{draft.pk}/images/scene_{segment.index:02d}.jpg"
    s3 = _s3()
    s3.put_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=key,
        Body=image_bytes,
        ContentType="image/jpeg",
        ACL="public-read",
    )

    asset.status = "ready"
    asset.asset_url = _draft_url(key)
    asset.generation_input = {"prompt": full_prompt}
    asset.generation_cost_usd = Decimal(str(ImagenService.estimate_cost()))
    asset.generated_at = timezone.now()
    asset.error_message = ""
    asset.save(update_fields=[
        "status", "asset_url", "generation_input",
        "generation_cost_usd", "generated_at", "error_message", "updated_at",
    ])

    segment.recompute_status()

    job.status = "completed"
    job.finished_at = timezone.now()
    job.save(update_fields=["status", "finished_at"])
    logger.info("Image generated for segment %s", segment.pk)


# ---------------------------------------------------------------------------
# Audio generation task (ElevenLabs)
# ---------------------------------------------------------------------------

@shared_task(bind=True, max_retries=2, name="studio.generate_audio")
def generate_audio(self, asset_id: str, job_id: str) -> None:
    from apps.studio.models import GenerationJob, SegmentAsset
    from apps.studio.services.elevenlabs_service import ElevenLabsService

    job = GenerationJob.objects.get(pk=job_id)
    job.status = "running"
    job.started_at = timezone.now()
    job.save(update_fields=["status", "started_at"])

    asset = SegmentAsset.objects.select_related("segment__draft", "language").get(pk=asset_id)
    asset.status = "generating"
    asset.save(update_fields=["status"])

    segment = asset.segment
    draft = segment.draft
    lang_code = asset.language_id

    # Fetch narration text from sibling text asset
    text_asset = SegmentAsset.objects.filter(
        segment=segment, asset_type="text", language_id=lang_code
    ).first()
    if not text_asset or not text_asset.content:
        _fail_asset(asset, job, ValueError("No narration text found for this segment/language"))
        return

    narration_text = text_asset.content

    try:
        svc = ElevenLabsService()
        mp3_bytes, duration = svc.generate_audio(narration_text, lang_code)
    except Exception as exc:
        _fail_asset(asset, job, exc)
        raise self.retry(exc=exc, countdown=10) if self.request.retries < self.max_retries else exc

    # Upload to draft path
    key = (
        f"{settings.STUDIO_DRAFT_PATH_PREFIX}/{draft.pk}/"
        f"audio/{lang_code}/scene_{segment.index:02d}.mp3"
    )
    s3 = _s3()
    s3.put_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=key,
        Body=mp3_bytes,
        ContentType="audio/mpeg",
        ACL="public-read",
    )

    asset.status = "ready"
    asset.asset_url = _draft_url(key)
    # Per-scene audio: start=0, end=duration (absolute timing within this file)
    asset.audio_start_sec = 0.0
    asset.audio_end_sec = round(duration, 3)
    asset.generation_input = {"text": narration_text, "language": lang_code}
    asset.generation_cost_usd = Decimal(str(ElevenLabsService.estimate_cost(len(narration_text))))
    asset.generated_at = timezone.now()
    asset.error_message = ""
    asset.save(update_fields=[
        "status", "asset_url", "audio_start_sec", "audio_end_sec",
        "generation_input", "generation_cost_usd", "generated_at", "error_message", "updated_at",
    ])

    segment.recompute_status()

    job.status = "completed"
    job.finished_at = timezone.now()
    job.save(update_fields=["status", "finished_at"])
    logger.info("Audio generated for segment %s lang=%s (%.2fs)", segment.pk, lang_code, duration)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fail_asset(asset, job, exc: Exception) -> None:
    from django.utils import timezone as tz

    asset.status = "failed"
    asset.error_message = str(exc)
    asset.save(update_fields=["status", "error_message", "updated_at"])
    asset.segment.recompute_status()

    job.status = "failed"
    job.finished_at = tz.now()
    job.error_message = str(exc)
    job.save(update_fields=["status", "finished_at", "error_message"])
    logger.exception("Generation failed for asset %s", asset.pk)
