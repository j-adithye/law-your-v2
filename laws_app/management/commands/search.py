from django.core.management.base import BaseCommand
from laws_app.search import vector_search


class Command(BaseCommand):
    help = "Vector search over BNS sections"

    def add_arguments(self, parser):
        parser.add_argument("question", type=str)
        parser.add_argument("-k", type=int, default=5)

    def handle(self, *args, **options):
        for s in vector_search(options["question"], options["k"]):
            self.stdout.write(f"{s.number:>4}  {s.distance:.4f}  {s.title}")