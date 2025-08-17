"""Pydantic models that define the request and response schemas shared across services.

These models are imported by both the answer API and the verifier to ensure the
API contracts remain synchronised.  Changing these schemas requires bumping
service versions and updating clients accordingly.
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional, Tuple

from pydantic import BaseModel, Field, HttpUrl


class Mode(str, Enum):
    """Query execution modes."""

    fast = "fast"
    strict = "strict"


class Citation(BaseModel):
    """A citation points to a specific span within an evidence source."""

    source_id: str = Field(..., description="Unique identifier for the evidence source")
    start: int = Field(..., ge=0, description="Start character index in the source snippet")
    end: int = Field(..., ge=0, description="End character index in the source snippet")


class SentenceVerifierResult(BaseModel):
    """Results returned by the verifier for a single sentence."""

    label: str = Field(
        ...,
        description="Entailment label returned by the verifier",
        pattern="^(entailed|weak|unsupported|contradicted)$",
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for the label")
    unsupported_spans: List[Tuple[int, int]] = Field(
        default_factory=list,
        description="List of (start, end) character spans within the sentence that the verifier marked as unsupported",
    )


class Sentence(BaseModel):
    """A sentence from the answer along with citations and verifier output."""

    text: str
    citations: List[Citation] = Field(default_factory=list)
    verifier: SentenceVerifierResult
    weight: float = Field(1.0, description="Sentence importance weight used in metric computations")


class Source(BaseModel):
    """Describes an evidence source returned by the retriever."""

    source_id: str
    title: str
    url: HttpUrl
    snippet: str


class AnswerRequest(BaseModel):
    """Request body for the answer API."""

    query: str
    mode: Mode = Mode.fast
    top_k: int = Field(6, ge=1, le=10)
    trace_id: str


class AnswerResponse(BaseModel):
    """Response returned by the answer API."""

    trace_id: str
    answer_html: str
    sentences: List[Sentence]
    sources: List[Source]
    confidence_overall: float = Field(
        ..., ge=0.0, le=1.0, description="Overall confidence aggregated from verifier confidences"
    )
    metrics_snapshot: Optional[dict] = Field(
        None, description="Metrics snapshot (SWA/NER/CR/ECE) computed on the answer"
    )


class VerifierRequest(BaseModel):
    """Request body for the verifier service."""

    sentence: str
    evidence: List[dict] = Field(
        ..., description="List of evidence objects with text and URL fields"
    )


class VerifierResponse(BaseModel):
    """Response returned by the verifier service."""

    label: str = Field(
        ..., pattern="^(entailed|unsupported|contradicted)$",
        description="Entailment label assigned to the sentence",
    )
    confidence: float = Field(..., ge=0.0, le=1.0)
    unsupported_spans: List[Tuple[int, int]] = Field(default_factory=list)