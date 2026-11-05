'''
Management command: loads the extracted BNS data (bns_sections.json)
into the Chapter and Section tables.

Run it with:  python manage.py load_json_data
(the filename without ".py" is the command name)

It lives in laws_app/management/commands/, and both `management/` and
`commands/` need an empty __init__.py for Django to discover it.
'''
import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from laws_app.models import Chapter, Section

'''
Build the path to the JSON file from settings.BASE_DIR (the project root,
where manage.py lives).
'''
JSON_PATH = os.path.join(settings.BASE_DIR, "data", "processed", "bns_sections.json")

# Values of the Roman numeral symbols. BNS chapters go up to XX (20),
ROMAN = {"I": 1, "V": 5, "X": 10}


def roman_to_int(s):
    """Convert a Roman numeral string like "II" or "XIV" to an int (2, 14).

    The JSON stores chapter numbers as Roman numerals, but the Chapter model
    uses an integer primary key, so we convert before saving.
    """
    total = 0
    prev = 0  # the value of the symbol we looked at last (one to the right)

    # Walk the string right to left. If the current symbol is smaller than
    # the one to its right, it's a subtractive pair (the I in IV or IX),
    # so subtract it. Otherwise add it.
    for ch in reversed(s.strip().upper()):
        val = ROMAN[ch]
        if val < prev:
            total -= val
        else:
            total += val
            prev = val
    return total


class Command(BaseCommand):
    # Shown when you run: python manage.py help load_json_data
    help = "Load BNS sections from bns_sections.json into the database"

    def handle(self, *args, **options):
        # Django calls handle() when the command runs. All the logic goes here.

        # Read the whole JSON file into a Python list of dicts, one per section.
        with open(JSON_PATH, encoding="utf-8") as f:
            data = json.load(f)

        for item in data:
            # Each section repeats its chapter info, so the same chapter shows
            # up many times. update_or_create looks up the Chapter by its
            # number: if it exists, it updates the title; if not, it creates
            # the row. It returns (object, created_flag); we only need the
            # object, so the flag goes to `_`.
            chapter, _ = Chapter.objects.update_or_create(
                number=roman_to_int(item["chapter_number"]),
                defaults={"title": item["chapter_title"]},
            )

            # Same idea for the Section, keyed on its number. The JSON stores
            # section_number as a string ("7"), so convert it to int.
            # Everything in `defaults` is what gets set or updated.
            Section.objects.update_or_create(
                number=int(item["section_number"]),
                defaults={
                    "title": item["title"],
                    # Attach the section to the chapter we just got above.
                    "chapter": chapter,
                    # body is a list of paragraphs in the JSON, but the model
                    # field is a single TextField, so join with newlines.
                    "body": "\n".join(item["body"]),
                    # These three stay as lists and are stored in JSONFields.
                    "illustrations": item["illustrations"],
                    "explanations": item["explanations"],
                    "exceptions": item["exceptions"],
                },
            )

        # Because of update_or_create, running this command again updates
        # existing rows instead of creating duplicates, so it's safe to re-run.
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(data)} sections"))