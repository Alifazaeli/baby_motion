"""User and Child models.

Two distinct auth paths:
- App users (parents):  authenticated via Google OAuth → JWT.  No Django password.
- Admin superusers:     email + password → Django Admin only.  No google_sub.

Age group is NEVER stored — always computed at runtime from birth_year + birth_month.
See apps.users.services for the computation logic.
"""
import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """Custom manager supporting both Google SSO users and password-based admin superusers."""

    def create_user(
        self,
        email: str,
        password: str | None = None,
        **extra_fields,
    ) -> "User":
        """Create an app user or superuser.

        Pass password=None for Google SSO users (sets unusable password).
        Pass a real password for Django Admin superusers.
        """
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # None → unusable; real string → hashed
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str, **extra_fields) -> "User":
        """Create a Django Admin superuser with email + password.

        These accounts have no google_sub and cannot use the app's Google SSO flow.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if not password:
            raise ValueError("Superusers must have a password")
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Unified user model for both app parents (Google SSO) and admin superusers.

    - App parents:     google_sub set, password unusable, is_staff=False
    - Admin superusers: google_sub=None, password set, is_staff=True
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    google_sub = models.TextField(unique=True, null=True, blank=True, default=None)
    email = models.EmailField(unique=True)
    display_name = models.TextField(blank=True, default="")
    preferred_language = models.CharField(max_length=10, default="en")
    plan = models.CharField(max_length=20, default="free")
    last_login_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users"

    def __str__(self) -> str:
        return self.email


class Child(models.Model):
    """A child profile linked to a parent User.

    birth_year + birth_month are the sole source of truth for age.
    last_seen_age_group tracks which age group the parent last acknowledged,
    enabling the one-time transition banner (FR-A11).
    """

    AGE_GROUP_CHOICES = [
        ("12_18m", "12–18 months"),
        ("18_30m", "18–30 months"),
        ("30_42m", "30–42 months"),
        ("42_60m", "42–60 months"),
        ("60m_plus", "60+ months (graduated)"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="children")
    name = models.CharField(max_length=100)
    birth_year = models.IntegerField()
    birth_month = models.IntegerField()
    language = models.CharField(max_length=10)
    last_seen_age_group = models.CharField(
        max_length=20,
        choices=AGE_GROUP_CHOICES,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "children"
        indexes = [models.Index(fields=["user"])]
        constraints = [
            models.CheckConstraint(
                check=models.Q(birth_year__gte=2019, birth_year__lte=2030),
                name="children_birth_year_range",
            ),
            models.CheckConstraint(
                check=models.Q(birth_month__gte=1, birth_month__lte=12),
                name="children_birth_month_range",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} (user={self.user_id})"


class AdminUser(models.Model):
    """Maps a User to an admin role for the content management panel (AP-6)."""

    ROLE_CHOICES = [
        ("super_admin", "Super Admin"),
        ("content_admin", "Content Admin"),
        ("translator", "Translator"),
        ("analyst", "Analyst"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="admin_profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "admin_users"

    def __str__(self) -> str:
        return f"{self.user} — {self.role}"
