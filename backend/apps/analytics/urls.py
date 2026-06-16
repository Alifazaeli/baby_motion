"""URL patterns for analytics endpoints."""
from django.urls import path

from .views import (
    AbandonSessionView,
    AdminAnalyticsOverviewView,
    AdminAnalyticsStoriesView,
    CompleteSessionView,
    StartStoryView,
)

urlpatterns = [
    path("stories/<uuid:story_id>/start", StartStoryView.as_view(), name="story-start"),
    path("sessions/<uuid:session_id>/complete", CompleteSessionView.as_view(), name="session-complete"),
    path("sessions/<uuid:session_id>/abandon", AbandonSessionView.as_view(), name="session-abandon"),
    path("admin/analytics/overview", AdminAnalyticsOverviewView.as_view(), name="admin-analytics-overview"),
    path("admin/analytics/stories", AdminAnalyticsStoriesView.as_view(), name="admin-analytics-stories"),
]
