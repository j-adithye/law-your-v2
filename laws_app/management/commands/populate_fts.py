# management/commands/populate_fts.py
from django.core.management.base import BaseCommand
from django.contrib.postgres.search import SearchVector

from laws_app.models import Section


class Command(BaseCommand):
    help = "Populate full_text_search for all sections"

    def handle(self, *args, **options):
        vector = (
            SearchVector("title", weight="A", config="english")
            + SearchVector("body", weight="B", config="english")
        )
        count = Section.objects.update(full_text_search=vector)
        self.stdout.write(self.style.SUCCESS(f"Populated {count} sections"))