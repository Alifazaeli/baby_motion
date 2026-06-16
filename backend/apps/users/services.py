"""Age group computation and birth date validation.

Age group is NEVER stored in the database — it is computed on every request.
All functions here are pure (accept an optional `today` arg for testability).
"""
from __future__ import annotations

from datetime import date

from django.core.exceptions import ValidationError
from django.utils import timezone


AGE_GROUP_BOUNDARIES: list[tuple[int, str]] = [
    (18, "12_18m"),
    (30, "18_30m"),
    (42, "30_42m"),
    (60, "42_60m"),
]


def compute_age_in_months(birth_year: int, birth_month: int, today: date | None = None) -> int:
    """Return the child's age in whole months as of `today`."""
    today = today or timezone.now().date()
    return (today.year - birth_year) * 12 + (today.month - birth_month)


def compute_age_group(birth_year: int, birth_month: int, today: date | None = None) -> str | None:
    """Return the age group string for a child, or None if outside app range.

    Returns:
        '12_18m' | '18_30m' | '30_42m' | '42_60m' | '60m_plus' | None
    """
    months = compute_age_in_months(birth_year, birth_month, today)
    if months < 12:
        return None
    for threshold, group in AGE_GROUP_BOUNDARIES:
        if months < threshold:
            return group
    return "60m_plus"


def compute_next_age_group(current_group: str | None) -> str | None:
    """Return the next age group after `current_group`, or None if graduated/too young."""
    progression = ["12_18m", "18_30m", "30_42m", "42_60m"]
    if current_group not in progression:
        return None
    idx = progression.index(current_group)
    return progression[idx + 1] if idx + 1 < len(progression) else "60m_plus"


def compute_days_to_next_age_group(
    birth_year: int, birth_month: int, today: date | None = None
) -> int | None:
    """Return days until child enters the next age group, or None if graduated.

    Used for the upcoming-transition hint (FR-A13 / days_to_next_age_group field).
    """
    today = today or timezone.now().date()
    months = compute_age_in_months(birth_year, birth_month, today)

    next_threshold = None
    for threshold, _ in AGE_GROUP_BOUNDARIES:
        if months < threshold:
            next_threshold = threshold
            break

    if next_threshold is None:
        return None

    target_month = birth_month + next_threshold
    target_year = birth_year + (target_month - 1) // 12
    target_month = ((target_month - 1) % 12) + 1
    target_date = date(target_year, target_month, 1)
    return max(0, (target_date - today).days)


def validate_birth_date(birth_year: int, birth_month: int) -> None:
    """Validate that a birth date is within acceptable bounds for the app.

    Raises:
        ValidationError: if the date is in the future, too old (>72 months),
            or before the minimum supported age (6 months).
    """
    today = timezone.now().date()
    birth = date(birth_year, birth_month, 1)
    months_old = compute_age_in_months(birth_year, birth_month, today)

    if birth > today.replace(day=1):
        raise ValidationError("Birth date can't be in the future.")
    if months_old > 72:
        raise ValidationError(
            "This app is designed for children under 5. "
            "We'd love to have you back with a younger child!"
        )
    if months_old < 6:
        raise ValidationError(
            "Our youngest content is for 12 months and older. "
            "Please come back when your baby is a bit older."
        )
