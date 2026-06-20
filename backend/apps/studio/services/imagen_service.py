"""Imagen 3 image generation via Google Vertex AI REST API.

Uses google-auth to sign requests — no google-cloud-aiplatform SDK dependency.
Credentials are picked up from GOOGLE_APPLICATION_CREDENTIALS env var or
Application Default Credentials (ADC).

Imagen 3 API reference:
  POST https://{location}-aiplatform.googleapis.com/v1/projects/{project}/locations/{location}/
       publishers/google/models/imagen-3.0-generate-001:predict
"""
from __future__ import annotations

import base64
import io
import logging
import os
import uuid

import google.auth
import google.auth.transport.requests
import requests as http_requests
from django.conf import settings

logger = logging.getLogger(__name__)

_IMAGEN_MODEL = "imagen-3.0-generate-001"


class ImagenService:
    def __init__(self) -> None:
        # google.auth picks up ADC or GOOGLE_APPLICATION_CREDENTIALS
        if settings.GOOGLE_APPLICATION_CREDENTIALS:
            os.environ.setdefault(
                "GOOGLE_APPLICATION_CREDENTIALS", settings.GOOGLE_APPLICATION_CREDENTIALS
            )
        self._project = settings.GOOGLE_CLOUD_PROJECT
        self._location = settings.GOOGLE_CLOUD_LOCATION

    def _get_access_token(self) -> str:
        credentials, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        return credentials.token

    def generate_image(self, full_prompt: str) -> bytes:
        """Call Imagen 3 and return raw JPEG bytes.

        full_prompt should be style_block + " " + scene-specific image_prompt,
        assembled by the caller before invoking this method.
        """
        url = (
            f"https://{self._location}-aiplatform.googleapis.com/v1/"
            f"projects/{self._project}/locations/{self._location}/"
            f"publishers/google/models/{_IMAGEN_MODEL}:predict"
        )
        payload = {
            "instances": [{"prompt": full_prompt}],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": "4:3",
                "safetyFilterLevel": "block_some",
                "personGeneration": "dont_allow",
            },
        }
        token = self._get_access_token()
        resp = http_requests.post(
            url,
            json=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            timeout=90,
        )
        resp.raise_for_status()
        data = resp.json()
        b64 = data["predictions"][0]["bytesBase64Encoded"]
        return base64.b64decode(b64)

    @staticmethod
    def estimate_cost() -> float:
        """Rough USD cost per Imagen 3 image (~$0.04 per image as of launch pricing)."""
        return 0.04
