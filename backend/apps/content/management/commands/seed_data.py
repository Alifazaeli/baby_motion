"""Seed the database with sample languages, categories, and stories.

Creates:
  - 2 languages (fa, en)
  - 4 categories with translations
  - 12 stories: 3 per age group × 4 groups, each with fa + en translations
  - Basic UI strings for both languages

Run with:
    python manage.py seed_data
    python manage.py seed_data --clear   (wipe content tables first)
"""
from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.content.models import (
    Category,
    CategoryTranslation,
    Language,
    Story,
    StoryTranslation,
    UIString,
)

CDN = "https://cdn.arvanstorage.ir/storytelling-prod"

LANGUAGES = [
    {"code": "fa", "display_name": "Persian", "is_rtl": True},
    {"code": "en", "display_name": "English", "is_rtl": False},
]

CATEGORIES = [
    {
        "slug": "bedtime",
        "icon_url": f"{CDN}/ui/icons/category_bedtime.svg",
        "display_order": 1,
        "translations": {
            "fa": "قبل از خواب",
            "en": "Bedtime",
        },
    },
    {
        "slug": "routine",
        "icon_url": f"{CDN}/ui/icons/category_routine.svg",
        "display_order": 2,
        "translations": {
            "fa": "روتین روزانه",
            "en": "Daily Routine",
        },
    },
    {
        "slug": "emotion",
        "icon_url": f"{CDN}/ui/icons/category_emotion.svg",
        "display_order": 3,
        "translations": {
            "fa": "احساسات",
            "en": "Emotions",
        },
    },
    {
        "slug": "adventure",
        "icon_url": f"{CDN}/ui/icons/category_adventure.svg",
        "display_order": 4,
        "translations": {
            "fa": "ماجراجویی",
            "en": "Adventure",
        },
    },
]

