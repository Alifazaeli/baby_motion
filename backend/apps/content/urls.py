"""URL patterns for content endpoints."""
from django.urls import path

from .views import CategoryListView, StoryDetailView, StoryListView, UIStringView

urlpatterns = [
    path("categories", CategoryListView.as_view(), name="category-list"),
    path("stories", StoryListView.as_view(), name="story-list"),
    path("stories/<uuid:story_id>", StoryDetailView.as_view(), name="story-detail"),
    path("i18n/<str:language>", UIStringView.as_view(), name="ui-strings"),
]
