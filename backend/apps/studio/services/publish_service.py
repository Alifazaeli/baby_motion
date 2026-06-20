"""Publish service: assembles a manifest per language and upserts Story + StoryTranslation.

On publish:
1. Validates all segment assets are `ready` (none stale/failed/pending).
2. Per language: promotes draft asset files from drafts/{id}/... to production paths
   stories/{slug}/images/ and stories/{slug}/audio/{lang}/.
3. Builds the manifest JSON matching the existing client contract.
4. Uploads manifest to stories/{slug}/manifests/{lang}.json.
5. Upserts Story + StoryTranslation rows.
6. Updates StoryDraft.status → 'published' and links StoryDraft.linked_story.

Zero changes to the client API contract (AC-3).
"""
from __future__ import annotations

import json
import logging
import re
import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

if TYPE_CHECKING:
    from apps.studio.models import StoryDraft

logger = logging.getLogger(__name__)


def _s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        region_name=settings.AWS_S3_REGION_NAME,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )


def _copy_to_production(s3, draft_url: str, production_key: str, content_type: str) -> str:
    """Copy a draft file to the production path and return the public CDN URL."""
    bucket = settings.AWS_STORAGE_BUCKET_NAME
    # draft_url is like https://.../drafts/...  — extract S3 key
    if draft_url.startswith("http"):
        # Strip scheme+host to get key
        path_start = draft_url.index("/", 8)  # skip https://
        slash_idx = draft_url.index("/", path_start + 1)
        draft_key = draft_url[slash_idx + 1:]
    else:
        draft_key = draft_url.lstrip("/")

    s3.copy_object(
        Bucket=bucket,
        CopySource={"Bucket": bucket, "Key": draft_key},
        Key=production_key,
        ACL="public-read",
        ContentType=content_type,
        MetadataDirective="REPLACE",
    )

    cdn_domain = settings.AWS_S3_CUSTOM_DOMAIN
    if cdn_domain:
        return f"https://{cdn_domain}/{production_key}"
    return f"{settings.AWS_S3_ENDPOINT_URL}/{bucket}/{production_key}"


def _upload_json(s3, key: str, data: dict) -> str:
    """Upload a JSON manifest to S3 and return its public URL."""
    bucket = settings.AWS_STORAGE_BUCKET_NAME
    body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=body,
        ContentType="application/json",
        ACL="public-read",
    )
    cdn_domain = settings.AWS_S3_CUSTOM_DOMAIN
    if cdn_domain:
        return f"https://{cdn_domain}/{key}"
    return f"{settings.AWS_S3_ENDPOINT_URL}/{bucket}/{key}"


