"""Claude API service for story segmentation.

Calls Claude once per story-draft to produce:
  - A shared style/character block for visual consistency
  - N scenes, each with per-language narration text and an image prompt

Output is validated against a strict schema; invalid output is retried up to 2×
with the validation error fed back as context (CS-12).
"""
from __future__ import annotations

import json
import logging
from typing import Any

import anthropic
from django.conf import settings

from .age_params import AGE_GROUP_PARAMS

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
You are an expert children's story creator for a baby and toddler storytelling app.
Your task is to transform a raw story idea into a structured scene-by-scene story.

Target age group: {age_group_label}
Developmental parameters:
- Number of scenes: {scene_count_min}–{scene_count_max}
- Sentence length: {sentence_length}
- Pacing: {animation_pace}
- Story structure: {story_structure}
- Visual style notes: {style_notes}

Languages to generate narration for: {languages}

You MUST output ONLY valid JSON — no explanation, no markdown, no preamble.
The JSON must exactly match this schema:

{{
  "style_block": "<string: shared character description and visual style, appended to every scene's image prompt for visual consistency>",
  "scenes": [
    {{
      "index": <integer starting at 0>,
      "narration": {{
        "<language_code>": "<narration text in that language>"
      }},
      "image_prompt": "<scene-specific setting and action — this will be combined with style_block>"
    }}
  ]
}}

Rules:
1. scene count must be between {scene_count_min} and {scene_count_max}
2. every scene must have narration in ALL requested languages: {languages}
3. narration sentences must respect the sentence length requirement
4. style_block must describe the main character(s) appearance and art style consistently
5. image_prompt must describe only scene-specific content; the style_block is always prepended automatically
"""


def _validate_output(data: Any, languages: list[str], params: dict) -> list[str]:
    """Return a list of validation error strings, empty if valid."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["Root value must be a JSON object"]

    if "style_block" not in data or not data["style_block"]:
        errors.append("Missing or empty 'style_block'")

    scenes = data.get("scenes")
    if not isinstance(scenes, list):
        errors.append("'scenes' must be a list")
        return errors

    count = len(scenes)
    if count < params["scene_count_min"] or count > params["scene_count_max"]:
        errors.append(
            f"Scene count {count} is outside allowed range "
            f"{params['scene_count_min']}–{params['scene_count_max']}"
        )

    for i, scene in enumerate(scenes):
        if not isinstance(scene, dict):
            errors.append(f"Scene {i} is not an object")
            continue
        if "image_prompt" not in scene or not scene["image_prompt"]:
            errors.append(f"Scene {i} missing 'image_prompt'")
        narration = scene.get("narration", {})
        if not isinstance(narration, dict):
            errors.append(f"Scene {i} 'narration' must be an object")
            continue
        for lang in languages:
            if lang not in narration or not narration[lang]:
                errors.append(f"Scene {i} missing narration for language '{lang}'")

    return errors


class ClaudeService:
    def __init__(self) -> None:
        self._client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    def segment_story(
        self,
        idea_text: str,
        age_groups: list[str],
        languages: list[str],
        category_slug: str = "",
    ) -> dict:
        """Call Claude to segment a story idea into scenes.

        Returns the validated dict with keys: style_block, scenes[].
        Raises ValueError on repeated validation failure.
        Raises anthropic.APIError on API failure.
        """
        primary_age_group = age_groups[0] if age_groups else "30_42m"
        params = AGE_GROUP_PARAMS[primary_age_group]
        age_label_map = {
            "12_18m": "12–18 months",
            "18_30m": "18–30 months",
            "30_42m": "30–42 months",
            "42_60m": "42–60 months",
        }
        age_label = " & ".join(age_label_map[ag] for ag in age_groups if ag in age_label_map)
        system = _SYSTEM_PROMPT.format(
            age_group_label=age_label or age_label_map[primary_age_group],
            scene_count_min=params["scene_count_min"],
            scene_count_max=params["scene_count_max"],
            sentence_length=params["sentence_length"],
            animation_pace=params["animation_pace"],
            story_structure=params["story_structure"],
            style_notes=params["style_notes"],
            languages=", ".join(languages),
        )

        user_message = f"Story idea: {idea_text}"
        if category_slug:
            user_message += f"\nCategory: {category_slug}"

        last_errors: list[str] = []
        messages: list[dict] = [{"role": "user", "content": user_message}]

        for attempt in range(3):
            response = self._client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4096,
                system=system,
                messages=messages,
            )
            raw = response.content[0].text.strip()

            try:
                data = json.loads(raw)
            except json.JSONDecodeError as exc:
                last_errors = [f"Response is not valid JSON: {exc}"]
                messages.append({"role": "assistant", "content": raw})
                messages.append({
                    "role": "user",
                    "content": f"Your response was not valid JSON. Error: {exc}. "
                               f"Please output ONLY the JSON object, nothing else.",
                })
                logger.warning("Claude segmentation attempt %d: JSON parse error", attempt + 1)
                continue

            errors = _validate_output(data, languages, params)
            if not errors:
                logger.info(
                    "Claude segmentation succeeded on attempt %d with %d scenes",
                    attempt + 1,
                    len(data["scenes"]),
                )
                return data

            last_errors = errors
            messages.append({"role": "assistant", "content": raw})
            messages.append({
                "role": "user",
                "content": (
                    "Your response had validation errors:\n"
                    + "\n".join(f"- {e}" for e in errors)
                    + "\nPlease fix them and output ONLY the corrected JSON object."
                ),
            })
            logger.warning(
                "Claude segmentation attempt %d validation errors: %s", attempt + 1, errors
            )

        raise ValueError(
            f"Claude segmentation failed after 3 attempts. Last errors: {last_errors}"
        )

    @staticmethod
    def estimate_cost(input_tokens: int, output_tokens: int) -> float:
        """Rough USD cost estimate for claude-sonnet-4-6 (update if model pricing changes)."""
        return (input_tokens * 3.0 + output_tokens * 15.0) / 1_000_000
