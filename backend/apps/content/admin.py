"""Django Admin for content management — stories, categories, UI strings (AP-1 to AP-6)."""
from django.contrib import admin
from django.utils import timezone

from apps.users.models import AdminUser

from .models import Category, CategoryTranslation, Language, Story, StoryTranslation, UIString


class RequireRoleMixin:
    """Restrict access to specified admin roles (AP-6)."""

    allowed_roles: list[str] = ["super_admin", "content_admin"]

    def has_module_perms(self, request, app_label: str) -> bool:
        return self._has_role(request)

    def has_view_permission(self, request, obj=None) -> bool:
        return self._has_role(request)

    def has_change_permission(self, request, obj=None) -> bool:
        return self._has_role(request)

    def has_add_permission(self, request) -> bool:
        return self._has_role(request)

    def has_delete_permission(self, request, obj=None) -> bool:
        return self._has_role(request)

    def _has_role(self, request) -> bool:
        if request.user.is_superuser:
            return True
        try:
            return request.user.admin_profile.role in self.allowed_roles
        except AdminUser.DoesNotExist:
            return False


class StoryTranslationInline(admin.TabularInline):
    """Inline translation rows per story (AP-2)."""

    model = StoryTranslation
    extra = 0
    fields = ["language", "title", "description", "manifest_url"]
    readonly_fields = ["language"]


class CategoryTranslationInline(admin.TabularInline):
    """Inline translation rows per category."""

    model = CategoryTranslation
    extra = 0
    fields = ["language", "name"]


@admin.register(Story)
class StoryAdmin(RequireRoleMixin, admin.ModelAdmin):
    """Story management with publish workflow (AP-1, AP-5)."""

    list_display = ["slug", "age_group", "category", "status", "published_at", "translation_coverage"]
    list_filter = ["status", "age_group", "category"]
    search_fields = ["slug"]
    readonly_fields = ["id", "published_at", "created_at", "updated_at"]
    inlines = [StoryTranslationInline]
    actions = ["publish_stories", "archive_stories", "move_to_review"]

    @admin.display(description="Translations")
    def translation_coverage(self, obj: Story) -> str:
        """Show how many languages have a translation for this story."""
        count = obj.translations.count()
        active = Language.objects.filter(is_active=True).count()
        return f"{count}/{active}"

    @admin.action(description="Publish selected stories")
    def publish_stories(self, request, queryset):
        """Set status=published and stamp published_at."""
        queryset.update(status="published", published_at=timezone.now())

    @admin.action(description="Archive selected stories")
    def archive_stories(self, request, queryset):
        queryset.update(status="archived")

    @admin.action(description="Move to review")
    def move_to_review(self, request, queryset):
        queryset.update(status="review")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Category management."""

    list_display = ["slug", "display_order"]
    inlines = [CategoryTranslationInline]


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    """Language registry — adding a row here enables a new content language."""

    list_display = ["code", "display_name", "is_rtl", "is_active"]
    list_editable = ["is_active"]


@admin.register(UIString)
class UIStringAdmin(RequireRoleMixin, admin.ModelAdmin):
    """UI string translator interface (AP-3).

    allowed_roles includes 'translator' so translators can edit strings
    without accessing story content.
    """

    allowed_roles = ["super_admin", "content_admin", "translator"]
    list_display = ["key", "language", "value_preview"]
    list_filter = ["language"]
    search_fields = ["key", "value"]
    list_per_page = 50

    @admin.display(description="Value")
    def value_preview(self, obj: UIString) -> str:
        return obj.value[:80]
