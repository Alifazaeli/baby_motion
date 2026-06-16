"""URL patterns for user and children endpoints."""
from django.urls import path

from .views import AcknowledgeAgeGroupView, ChildDetailView, ChildListCreateView, MeView

urlpatterns = [
    path("me", MeView.as_view(), name="me"),
    path("children", ChildListCreateView.as_view(), name="child-list-create"),
    path("children/<uuid:child_id>", ChildDetailView.as_view(), name="child-detail"),
    path(
        "children/<uuid:child_id>/acknowledge-age-group",
        AcknowledgeAgeGroupView.as_view(),
        name="child-acknowledge-age-group",
    ),
]
