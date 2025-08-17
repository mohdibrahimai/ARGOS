"""Simple hybrid retriever implementation.

This module loads a small seed corpus from JSON and performs very naive
string‑matching based retrieval.  The goal is to provide a minimal but
functioning retriever that demonstrates the ARGOS architecture without
pulling in heavy dependencies.  In a production deployment this would be
replaced by a hybrid BM25 + vector retriever backed by Elasticsearch or
Qdrant/Weaviate.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import List, Tuple


@dataclass
class Document:
    """A single document in the corpus."""

    source_id: str
    title: str
    url: str
    content: str

    @property
    def tokens(self) -> set[str]:
        return set(self.content.lower().split())


class SimpleRetriever:
    """A naive retriever that matches query tokens against document tokens."""

    def __init__(self, corpus_path: Path) -> None:
        self.documents: List[Document] = []
        self._load_corpus(corpus_path)

    def _load_corpus(self, corpus_path: Path) -> None:
        if not corpus_path.exists():
            raise FileNotFoundError(f"Corpus file not found at {corpus_path}")
        with corpus_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        for entry in data:
            doc = Document(
                source_id=entry["source_id"],
                title=entry["title"],
                url=entry["url"],
                content=entry["content"],
            )
            self.documents.append(doc)

    @staticmethod
    def _score(doc_tokens: set[str], query_tokens: set[str]) -> float:
        if not query_tokens:
            return 0.0
        intersection = query_tokens.intersection(doc_tokens)
        return len(intersection) / len(query_tokens)

    def search(self, query: str, top_k: int = 6) -> List[Tuple[Document, float]]:
        """Return top_k documents ranked by simple token overlap score."""
        query_tokens = set(query.lower().split())
        scores = []
        for doc in self.documents:
            score = self._score(doc.tokens, query_tokens)
            if score > 0:
                scores.append((doc, score))
        # If no documents scored, fall back to returning first top_k documents
        if not scores:
            return [(doc, 0.0) for doc in self.documents[:top_k]]
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]


@lru_cache(maxsize=1)
def get_retriever() -> SimpleRetriever:
    """Singleton accessor to the retriever instance."""
    corpus_path = Path(os.getenv("SEED_CORPUS_PATH", "seeds/corpus/seeds.json"))
    return SimpleRetriever(corpus_path)