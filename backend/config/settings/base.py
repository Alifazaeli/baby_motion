"""Base Django settings shared across all environments."""
from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "corsheaders",
    "simple_history",
    "storages",
    # Local
    "apps.users",
    "apps.authentication",
    "apps.content",
    "apps.analytics",
    "apps.studio",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {
    "default": env.db("DATABASE_URL", default="postgres://postgres:postgres@localhost:5432/baby_motion")
}

AUTH_USER_MODEL = "users.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
APPEND_SLASH = False

# DRF
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}

# JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=env.int("JWT_ACCESS_TOKEN_LIFETIME_MINUTES", default=60)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env.int("JWT_REFRESH_TOKEN_LIFETIME_DAYS", default=30)),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# Google OAuth
GOOGLE_CLIENT_ID = env("GOOGLE_CLIENT_ID")

# CORS
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=["http://localhost:3000"])
CORS_ALLOW_CREDENTIALS = True

# Arvan Cloud (S3-compatible)
AWS_S3_ENDPOINT_URL = "https://s3.ir-thr-at1.arvanstorage.ir"
AWS_S3_REGION_NAME = "ir-thr-at1"
AWS_ACCESS_KEY_ID = env("ARVAN_ACCESS_KEY", default="")
AWS_SECRET_ACCESS_KEY = env("ARVAN_SECRET_KEY", default="")
AWS_STORAGE_BUCKET_NAME = env("ARVAN_BUCKET", default="storytelling-prod")
AWS_S3_CUSTOM_DOMAIN = env("ARVAN_CDN_DOMAIN", default="")
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = "public-read"
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

# drf-spectacular
SPECTACULAR_SETTINGS = {
    "TITLE": "BabyMotion API",
    "DESCRIPTION": "AI Storytelling App for Toddlers",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# Celery
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_TASK_TRACK_STARTED = True

# AI service credentials
ANTHROPIC_API_KEY = env("ANTHROPIC_API_KEY", default="")
ELEVENLABS_API_KEY = env("ELEVENLABS_API_KEY", default="")

# ElevenLabs voice IDs per language (fixed per language for v1 — see OD-7)
ELEVENLABS_VOICES = {
    "en": env("ELEVENLABS_VOICE_EN", default="EXAVITQu4vr4xnSDxMaL"),   # default: Bella
    "fa": env("ELEVENLABS_VOICE_FA", default="pNInz6obpgDQGcFmaJgB"),   # default: Adam (multilingual)
}

# Google Vertex AI for Imagen 3
GOOGLE_CLOUD_PROJECT = env("GOOGLE_CLOUD_PROJECT", default="")
GOOGLE_CLOUD_LOCATION = env("GOOGLE_CLOUD_LOCATION", default="us-central1")
GOOGLE_APPLICATION_CREDENTIALS = env("GOOGLE_APPLICATION_CREDENTIALS", default="")

# Content Studio draft storage prefix (Arvan Cloud)
STUDIO_DRAFT_PATH_PREFIX = "drafts"
