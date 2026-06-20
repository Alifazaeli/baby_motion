"""Developmental stage parameters injected into Claude prompts.

These match the child-development framework referenced in PRD v2.1 §11
and used by the original hand-authored YAML pipeline.
"""

AGE_GROUP_PARAMS: dict[str, dict] = {
    "12_18m": {
        "scene_count_min": 3,
        "scene_count_max": 5,
        "sentence_length": "very short — 4 to 7 words maximum per sentence",
        "animation_pace": "very slow and gentle",
        "story_structure": "single simple concept or emotion, highly repetitive, no conflict",
        "scene_duration_sec": 9,
        "style_notes": "extremely soft rounded shapes, no sharp edges, very warm pastel colors",
    },
    "18_30m": {
        "scene_count_min": 4,
        "scene_count_max": 6,
        "sentence_length": "short — 6 to 10 words per sentence",
        "animation_pace": "slow and gentle",
        "story_structure": "familiar daily routine or simple cause-and-effect, 1–2 characters",
        "scene_duration_sec": 8,
        "style_notes": "soft rounded shapes, warm pastel colors, friendly expressive faces",
    },
    "30_42m": {
        "scene_count_min": 5,
        "scene_count_max": 8,
        "sentence_length": "short to medium — 8 to 14 words per sentence",
        "animation_pace": "moderate, comfortable pace",
        "story_structure": "simple beginning-middle-end with a small problem and resolution, 2–3 characters",
        "scene_duration_sec": 7,
        "style_notes": "bright cheerful colors, expressive characters, clear simple backgrounds",
    },
    "42_60m": {
        "scene_count_min": 6,
        "scene_count_max": 10,
        "sentence_length": "medium — 10 to 18 words per sentence, full natural sentences",
        "animation_pace": "engaging, slightly faster",
        "story_structure": "clear narrative arc with emotional journey, 2–4 characters, mild complexity",
        "scene_duration_sec": 6,
        "style_notes": "vibrant colors, richer details, expressive storytelling scenes",
    },
}
