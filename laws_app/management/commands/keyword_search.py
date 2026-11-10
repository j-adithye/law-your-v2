from django.core.management.base import BaseCommand
from laws_app.search import keyword_search


class Command(BaseCommand):
    help = "Keyword search over BNS sections"

    def add_arguments(self, parser):
        parser.add_argument("question", type=str)
        parser.add_argument("-limit", type=int, default=5)

    def handle(self, *args, **options):
        for s in keyword_search(options["question"], options["limit"]):
            self.stdout.write(f"{s.number:>4}  {s.rank:.4f}  {s.title}")