def publish_draft(draft: "StoryDraft") -> None:
    """Publish a StoryDraft: promote assets, build manifests, upsert Story rows.

    Raises ValueError if any segment asset is not ready.
    Must be called inside a DB transaction (wraps itself if needed).
    """
    from apps.content.models import Story, StoryTranslation
    from apps.studio.models import SegmentAsset, StorySegment

    # 1. Validate all assets are ready
    unready = SegmentAsset.objects.filter(
        segment__draft=draft
    ).exclude(status="ready")
    if unready.exists():
        bad = list(unready.values("segment__index", "asset_type", "language", "status"))
        raise ValueError(f"Cannot publish: some assets are not ready: {bad}")

    segments = list(
        StorySegment.objects.filter(draft=draft).prefetch_related("assets__language").order_by("index")
    )
    if not segments:
        raise ValueError("Cannot publish: draft has no segments")

    s3 = _s3_client()
    slug = _make_slug(draft)

    with transaction.atomic():
        # 2+3. Per language: promote assets + build manifest
        for lang_code in draft.languages:
            image_urls: dict[int, str] = {}
            audio_urls: dict[int, str] = {}
            audio_durations: dict[int, tuple[float, float]] = {}

            for seg in segments:
                # Promote image (language-neutral, done once per segment)
                if lang_code == draft.languages[0]:
                    image_asset = seg.assets.filter(asset_type="image").first()
                    if image_asset and image_asset.asset_url:
                        prod_key = f"stories/{slug}/images/scene_{seg.index:02d}.jpg"
                        prod_url = _copy_to_production(s3, image_asset.asset_url, prod_key, "image/jpeg")
                        image_urls[seg.index] = prod_url
                    else:
                        image_urls[seg.index] = ""
                else:
                    # Image already promoted on first language pass
                    image_asset = seg.assets.filter(asset_type="image").first()
                    image_urls[seg.index] = image_asset.asset_url if image_asset else ""

                # Promote audio per language
                audio_asset = seg.assets.filter(asset_type="audio", language_id=lang_code).first()
                if audio_asset and audio_asset.asset_url:
                    prod_key = f"stories/{slug}/audio/{lang_code}/scene_{seg.index:02d}.mp3"
                    prod_url = _copy_to_production(s3, audio_asset.asset_url, prod_key, "audio/mpeg")
                    audio_urls[seg.index] = prod_url
                    audio_durations[seg.index] = (
                        audio_asset.audio_start_sec or 0.0,
                        audio_asset.audio_end_sec or 0.0,
                    )
                else:
                    audio_urls[seg.index] = ""
                    audio_durations[seg.index] = (0.0, 0.0)

            # Recompute image_urls for non-first languages using production path convention
            if lang_code != draft.languages[0]:
                for seg in segments:
                    image_urls[seg.index] = (
                        f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/"
                        f"stories/{slug}/images/scene_{seg.index:02d}.jpg"
                        if settings.AWS_S3_CUSTOM_DOMAIN
                        else (
                            f"{settings.AWS_S3_ENDPOINT_URL}/{settings.AWS_STORAGE_BUCKET_NAME}/"
                            f"stories/{slug}/images/scene_{seg.index:02d}.jpg"
                        )
                    )

            # Compute cumulative audio start/end from per-scene durations
            offset = 0.0
            scene_timings: dict[int, tuple[float, float]] = {}
            for seg in segments:
                start, end = audio_durations[seg.index]
                duration = end - start if end > start else (end or 0.0)
                if duration <= 0:
                    # Use audio_end_sec directly if start/end already in absolute form
                    duration = audio_durations[seg.index][1]
                scene_timings[seg.index] = (offset, offset + duration)
                offset += duration

            total_duration = offset

            # Gather narration text per scene
            narration_by_scene: dict[int, str] = {}
            for seg in segments:
                text_asset = seg.assets.filter(asset_type="text", language_id=lang_code).first()
                narration_by_scene[seg.index] = text_asset.content if text_asset else ""

            manifest = {
                "story_id": str(draft.linked_story_id) if draft.linked_story_id else None,
                "slug": slug,
                "language": lang_code,
                "title": draft.title,
                "duration_seconds": round(total_duration, 2),
                "audio_url": "",  # per-scene files; concatenation is handled by player via scenes
                "scenes": [
                    {
                        "index": seg.index,
                        "image_url": image_urls.get(seg.index, ""),
                        "text": narration_by_scene.get(seg.index, ""),
                        "audio_url": audio_urls.get(seg.index, ""),
                        "audio_start_sec": round(scene_timings[seg.index][0], 3),
                        "audio_end_sec": round(scene_timings[seg.index][1], 3),
                    }
                    for seg in segments
                ],
            }

            manifest_key = f"stories/{slug}/manifests/{lang_code}.json"
            manifest_url = _upload_json(s3, manifest_key, manifest)

            # 5. Upsert Story + StoryTranslation
            story, _ = Story.objects.update_or_create(
                slug=slug,
                defaults={
                    "category_id": draft.category_id,
                    "age_group": draft.age_groups[0] if draft.age_groups else "",
                    "duration_seconds": int(total_duration),
                    "status": "published",
                    "published_at": timezone.now(),
                },
            )

            # Retrieve per-language title from first text asset of first segment if available
            lang_title = draft.title
            first_text = (
                segments[0].assets.filter(asset_type="text", language_id=lang_code).first()
                if segments
                else None
            )

            StoryTranslation.objects.update_or_create(
                story=story,
                language_id=lang_code,
                defaults={
                    "title": lang_title,
                    "description": "",
                    "manifest_url": manifest_url,
                },
            )

            # Back-fill manifest story_id now we have the story.pk
            manifest["story_id"] = str(story.pk)
            _upload_json(s3, manifest_key, manifest)

        # 6. Link draft to story and mark published
        draft.linked_story = story
        draft.status = "published"
        draft.save(update_fields=["linked_story", "status", "updated_at"])

    logger.info("Published draft %s as story slug=%s", draft.pk, slug)


def _make_slug(draft: "StoryDraft") -> str:
    """Generate a URL-safe slug from draft title or idea text."""
    base = draft.title or draft.idea_text[:60]
    slug = slugify(base, allow_unicode=False)
    # Trim and ensure uniqueness suffix if linked story already exists
    slug = slug[:80] or f"story-{str(draft.pk)[:8]}"
    if not draft.linked_story_id:
        return slug
    return draft.linked_story.slug
