"""Celery application for BabyMotion async generation jobs."""
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("baby_motion")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