# 3 stories per age group, each with fa + en translations
# duration_seconds matches PRD age group ranges
STORIES = [
    # ── 12–18 months ──────────────────────────────────────────────────
    {
        "slug": "little-moon",
        "category": "bedtime",
        "age_group": "12_18m",
        "duration_seconds": 120,
        "cover_url": f"{CDN}/stories/little-moon/cover.jpg",
        "translations": {
            "fa": {
                "title": "ماه کوچولو",
                "description": "ماه کوچولو آسمان را نگاه می‌کند.",
                "manifest_url": f"{CDN}/stories/little-moon/manifests/fa.json",
            },
            "en": {
                "title": "Little Moon",
                "description": "Little moon looks at the sky.",
                "manifest_url": f"{CDN}/stories/little-moon/manifests/en.json",
            },
        },
    },
    {
        "slug": "good-night-bear",
        "category": "bedtime",
        "age_group": "12_18m",
        "duration_seconds": 100,
        "cover_url": f"{CDN}/stories/good-night-bear/cover.jpg",
        "translations": {
            "fa": {
                "title": "شب بخیر خرسه",
                "description": "خرسه می‌خوابد. شب بخیر.",
                "manifest_url": f"{CDN}/stories/good-night-bear/manifests/fa.json",
            },
            "en": {
                "title": "Good Night Bear",
                "description": "Bear goes to sleep. Good night.",
                "manifest_url": f"{CDN}/stories/good-night-bear/manifests/en.json",
            },
        },
    },
    {
        "slug": "wash-hands",
        "category": "routine",
        "age_group": "12_18m",
        "duration_seconds": 90,
        "cover_url": f"{CDN}/stories/wash-hands/cover.jpg",
        "translations": {
            "fa": {
                "title": "دست بشور",
                "description": "دست‌ها را می‌شوریم.",
                "manifest_url": f"{CDN}/stories/wash-hands/manifests/fa.json",
            },
            "en": {
                "title": "Wash Your Hands",
                "description": "We wash our hands.",
                "manifest_url": f"{CDN}/stories/wash-hands/manifests/en.json",
            },
        },
    },
    # ── 18–30 months ──────────────────────────────────────────────────
    {
        "slug": "beary-and-flower",
        "category": "bedtime",
        "age_group": "18_30m",
        "duration_seconds": 165,
        "cover_url": f"{CDN}/stories/beary-and-flower/cover.jpg",
        "translations": {
            "fa": {
                "title": "خرسی و گل",
                "description": "خرسی یه گل صورتی پیدا کرد.",
                "manifest_url": f"{CDN}/stories/beary-and-flower/manifests/fa.json",
            },
            "en": {
                "title": "Beary and the Flower",
                "description": "Beary found a pink flower.",
                "manifest_url": f"{CDN}/stories/beary-and-flower/manifests/en.json",
            },
        },
    },
    {
        "slug": "happy-sad-day",
        "category": "emotion",
        "age_group": "18_30m",
        "duration_seconds": 180,
        "cover_url": f"{CDN}/stories/happy-sad-day/cover.jpg",
        "translations": {
            "fa": {
                "title": "روز شاد و غمگین",
                "description": "گاهی شاد هستیم، گاهی غمگین.",
                "manifest_url": f"{CDN}/stories/happy-sad-day/manifests/fa.json",
            },
            "en": {
                "title": "Happy and Sad Day",
                "description": "Sometimes we feel happy, sometimes sad.",
                "manifest_url": f"{CDN}/stories/happy-sad-day/manifests/en.json",
            },
        },
    },
    {
        "slug": "bunny-breakfast",
        "category": "routine",
        "age_group": "18_30m",
        "duration_seconds": 150,
        "cover_url": f"{CDN}/stories/bunny-breakfast/cover.jpg",
        "translations": {
            "fa": {
                "title": "صبحانه خرگوشه",
                "description": "خرگوشه صبحانه می‌خورد. نوش جانش!",
                "manifest_url": f"{CDN}/stories/bunny-breakfast/manifests/fa.json",
            },
            "en": {
                "title": "Bunny's Breakfast",
                "description": "Bunny eats breakfast. Yummy!",
                "manifest_url": f"{CDN}/stories/bunny-breakfast/manifests/en.json",
            },
        },
    },
    # ── 30–42 months ──────────────────────────────────────────────────
    {
        "slug": "brave-little-fox",
        "category": "adventure",
        "age_group": "30_42m",
        "duration_seconds": 240,
        "cover_url": f"{CDN}/stories/brave-little-fox/cover.jpg",
        "translations": {
            "fa": {
                "title": "روباه کوچک شجاع",
                "description": "روباه کوچک از جنگل تاریک رد می‌شود.",
                "manifest_url": f"{CDN}/stories/brave-little-fox/manifests/fa.json",
            },
            "en": {
                "title": "The Brave Little Fox",
                "description": "A little fox walks through the dark forest.",
                "manifest_url": f"{CDN}/stories/brave-little-fox/manifests/en.json",
            },
        },
    },
    {
        "slug": "sharing-is-caring",
        "category": "emotion",
        "age_group": "30_42m",
        "duration_seconds": 220,
        "cover_url": f"{CDN}/stories/sharing-is-caring/cover.jpg",
        "translations": {
            "fa": {
                "title": "باهم شریک شدن",
                "description": "وقتی چیزی را با دوستانمان تقسیم می‌کنیم، خوشحال‌تر می‌شویم.",
                "manifest_url": f"{CDN}/stories/sharing-is-caring/manifests/fa.json",
            },
            "en": {
                "title": "Sharing Is Caring",
                "description": "When we share with friends, everyone feels happier.",
                "manifest_url": f"{CDN}/stories/sharing-is-caring/manifests/en.json",
            },
        },
    },
    {
        "slug": "bedtime-for-elephant",
        "category": "bedtime",
        "age_group": "30_42m",
        "duration_seconds": 260,
        "cover_url": f"{CDN}/stories/bedtime-for-elephant/cover.jpg",
        "translations": {
            "fa": {
                "title": "وقت خواب فیله",
                "description": "فیله دندان‌هایش را مسواک می‌زند و آماده خواب می‌شود.",
                "manifest_url": f"{CDN}/stories/bedtime-for-elephant/manifests/fa.json",
            },
            "en": {
                "title": "Bedtime for Elephant",
                "description": "Elephant brushes his teeth and gets ready for bed.",
                "manifest_url": f"{CDN}/stories/bedtime-for-elephant/manifests/en.json",
            },
        },
    },
    # ── 42–60 months ──────────────────────────────────────────────────
    {
        "slug": "the-lost-kite",
        "category": "adventure",
        "age_group": "42_60m",
        "duration_seconds": 360,
        "cover_url": f"{CDN}/stories/the-lost-kite/cover.jpg",
        "translations": {
            "fa": {
                "title": "بادبادک گم‌شده",
                "description": "سارا بادبادکش را در باغ گم کرد و به دنبالش رفت.",
                "manifest_url": f"{CDN}/stories/the-lost-kite/manifests/fa.json",
            },
            "en": {
                "title": "The Lost Kite",
                "description": "Sara lost her kite in the garden and went on an adventure to find it.",
                "manifest_url": f"{CDN}/stories/the-lost-kite/manifests/en.json",
            },
        },
    },
    {
        "slug": "why-do-leaves-fall",
        "category": "adventure",
        "age_group": "42_60m",
        "duration_seconds": 320,
        "cover_url": f"{CDN}/stories/why-do-leaves-fall/cover.jpg",
        "translations": {
            "fa": {
                "title": "چرا برگ‌ها می‌ریزند؟",
                "description": "آرش از پدرش می‌پرسد چرا درخت‌ها در پاییز برگ‌هایشان را از دست می‌دهند.",
                "manifest_url": f"{CDN}/stories/why-do-leaves-fall/manifests/fa.json",
            },
            "en": {
                "title": "Why Do Leaves Fall?",
                "description": "Arash asks his father why trees lose their leaves in autumn.",
                "manifest_url": f"{CDN}/stories/why-do-leaves-fall/manifests/en.json",
            },
        },
    },
    {
        "slug": "the-brave-dentist-visit",
        "category": "emotion",
        "age_group": "42_60m",
        "duration_seconds": 300,
        "cover_url": f"{CDN}/stories/the-brave-dentist-visit/cover.jpg",
        "translations": {
            "fa": {
                "title": "پیش دندانپزشک",
                "description": "نیلوفر می‌ترسد، اما شجاعانه پیش دندانپزشک می‌رود.",
                "manifest_url": f"{CDN}/stories/the-brave-dentist-visit/manifests/fa.json",
            },
            "en": {
                "title": "The Brave Dentist Visit",
                "description": "Niloofar is scared, but bravely goes to the dentist.",
                "manifest_url": f"{CDN}/stories/the-brave-dentist-visit/manifests/en.json",
            },
        },
    },
]

