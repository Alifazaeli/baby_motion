"""ElevenLabs text-to-speech service.

Per OD-2: one ElevenLabs call per scene (not one call for the whole story).
This keeps per-scene audio files independent and makes individual regeneration trivial.
Per OD-7: one fixed voice per language, configurable via settings.ELEVENLABS_VOICES.

Audio duration is derived from the returned MP3 bytes using mutagen for precision,
falling back to a simple heuristic if mutagen is not installed.
"""
from __future__ import annotations

import io
import logging

import requests as http_requests
from django.conf import settings

logger = logging.getLogger(__name__)

_API_BASE = "https://api.elevenlabs.io/v1"


def _mp3_duration_seconds(mp3_bytes: bytes) -> float:
    """Return audio duration from MP3 bytes.

    Uses mutagen if available; otherwise estimates from file size (rough).
    """
    try:
        from mutagen.mp3 import MP3

        audio = MP3(io.BytesIO(mp3_bytes))
        return float(audio.info.length)
    except Exception:
        # ~128 kbps CBR fallback
        return len(mp3_bytes) / (128 * 1024 / 8)


class ElevenLabsService:
    def __init__(self) -> None:
        self._api_key = settings.ELEVENLABS_API_KEY
        self._voices: dict[str, str] = settings.ELEVENLABS_VOICES

    def _voice_for_language(self, language: str) -> str:
        voice_id = self._voices.get(language)
        if not voice_id:
            raise ValueError(f"No ElevenLabs voice configured for language '{language}'")
        return voice_id

    def generate_audio(self, text: str, language: str) -> tuple[bytes, float]:
        """Generate TTS audio for a single scene narration.

        Returns (mp3_bytes, duration_seconds).
        The caller is responsible for uploading the bytes to storage.
        """
        voice_id = self._voice_for_language(language)
        url = f"{_API_BASE}/text-to-speech/{voice_id}"
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.75,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True,
            },
        }
        resp = http_requests.post(
            url,
            json=payload,
            headers={
                "xi-api-key": self._api_key,
                "Content-Type": "application/json",
                "Accept": "audio/mpeg",
            },
            timeout=60,
        )
        resp.raise_for_status()
        mp3_bytes = resp.content
        duration = _mp3_duration_seconds(mp3_bytes)
        logger.info(
            "ElevenLabs: generated %.2fs audio for lang=%s (%d bytes)",
            duration,
            language,
            len(mp3_bytes),
        )
        return mp3_bytes, duration

    @staticmethod
    def estimate_cost(character_count: int) -> float:
        """Rough USD cost estimate (~$0.30 per 1000 characters for Eleven Multilingual v2)."""
        return character_count * 0.30 / 1000
