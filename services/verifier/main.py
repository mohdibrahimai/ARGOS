"""Stub implementation of the verifier service.

This service exposes a `/v1/verify` endpoint that accepts a sentence and
evidence passages.  It returns an entailment label, confidence, and
unsupported spans.  The implementation here is heuristic: if the evidence
contains the sentence verbatim, the label is "entailed"; if it shares at
least one content word, the label is "weak"; otherwise it is "unsupported".
Unsupported spans cover the entire sentence for unsupported labels.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Tuple

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from shared.logging_utils import configure_logging

app = FastAPI(title="ARGOS Verifier", version="0.1.0")
logger = configure_logging("verifier")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "argos_verifier_requests_total",
    "Total number of verification requests",
)
REQUEST_LATENCY = Histogram(
    "argos_verifier_latency_seconds",
    "Latency of verifier requests",
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0),
)


@app.get("/healthz")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz")
async def ready() -> Dict[str, str]:
    return {"status": "ready"}


@app.get("/metrics")
async def metrics() -> Response:
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


@app.post("/v1/verify")
async def verify(body: Dict[str, Any]) -> JSONResponse:
    """Verify a sentence against provided evidence.

    Body structure:
    {
      "sentence": "string",
      "evidence": [ { "text": "string", "url": "string" }, ... ]
    }
    """
    start_time = time.perf_counter()
    REQUEST_COUNT.inc()
    sentence: str = body.get("sentence", "")
    evidence_list: List[Dict[str, str]] = body.get("evidence", [])
    if not sentence or not evidence_list:
        raise HTTPException(status_code=400, detail="Sentence and evidence must be provided")
    # Determine label heuristically
    label = "unsupported"
    confidence = 0.1
    sentence_lower = sentence.lower()
    words = set(sentence_lower.split())
    for e in evidence_list:
        text = e.get("text", "").lower()
        if sentence_lower in text:
            label = "entailed"
            confidence = 0.9
            break
        if words.intersection(set(text.split())):
            label = "weak"
            confidence = 0.5
    # Determine unsupported spans
    if label == "entailed":
        unsupported_spans: List[Tuple[int, int]] = []
    else:
        unsupported_spans = [(0, len(sentence))]
    elapsed = time.perf_counter() - start_time
    REQUEST_LATENCY.observe(elapsed)
    logger.info(
        "verification completed",
        sentence=sentence,
        label=label,
        confidence=confidence,
        unsupported_spans=unsupported_spans,
        elapsed=elapsed,
    )
    return JSONResponse({"label": label, "confidence": confidence, "unsupported_spans": unsupported_spans})