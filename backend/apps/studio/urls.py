"""URL routing for the Content Studio API at /studio/api/."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AnalyticsView,
    SegmentAssetViewSet,
    StoryDraftViewSet,
    StorySegmentViewSet,
    StudioCategoryViewSet,
    StudioLanguageViewSet,
    StudioLoginView,
    UIStringViewSet,
)

router = DefaultRouter()
router.register(r"drafts", StoryDraftViewSet, basename="draft")
router.register(r"segments", StorySegmentViewSet, basename="segment")
router.register(r"assets", SegmentAssetViewSet, basename="asset")
router.register(r"categories", StudioCategoryViewSet, basename="studio-category")
router.register(r"languages", StudioLanguageViewSet, basename="studio-language")
router.register(r"ui-strings", UIStringViewSet, basename="ui-string")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/login/", StudioLoginView.as_view(), name="studio-login"),
    path("analytics/", AnalyticsView.as_view(), name="studio-analytics"),
]
