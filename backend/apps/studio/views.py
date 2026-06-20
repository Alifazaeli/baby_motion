"""Content Studio API views.

All endpoints under /studio/api/ — separately authenticated from public /api/v1/.
Permission: IsStudioUser (super_admin or content_admin roles only).
"""
from __future__ import annotations

import uuid

from django.contrib.auth import authenticate
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from apps.content.models import Category, Language, UIString
from apps.content.serializers import CategorySerializer, LanguageSerializer

from .models import GenerationJob, SegmentAsset, StoryDraft, StorySegment
from .permissions import IsStudioUser
from .serializers import (
    CategoryWriteSerializer,
    GenerationJobSerializer,
    SegmentAssetSerializer,
    StoryDraftCreateSerializer,
    StoryDraftDetailSerializer,
    StoryDraftListSerializer,
    StorySegmentSerializer,
    UIStringSerializer,
)


def _create_job(draft, job_type, provider, segment=None, asset=None):
    return GenerationJob.objects.create(
        id=uuid.uuid4(),
        draft=draft,
        segment=segment,
        asset=asset,
        job_type=job_type,
        external_provider=provider,
        status="queued",
    )


# ── Story Drafts ─────────────────────────────────────────────────────────────

class StoryDraftViewSet(ModelViewSet):
    permission_classes = [IsStudioUser]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        qs = StoryDraft.objects.select_related("category", "created_by").order_by("-created_at")
        s = self.request.query_params.get("status")
        if s:
            qs = qs.filter(status=s)
        ag = self.request.query_params.get("age_group")
        if ag:
            qs = qs.filter(age_group=ag)
        cat = self.request.query_params.get("category")
        if cat:
            qs = qs.filter(category__slug=cat)
        return qs

    def get_serializer_class(self):
        if self.action == "create":
            return StoryDraftCreateSerializer
        if self.action in ("retrieve", "partial_update"):
            return StoryDraftDetailSerializer
        return StoryDraftListSerializer

    def perform_create(self, serializer):
        admin_profile = self.request.user.admin_profile
        serializer.save(created_by=admin_profile)

    # POST /drafts/{id}/segment/ — trigger Claude segmentation
    @action(detail=True, methods=["post"], url_path="segment")
    def segment(self, request, pk=None):
        draft = self.get_object()
        if draft.status not in ("drafting", "review"):
            return Response(
                {"detail": "Segmentation is only available on drafting or review drafts."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        job = _create_job(draft, "segmentation", "claude")
        from .tasks import run_segmentation
        run_segmentation.delay(str(draft.pk), str(job.pk))
        return Response({"job_id": str(job.pk)}, status=status.HTTP_202_ACCEPTED)

    # POST /drafts/{id}/generate-assets/ — fan out image + audio generation
    @action(detail=True, methods=["post"], url_path="generate-assets")
    def generate_assets(self, request, pk=None):
        draft = self.get_object()
        if draft.status not in ("review", "drafting"):
            return Response(
                {"detail": "Asset generation requires draft to be in review or drafting status."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        segments = list(draft.segments.prefetch_related("assets").all())
        if not segments:
            return Response(
                {"detail": "Run segmentation first."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        asset_type = request.data.get("asset_type")  # optional filter: 'image' | 'audio'
        language = request.data.get("language")        # optional filter for audio

        from .tasks import generate_audio, generate_image

        jobs_created = []
        for seg in segments:
            if asset_type in (None, "image"):
                image_asset, _ = SegmentAsset.objects.get_or_create(
                    segment=seg,
                    asset_type="image",
                    language=None,
                    defaults={"status": "pending"},
                )
                if image_asset.status in ("pending", "failed", "stale"):
                    job = _create_job(draft, "image", "imagen3", segment=seg, asset=image_asset)
                    generate_image.delay(str(image_asset.pk), str(job.pk))
                    jobs_created.append(str(job.pk))

            if asset_type in (None, "audio"):
                for lang_code in draft.languages:
                    if language and lang_code != language:
                        continue
                    audio_asset, _ = SegmentAsset.objects.get_or_create(
                        segment=seg,
                        asset_type="audio",
                        language_id=lang_code,
                        defaults={"status": "pending"},
                    )
                    if audio_asset.status in ("pending", "failed", "stale"):
                        job = _create_job(draft, "audio", "elevenlabs", segment=seg, asset=audio_asset)
                        generate_audio.delay(str(audio_asset.pk), str(job.pk))
                        jobs_created.append(str(job.pk))

        return Response({"jobs_queued": len(jobs_created), "job_ids": jobs_created}, status=status.HTTP_202_ACCEPTED)

    # POST /drafts/{id}/publish/ — assemble manifests and publish
    @action(detail=True, methods=["post"], url_path="publish")
    def publish(self, request, pk=None):
        draft = self.get_object()
        if draft.status not in ("review",):
            return Response(
                {"detail": "Only drafts in 'review' status can be published."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Validate all ready
        unready = SegmentAsset.objects.filter(segment__draft=draft).exclude(status="ready")
        if unready.exists():
            bad = list(unready.values("segment__index", "asset_type", "language", "status"))
            return Response({"detail": "Not all assets are ready.", "unready": bad}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from .services.publish_service import publish_draft
            publish_draft(draft)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(StoryDraftDetailSerializer(draft).data, status=status.HTTP_200_OK)

    # GET /drafts/{id}/jobs/
    @action(detail=True, methods=["get"], url_path="jobs")
    def jobs(self, request, pk=None):
        draft = self.get_object()
        jobs = GenerationJob.objects.filter(draft=draft).order_by("-created_at")
        return Response(GenerationJobSerializer(jobs, many=True).data)


# ── Segments ─────────────────────────────────────────────────────────────────

class StorySegmentViewSet(ModelViewSet):
    permission_classes = [IsStudioUser]
    serializer_class = StorySegmentSerializer
    http_method_names = ["get", "patch", "head", "options"]

    def get_queryset(self):
        return StorySegment.objects.prefetch_related("assets__language").order_by("index")

    def partial_update(self, request, *args, **kwargs):
        """Edit image_prompt or (via nested assets) narration text.

        Editing narration text of a segment is handled via SegmentAssetViewSet.
        This endpoint only handles image_prompt edits.
        """
        return super().partial_update(request, *args, **kwargs)

    # POST /segments/{id}/generate-image/
    @action(detail=True, methods=["post"], url_path="generate-image")
    def generate_image(self, request, pk=None):
        segment = self.get_object()
        draft = segment.draft
        image_asset, _ = SegmentAsset.objects.get_or_create(
            segment=segment,
            asset_type="image",
            language=None,
            defaults={"status": "pending"},
        )
        image_asset.status = "pending"
        image_asset.save(update_fields=["status"])

        job = _create_job(draft, "image", "imagen3", segment=segment, asset=image_asset)
        from .tasks import generate_image
        generate_image.delay(str(image_asset.pk), str(job.pk))
        return Response({"job_id": str(job.pk)}, status=status.HTTP_202_ACCEPTED)

    # POST /segments/{id}/generate-audio/
    @action(detail=True, methods=["post"], url_path="generate-audio")
    def generate_audio(self, request, pk=None):
        segment = self.get_object()
        draft = segment.draft
        language = request.data.get("language")
        if not language:
            return Response({"detail": "language is required."}, status=status.HTTP_400_BAD_REQUEST)

        audio_asset, _ = SegmentAsset.objects.get_or_create(
            segment=segment,
            asset_type="audio",
            language_id=language,
            defaults={"status": "pending"},
        )
        audio_asset.status = "pending"
        audio_asset.save(update_fields=["status"])

        job = _create_job(draft, "audio", "elevenlabs", segment=segment, asset=audio_asset)
        from .tasks import generate_audio
        generate_audio.delay(str(audio_asset.pk), str(job.pk))
        return Response({"job_id": str(job.pk)}, status=status.HTTP_202_ACCEPTED)


# ── Segment Assets ───────────────────────────────────────────────────────────

class SegmentAssetViewSet(ModelViewSet):
    permission_classes = [IsStudioUser]
    serializer_class = SegmentAssetSerializer
    http_method_names = ["get", "patch", "head", "options"]

    def get_queryset(self):
        return SegmentAsset.objects.select_related("language").all()

    def perform_update(self, serializer):
        """When narration text changes, mark sibling audio assets as stale (CS-17)."""
        instance = self.get_object()
        old_content = instance.content
        serializer.save()
        instance.refresh_from_db()
        if instance.asset_type == "text" and instance.content != old_content:
            # Stale audio assets for the same segment+language — never auto-regenerate
            SegmentAsset.objects.filter(
                segment=instance.segment,
                asset_type="audio",
                language=instance.language,
            ).update(status="stale")
            instance.segment.recompute_status()

    # POST /assets/{id}/regenerate/
    @action(detail=True, methods=["post"], url_path="regenerate")
    def regenerate(self, request, pk=None):
        asset = self.get_object()
        draft = asset.segment.draft

        asset.status = "pending"
        asset.save(update_fields=["status"])

        if asset.asset_type == "image":
            job = _create_job(draft, "image", "imagen3", segment=asset.segment, asset=asset)
            from .tasks import generate_image
            generate_image.delay(str(asset.pk), str(job.pk))
        elif asset.asset_type == "audio":
            job = _create_job(draft, "audio", "elevenlabs", segment=asset.segment, asset=asset)
            from .tasks import generate_audio
            generate_audio.delay(str(asset.pk), str(job.pk))
        else:
            return Response(
                {"detail": "Text assets cannot be regenerated via this endpoint; edit directly."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"job_id": str(job.pk)}, status=status.HTTP_202_ACCEPTED)


# ── CMS: Categories ──────────────────────────────────────────────────────────

class StudioCategoryViewSet(ModelViewSet):
    permission_classes = [IsStudioUser]
    queryset = Category.objects.prefetch_related("translations").order_by("display_order")

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return CategoryWriteSerializer
        return CategorySerializer


# ── CMS: Languages ────────────────────────────────────────────────────────────

class StudioLanguageViewSet(ModelViewSet):
    permission_classes = [IsStudioUser]
    serializer_class = LanguageSerializer
    queryset = Language.objects.all()
    lookup_field = "code"
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]


# ── CMS: UI Strings ───────────────────────────────────────────────────────────

class UIStringViewSet(ModelViewSet):
    permission_classes = [IsStudioUser]
    serializer_class = UIStringSerializer
    http_method_names = ["get", "patch", "head", "options"]

    def get_queryset(self):
        qs = UIString.objects.select_related("language").order_by("key", "language")
        lang = self.request.query_params.get("language")
        if lang:
            qs = qs.filter(language_id=lang)
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(key__icontains=q)
        return qs


# ── Analytics (read-only port of AP-4) ───────────────────────────────────────

class AnalyticsView(APIView):
    permission_classes = [IsStudioUser]

    def get(self, request):
        from apps.analytics.models import ViewingSession
        from django.db.models import Count

        top_stories = (
            ViewingSession.objects.values("story__slug")
            .annotate(views=Count("id"))
            .order_by("-views")[:10]
        )
        return Response({"top_stories": list(top_stories)})


# ── Studio login (email + password) ──────────────────────────────────────────

class StudioLoginView(APIView):
    """Authenticate a Django admin superuser with email + password and return JWT tokens.

    Accepts staff users (is_staff=True) who are either Django superusers or have an
    AdminUser row with a studio-allowed role (super_admin or content_admin).
    App parents who signed up via Google OAuth cannot log in here.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email", "").strip().lower()
        password = request.data.get("password", "")

        if not email or not password:
            return Response(
                {"detail": "email and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, username=email, password=password)
        if user is None:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {"detail": "Account is disabled."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Allow Django superusers unconditionally; otherwise require a studio role.
        allowed = user.is_superuser
        if not allowed:
            try:
                allowed = user.admin_profile.role in ("super_admin", "content_admin")
            except Exception:
                allowed = False

        if not allowed:
            return Response(
                {"detail": "Your account does not have Content Studio access."},
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "email": user.email,
                "is_superuser": user.is_superuser,
                "role": getattr(getattr(user, "admin_profile", None), "role", "super_admin" if user.is_superuser else None),
            }
        )
