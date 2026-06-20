"""Permission classes for the Content Studio API.

Only `super_admin` and `content_admin` roles may access the studio.
Enforced at view level (CS-9); the `translator` and `analyst` roles are excluded.
"""
from rest_framework.permissions import BasePermission


class IsStudioUser(BasePermission):
    """Allow access only to AdminUser rows with super_admin or content_admin roles."""

    ALLOWED_ROLES = frozenset({"super_admin", "content_admin"})

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        try:
            return request.user.admin_profile.role in self.ALLOWED_ROLES
        except Exception:
            return False
