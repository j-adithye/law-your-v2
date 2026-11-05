import os
import time

from django.core.management.base import BaseCommand
from openai import OpenAI, RateLimitError

from laws_app.models import Section

MODEL = "nvidia/nemotron-3-embed-1b"
BATCH_SIZE = 16
MAX_RETRIES = 5

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY"),
)


def build_text(s):
    parts = [s.title, s.body]
    parts += s.explanations or []
    parts += s.exceptions or []
    return "\n".join(p for p in parts if p)


def embed_batch(texts):
    for attempt in range(MAX_RETRIES):
        try:
            response = client.embeddings.create(
                model=MODEL,
                input=texts,
                encoding_format="float",
                extra_body={"input_type": "passage", "truncate": "NONE"},
            )
            return [d.embedding for d in response.data]
        except RateLimitError:
            wait = 2 ** attempt
            print(f"Rate limited, waiting {wait}s...")
            time.sleep(wait)
    raise RuntimeError("Still rate limited after retries")


class Command(BaseCommand):
    help = "Embed all sections that don't have an embedding yet"

    def handle(self, *args, **options):
        pending = list(Section.objects.filter(embedding__isnull=True).order_by("number"))
        self.stdout.write(f"{len(pending)} sections to embed")

        for i in range(0, len(pending), BATCH_SIZE):
            batch = pending[i:i + BATCH_SIZE]
            vectors = embed_batch([build_text(s) for s in batch])

            for section, vector in zip(batch, vectors):
                section.embedding = vector
            Section.objects.bulk_update(batch, ["embedding"])

            self.stdout.write(f"Embedded {i + len(batch)} / {len(pending)}")

        self.stdout.write(self.style.SUCCESS("Done"))