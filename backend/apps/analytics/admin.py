"""Django Admin for analytics (read-only for analysts)."""
from django.contrib import admin

from .models import ViewingSession


@admin.register(ViewingSession)
class ViewingSessionAdmin(admin.ModelAdmin):
    """Read-only analytics view for sessions."""

    list_display = ["child", "story", "language", "started_at", "completed", "scenes_watched"]
    list_filter = ["completed", "language"]
    search_fields = ["child__name", "story__slug"]
    readonly_fields = [f.name for f in ViewingSession._meta.get_fields() if hasattr(f, "name")]

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return request.user.is_superuser
