import os
from dotenv import load_dotenv
from openai import OpenAI
from pgvector import HalfVector
from pgvector.django import CosineDistance
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F
import requests

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


def vector_search(question: str, limit: int = 20):
    query_vec = HalfVector(embed_query(question))
    return (
        Section.objects
        .filter(embedding__isnull=False)
        .annotate(distance=CosineDistance("embedding", query_vec))
        .order_by("distance")[:limit]
    )
    
import re

def keyword_search(question: str, limit: int = 20):
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
    

RERANK_URL = (
    "https://ai.api.nvidia.com/v1/retrieval/"
    "nvidia/nemotron-3.5-rerank-8b/reranking"
)
RERANK_MODEL = "nvidia/nemotron-3.5-rerank-8b"


def get_rerank(query: str, passages: list[str], timeout: int = 60) -> list[dict]:
    """
    Raw API call. Sends one query + a list of passage strings to the
    NIM reranker and returns the 'rankings' list from the response.

    Each item looks like {"index": 1, "logit": -2.09}, where "index" is
    the position of the passage in the list we sent. The API returns them
    best-first, but we don't rely on that here.
    """
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        raise RuntimeError("NVIDIA_API_KEY is not set (check your .env)")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }

    payload = {
        "model": RERANK_MODEL,
        "query": {"text": query},
        "passages": [{"text": p} for p in passages],
    }

    response = requests.post(RERANK_URL, headers=headers, json=payload, timeout=timeout)
    response.raise_for_status()  # if error raises on 4xx/5xx
    return response.json()["rankings"]


def section_text(section) -> str:
    """
    Turn a Section into the text the reranker sees. Keep it the same as
    what you embedded, so the reranker judges the same content.
    """
    return f"{section.title}\n{section.body}"


def rerank(query: str, sections: list, top_n: int = 5) -> list[tuple]:
    """
    Take the candidate sections (e.g. the top 20 from hybrid_search),
    rerank them against the query, and return the best top_n as
    (section, score) tuples, best first.
    """
    # Nothing to rerank, and the API would reject an empty list.
    if not sections:
        return []

    passages = [section_text(s) for s in sections]
    rankings = get_rerank(query, passages)

    # Sort by logit, highest first.
    rankings = sorted(rankings, key=lambda r: r["logit"], reverse=True)

    # "index" points back into the list sent, which lines up with
    # `sections`, so we can return the original Section objects.
    return [sections[r["index"]] for r in rankings[:top_n]]



def retrieve(question: str, limit: int = 20, top_n: int = 20) -> list[tuple]:
    """
    Full retrieval pipeline: hybrid search -> rerank.

    question   : the user's question
    candidates : how many sections hybrid_search pulls in
    top_n      : how many sections to keep after reranking

    Returns a list of (section, score) tuples, best first. The score is the
    raw reranker logit: use it for ordering and debugging, not as a probability.
    """
    candidates = hybrid_search(question, limit=limit)
    result = rerank(question, candidates, top_n=top_n)
    return result