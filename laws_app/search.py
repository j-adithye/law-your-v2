import os
from dotenv import load_dotenv
from openai import OpenAI
from pgvector import HalfVector
from pgvector.django import CosineDistance
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F

from laws_app.models import Section

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


def vector_search(question: str, limit: int = 5):
    query_vec = HalfVector(embed_query(question))
    return (
        Section.objects
        .filter(embedding__isnull=False)
        .annotate(distance=CosineDistance("embedding", query_vec))
        .order_by("distance")[:limit]
    )
    
import re

def keyword_search(question: str, limit: int = 5):
    words = re.findall(r"\w+", question)
    query = SearchQuery(words[0], config="english")
    for w in words[1:]:
        query |= SearchQuery(w, config="english")
    return (
        Section.objects
        .annotate(rank=SearchRank(F("full_text_search"), query))
        .filter(full_text_search=query)
        .order_by("-rank")[:limit]
    )

from collections import defaultdict    

def rrf(ranked_lists, k=60):
    """
    Merge several ranked lists into one using Reciprocal Rank Fusion.

    ranked_lists: list of lists, each one a ranked list of ids (best first).
    Returns a list of (id, score) sorted by score, best first.
    """
    scores = defaultdict(float)
    for ranked in ranked_lists:
        for rank, item_id in enumerate(ranked, start=1):
            scores[item_id] += 1 / (k + rank)
    return sorted(scores.items(), key=lambda pair: pair[1], reverse=True)


def hybrid_search(question: str, limit: int = 20, candidates: int = 20, k: int = 60):
    """Run vector + keyword search, merge with RRF, return Sections best-first."""
    vector_ids = [s.number for s in vector_search(question, limit=candidates)]
    keyword_ids = [s.number for s in keyword_search(question, limit=candidates)]

    merged = rrf([vector_ids, keyword_ids], k=k)
    top_ids = [number for number, _score in merged[:limit]]

    sections = Section.objects.in_bulk(top_ids)  # {number: Section}
    return [sections[number] for number in top_ids]