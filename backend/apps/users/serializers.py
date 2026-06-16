"""Serializers for User and Child resources."""
from __future__ import annotations

from rest_framework import serializers

from .models import Child, User
from .services import (
    compute_age_group,
    compute_age_in_months,
    compute_days_to_next_age_group,
    compute_next_age_group,
    validate_birth_date,
)


class UserSerializer(serializers.ModelSerializer):
    """Read-only serializer for the authenticated user."""

    class Meta:
        model = User
        fields = ["id", "email", "display_name", "preferred_language", "plan"]
        read_only_fields = fields


class ChildSerializer(serializers.ModelSerializer):
    """Serializer for Child with all computed age fields included in output."""

    age_in_months = serializers.SerializerMethodField()
    age_group = serializers.SerializerMethodField()
    next_age_group = serializers.SerializerMethodField()
    days_to_next_age_group = serializers.SerializerMethodField()
    has_pending_age_group_transition = serializers.SerializerMethodField()

    class Meta:
        model = Child
        fields = [
            "id",
            "name",
            "birth_year",
            "birth_month",
            "language",
            "age_in_months",
            "age_group",
            "next_age_group",
            "days_to_next_age_group",
            "has_pending_age_group_transition",
        ]
        read_only_fields = [
            "id",
            "age_in_months",
            "age_group",
            "next_age_group",
            "days_to_next_age_group",
            "has_pending_age_group_transition",
        ]

    def get_age_in_months(self, obj: Child) -> int:
        """Compute age in whole months as of today."""
        return compute_age_in_months(obj.birth_year, obj.birth_month)

    def get_age_group(self, obj: Child) -> str | None:
        """Compute current age group — never read from DB."""
        return compute_age_group(obj.birth_year, obj.birth_month)

    def get_next_age_group(self, obj: Child) -> str | None:
        """Compute the next age group the child will enter."""
        return compute_next_age_group(self.get_age_group(obj))

    def get_days_to_next_age_group(self, obj: Child) -> int | None:
        """Compute days until the next age group transition."""
        return compute_days_to_next_age_group(obj.birth_year, obj.birth_month)

    def get_has_pending_age_group_transition(self, obj: Child) -> bool:
        """True when age_group differs from last_seen_age_group (banner should show)."""
        return self.get_age_group(obj) != obj.last_seen_age_group

    def validate(self, attrs: dict) -> dict:
        """Run birth date validation across year + month together."""
        birth_year = attrs.get("birth_year", getattr(self.instance, "birth_year", None))
        birth_month = attrs.get("birth_month", getattr(self.instance, "birth_month", None))
        if birth_year and birth_month:
            validate_birth_date(birth_year, birth_month)
            # Reset last_seen_age_group on birth date edit so the transition banner re-fires.
            if self.instance and (
                attrs.get("birth_year") != self.instance.birth_year
                or attrs.get("birth_month") != self.instance.birth_month
            ):
                attrs["last_seen_age_group"] = None
        return attrs


class MeSerializer(serializers.Serializer):
    """Response shape for GET /me."""

    user = UserSerializer()
    children = ChildSerializer(many=True)
