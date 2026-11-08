from django.db import models
from pgvector.django import HalfVectorField, HnswIndex
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField

class Chapter(models.Model):
    number = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)

    class Meta:
        ordering = ["number"]

    def __str__(self):
        return f"Chapter {self.number}: {self.title}"


class Section(models.Model):
    number = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=500)
    chapter = models.ForeignKey(
        Chapter, on_delete=models.CASCADE, related_name="sections"
    )
    body = models.TextField()
    illustrations = models.JSONField(default=list, blank=True)
    explanations = models.JSONField(default=list, blank=True)
    exceptions = models.JSONField(default=list, blank=True)
    embedding = HalfVectorField(dimensions=2048,null=True, blank=True)
    full_text_search = SearchVectorField(null=True)

    class Meta:
        ordering = ["number"]
        indexes = [HnswIndex(
            name="section_embedding_hnsw",
            fields=["embedding"],
            m=16,
            ef_construction=64,
            opclasses=["halfvec_cosine_ops"],
            ),
            GinIndex(
            name="full_text_search_ginindex",
            fields=["full_text_search"]
                )
            ]

    def __str__(self):
        return f"Section {self.number}: {self.title}"
    
    