UI_STRINGS = {
    "fa": {
        "home.welcome": "به بیبی‌موشن خوش آمدید",
        "home.catalog_empty": "هنوز قصه‌ای وجود ندارد.",
        "player.replay": "بازپخش",
        "player.exit": "خروج",
        "player.play": "پخش",
        "player.pause": "مکث",
        "onboarding.welcome": "قصه‌های شیرین برای کوچولوها",
        "settings.sign_out": "خروج از حساب",
        "error.network": "اتصال اینترنت ندارید.",
    },
    "en": {
        "home.welcome": "Welcome to BabyMotion",
        "home.catalog_empty": "No stories available yet.",
        "player.replay": "Replay",
        "player.exit": "Exit",
        "player.play": "Play",
        "player.pause": "Pause",
        "onboarding.welcome": "Sweet stories for little ones",
        "settings.sign_out": "Sign out",
        "error.network": "No internet connection.",
    },
}


class Command(BaseCommand):
    """Populate the database with sample content for development."""

    help = "Seed languages, categories, and 12 sample stories (3 per age group)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing content before seeding",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Clearing existing content…")
            StoryTranslation.objects.all().delete()
            Story.objects.all().delete()
            CategoryTranslation.objects.all().delete()
            Category.objects.all().delete()
            UIString.objects.all().delete()
            Language.objects.all().delete()
            self.stdout.write(self.style.WARNING("Content tables cleared."))

        # Languages
        self.stdout.write("Creating languages…")
        lang_objs: dict[str, Language] = {}
        for lang in LANGUAGES:
            obj, created = Language.objects.update_or_create(
                code=lang["code"],
                defaults={"display_name": lang["display_name"], "is_rtl": lang["is_rtl"]},
            )
            lang_objs[lang["code"]] = obj
            self.stdout.write(f"  {'created' if created else 'updated'} language: {lang['code']}")

        # Categories
        self.stdout.write("Creating categories…")
        cat_objs: dict[str, Category] = {}
        for cat in CATEGORIES:
            obj, created = Category.objects.update_or_create(
                slug=cat["slug"],
                defaults={
                    "icon_url": cat["icon_url"],
                    "display_order": cat["display_order"],
                },
            )
            cat_objs[cat["slug"]] = obj
            for lang_code, name in cat["translations"].items():
                CategoryTranslation.objects.update_or_create(
                    category=obj,
                    language=lang_objs[lang_code],
                    defaults={"name": name},
                )
            self.stdout.write(f"  {'created' if created else 'updated'} category: {cat['slug']}")

        # Stories
        self.stdout.write("Creating stories…")
        for story_data in STORIES:
            story, created = Story.objects.update_or_create(
                slug=story_data["slug"],
                defaults={
                    "category": cat_objs[story_data["category"]],
                    "age_group": story_data["age_group"],
                    "duration_seconds": story_data["duration_seconds"],
                    "cover_url": story_data["cover_url"],
                    "status": "published",
                    "published_at": timezone.now(),
                },
            )
            for lang_code, t in story_data["translations"].items():
                StoryTranslation.objects.update_or_create(
                    story=story,
                    language=lang_objs[lang_code],
                    defaults={
                        "title": t["title"],
                        "description": t["description"],
                        "manifest_url": t["manifest_url"],
                    },
                )
            label = f"[{story_data['age_group']}] {story_data['slug']}"
            self.stdout.write(f"  {'created' if created else 'updated'} story: {label}")

        # UI strings
        self.stdout.write("Creating UI strings…")
        total = 0
        for lang_code, strings in UI_STRINGS.items():
            for key, value in strings.items():
                UIString.objects.update_or_create(
                    key=key,
                    language=lang_objs[lang_code],
                    defaults={"value": value},
                )
                total += 1
        self.stdout.write(f"  {total} UI strings created/updated")

        self.stdout.write(self.style.SUCCESS(
            f"\n✓ Seeded: {len(lang_objs)} languages, "
            f"{len(cat_objs)} categories, "
            f"{len(STORIES)} stories (×2 languages each), "
            f"{total} UI strings"
        ))
