"""Django Admin configuration for User, Child, and AdminUser."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import AdminUser, Child, User
from .services import compute_age_group, compute_age_in_months


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin for the custom User model.

    Superusers log in with email + password.
    App users (Google SSO) have unusable passwords and cannot log into admin.
    """

    list_display = ["email", "display_name", "google_sub", "preferred_language", "plan", "is_staff", "created_at"]
    list_filter = ["plan", "preferred_language", "is_staff", "is_active"]
    search_fields = ["email", "display_name", "google_sub"]
    ordering = ["-created_at"]
    readonly_fields = ["id", "created_at", "updated_at", "last_login_at"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Profile", {"fields": ("id", "google_sub", "display_name")}),
        ("Preferences", {"fields": ("preferred_language", "plan")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Timestamps", {"fields": ("last_login_at", "created_at", "updated_at")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "is_staff", "is_superuser"),
        }),
    )


class AgeGroupDisplay:
    """Mixin that adds a computed age_group column to the child list."""

    @admin.display(description="Age Group")
    def age_group_display(self, obj: Child) -> str:
        """Show the computed age group (not stored in DB)."""
        group = compute_age_group(obj.birth_year, obj.birth_month)
        months = compute_age_in_months(obj.birth_year, obj.birth_month)
        return f"{group or 'N/A'} ({months}mo)"


@admin.register(Child)
class ChildAdmin(AgeGroupDisplay, admin.ModelAdmin):
    """Admin for Child profiles."""

    list_display = ["name", "user", "birth_year", "birth_month", "age_group_display", "language"]
    list_filter = ["language"]
    search_fields = ["name", "user__email"]
    readonly_fields = ["id", "age_group_display", "created_at", "updated_at"]


@admin.register(AdminUser)
class AdminUserAdmin(admin.ModelAdmin):
    """Admin for role assignments (AP-6)."""

    list_display = ["user", "role", "created_at"]
    list_filter = ["role"]
    search_fields = ["user__email"]
    readonly_fields = ["id", "created_at", "updated_at"]
