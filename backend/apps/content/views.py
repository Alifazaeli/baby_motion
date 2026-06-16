"""Views for categories, stories, and UI strings."""
from __future__ import annotations

from django.db.models import Prefetch, QuerySet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import Child
from apps.users.services import compute_age_group

from .models import Category, CategoryTranslation, Story, StoryTranslation, UIString
from .serializers import CategorySerializer, StorySerializer

AGE_GROUP_ORDER = ["12_18m", "18_30m", "30_42m", "42_60m"]


class CategoryListView(APIView):
    """GET /categories — list all categories in the requested language."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        """Return categories with localized names."""
        language = _resolve_language(request)
        categories = Category.objects.all().order_by("display_order")
        translations = {
            t.category_id: t
            for t in CategoryTranslation.objects.filter(language=language)
        }
        for cat in categories:
            t = translations.get(cat.pk)
            cat._translated_name = t.name if t else cat.slug
        return Response(CategorySerializer(categories, many=True).data)


class StoryListView(APIView):
    """GET /stories — catalog filtered to the child's age group and language."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        """Return published stories for a child, optionally including younger age groups."""
        language = _resolve_language(request)
        child_id = request.query_params.get("child_id")
        include_younger = request.query_params.get("include_younger", "false").lower() == "true"
        category_slug = request.query_params.get("category")

        try:
            child = request.user.children.get(pk=child_id)
        except Child.DoesNotExist:
            return Response({"detail": "Child not found."}, status=404)

        age_group = compute_age_group(child.birth_year, child.birth_month)
        groups = _resolve_age_groups(age_group, include_younger)

        qs = Story.objects.filter(status="published", age_group__in=groups)
        if category_slug:
            qs = qs.filter(category__slug=category_slug)

        translations_qs = StoryTranslation.objects.filter(language=language)
        stories = qs.prefetch_related(Prefetch("translations", queryset=translations_qs, to_attr="_translations_list"))

        for story in stories:
            translations = getattr(story, "_translations_list", [])
            story._translation = translations[0] if translations else None

        return Response(StorySerializer(stories, many=True).data)


class StoryDetailView(APIView):
    """GET /stories/{id} — single story with translation."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, story_id: str) -> Response:
        """Return a story with its translation in the requested language."""
        language = _resolve_language(request)
        story = Story.objects.get(pk=story_id, status="published")
        translation = StoryTranslation.objects.filter(story=story, language=language).first()
        story._translation = translation
        return Response(StorySerializer(story).data)


class UIStringView(APIView):
    """GET /i18n/{language} — all UI strings for a language. Public endpoint."""

    permission_classes = [AllowAny]

    def get(self, request: Request, language: str) -> Response:
        """Return a flat dict of key→value for client-side localization."""
        strings = UIString.objects.filter(language=language).values_list("key", "value")
        return Response(dict(strings))


def _resolve_language(request: Request) -> str:
    """Pick content language from query param, then Accept-Language, then 'en'."""
    if lang := request.query_params.get("language"):
        return lang
    accept = request.headers.get("Accept-Language", "")
    if accept:
        return accept.split(",")[0].split("-")[0].strip()
    return "en"


def _resolve_age_groups(current_group: str | None, include_younger: bool) -> list[str]:
    """Return the list of age groups to include in the catalog query."""
    if not current_group or current_group == "60m_plus":
        if include_younger:
            return AGE_GROUP_ORDER
        return [AGE_GROUP_ORDER[-1]]
    idx = AGE_GROUP_ORDER.index(current_group) if current_group in AGE_GROUP_ORDER else -1
    if include_younger:
        return AGE_GROUP_ORDER[: idx + 1]
    return [current_group]
