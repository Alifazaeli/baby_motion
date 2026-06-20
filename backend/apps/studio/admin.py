"""Django Admin registrations for studio models — for superuser inspection only.

Per G4: the Content Studio frontend (not Django Admin) is the content-management surface.
These registrations exist for debugging and data inspection by technical superusers only.
"""
from django.contrib import admin

from .models import GenerationJob, SegmentAsset, StoryDraft, StorySegment


class StorySegmentInline(admin.TabularInline):
    model = StorySegment
    fields = ("index", "image_prompt", "status")
    readonly_fields = ("status",)
    extra = 0


@admin.register(StoryDraft)
class StoryDraftAdmin(admin.ModelAdmin):
    list_display = ("title", "age_group", "status", "category", "created_by", "created_at")
    list_filter = ("status", "age_group")
    readonly_fields = ("id", "created_at", "updated_at", "linked_story")
    inlines = [StorySegmentInline]


class SegmentAssetInline(admin.TabularInline):
    model = SegmentAsset
    fields = ("asset_type", "language", "status", "generation_cost_usd")
    readonly_fields = ("status", "generation_cost_usd")
    extra = 0


@admin.register(StorySegment)
class StorySegmentAdmin(admin.ModelAdmin):
    list_display = ("draft", "index", "status")
    inlines = [SegmentAssetInline]


@admin.register(GenerationJob)
class GenerationJobAdmin(admin.ModelAdmin):
    list_display = ("job_type", "external_provider", "status", "draft", "started_at", "finished_at")
    list_filter = ("status", "job_type", "external_provider")
    readonly_fields = ("id", "created_at")
