import os
from dotenv import load_dotenv
from openai import OpenAI
from pgvector import HalfVector
from pgvector.django import CosineDistance
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F

from .models import Section

load_dotenv()

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY"),
)

MODEL = "nvidia/nemotron-3-embed-1b"


def embed_query(question: str) -> list[float]:
    response = client.embeddings.create(
        model=MODEL,
        input=question,
        encoding_format="float",
        extra_body={"input_type": "query", "truncate": "NONE"},
    )
    return response.data[0].embedding


def vector_search(question: str, k: int = 5):
    query_vec = HalfVector(embed_query(question))
    return (
        Section.objects
        .filter(embedding__isnull=False)
        .annotate(distance=CosineDistance("embedding", query_vec))
        .order_by("distance")[:k]
    )
    
def keyword_search(question: str, limit: int = 20):
    query = SearchQuery(question, search_type="websearch", config="english")
    return (
        Section.objects
        .annotate(rank=SearchRank(F("full_text_search"), query))
        .filter(full_text_search=query)
        .order_by("-rank")[:limit]
    )