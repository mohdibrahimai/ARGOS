"""FastAPI service implementing the ARGOS answer API.

This service orchestrates retrieval, answer generation and verification.  It
exposes a `/v1/answer` endpoint that accepts a query and returns an answer
with inline citations and metrics.  In this demonstration implementation
the LLM answerer is stubbed: it assembles an answer from the retrieved
documents.  The verifier is also stubbed to return synthetic labels.
"""

from __future__ import annotations

import os
import time
import uuid
from typing import Any, Dict, List

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    Summary,
    generate_latest,
)

from shared.logging_utils import configure_logging
from shared.schemas import (
    AnswerRequest,
    AnswerResponse,
    Citation,
    Sentence,
    SentenceVerifierResult,
    Source,
)

from eval.metrics import (
    support_weighted_accuracy,
    no_evidence_rate,
    contradiction_rate,
    calibration_error,
)


def get_env(name: str, default: str) -> str:
    return os.getenv(name, default)


RETRIEVER_URL = get_env("RETRIEVER_URL", "http://retriever:8001/v1/search")
VERIFIER_URL = get_env("VERIFIER_URL", "http://verifier:8002/v1/verify")

app = FastAPI(title="ARGOS Answer API", version="0.1.0")

# Structured logger
logger = configure_logging("answer-api")

# CORS for dev UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "argos_answer_requests_total",
    "Total number of answer requests",
    ["mode"],
)
REQUEST_LATENCY = Histogram(
    "argos_answer_latency_seconds",
    "Latency of answer requests",
    buckets=(0.1, 0.25, 0.5, 1.0, 2.0, 5.0),
)
SUPPORT_RATE_GAUGE = Gauge(
    "argos_support_rate",
    "Support‑Weighted Accuracy of the last answer",
)
NO_EVIDENCE_GAUGE = Gauge(
    "argos_no_evidence_rate",
    "No‑Evidence Rate of the last answer",
)
CONTRADICTION_GAUGE = Gauge(
    "argos_contradiction_rate",
    "Contradiction Rate of the last answer",
)
CALIBRATION_GAUGE = Gauge(
    "argos_calibration_ece",
    "Expected Calibration Error of the last answer",
)


@app.get("/healthz")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz")
async def ready() -> Dict[str, str]:
    # Always ready if we can reach the retriever (non-blocking ping)
    try:
        requests.get(RETRIEVER_URL.replace("/v1/search", "/healthz"), timeout=1)
        return {"status": "ready"}
    except Exception as exc:
        logger.error("answer-api not ready", error=str(exc))
        raise HTTPException(status_code=503, detail="Dependencies unavailable")


@app.get("/metrics")
async def metrics() -> Response:
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


@app.post("/v1/answer", response_model=AnswerResponse)
async def answer(request: AnswerRequest) -> AnswerResponse:
    """Generate an answer to the given query with citations and verifier support."""
    start_time = time.perf_counter()
    REQUEST_COUNT.labels(request.mode).inc()
    trace_id = request.trace_id or str(uuid.uuid4())
    # Retrieve candidate documents
    try:
        retr_resp = requests.post(
            RETRIEVER_URL,
            json={"query": request.query, "top_k": request.top_k, "trace_id": trace_id, "mode": request.mode},
            timeout=3,
        )
        retr_resp.raise_for_status()
    except Exception as exc:
        logger.error("retriever call failed", error=str(exc), trace_id=trace_id)
        raise HTTPException(status_code=502, detail="Retriever error")
    data = retr_resp.json()
    sources_raw = data.get("results", [])
    # Convert to Source models
    sources: List[Source] = []
    for s in sources_raw:
        try:
            src = Source(
                source_id=s["source_id"],
                title=s["title"],
                url=s["url"],
                snippet=s.get("snippet", ""),
            )
        except Exception as exc:
            logger.error("invalid source", error=str(exc), source=s, trace_id=trace_id)
            continue
        sources.append(src)
    if not sources:
        raise HTTPException(status_code=404, detail="No sources found")
    # Generate a naive answer by concatenating the first sentence from each doc
    sentences: List[Sentence] = []
    citations_map: Dict[str, int] = {}  # map source_id -> citation index
    citation_counter = 1
    answer_html_parts: List[str] = []
    for idx, src in enumerate(sources):
        content = src.snippet
        # Extract first sentence (naively splitting on '.')
        first_sent = content.split(".")[0].strip()
        if not first_sent:
            continue
        # Assign citation index
        if src.source_id not in citations_map:
            citations_map[src.source_id] = citation_counter
            citation_counter += 1
        citation_idx = citations_map[src.source_id]
        # Build HTML with citation footnote
        sent_html = f"{first_sent} <sup>[{citation_idx}]</sup>."
        answer_html_parts.append(sent_html)
        # Prepare citation object
        citation = Citation(source_id=src.source_id, start=0, end=len(first_sent))
        # Call the verifier with evidence list containing the full snippet and URL
        try:
            ver_resp = requests.post(
                VERIFIER_URL,
                json={
                    "sentence": first_sent,
                    "evidence": [
                        {"text": src.snippet, "url": str(src.url)}
                    ],
                },
                timeout=3,
            )
            ver_resp.raise_for_status()
            ver_json = ver_resp.json()
            verifier_result = SentenceVerifierResult(
                label=ver_json.get("label", "unsupported"),
                confidence=float(ver_json.get("confidence", 0.5)),
                unsupported_spans=ver_json.get("unsupported_spans", []),
            )
        except Exception as exc:
            logger.error("verifier call failed", error=str(exc), trace_id=trace_id)
            # Default unsupported result on error
            verifier_result = SentenceVerifierResult(label="unsupported", confidence=0.0, unsupported_spans=[(0, len(first_sent))])
        sentences.append(
            Sentence(
                text=first_sent + ".",
                citations=[citation],
                verifier=verifier_result,
            )
        )
    answer_html = " ".join(answer_html_parts)
    # Compute metrics
    swa = support_weighted_accuracy([s.dict() for s in sentences])
    ner = no_evidence_rate([s.dict() for s in sentences])
    cr = contradiction_rate([s.dict() for s in sentences])
    ece = calibration_error([s.dict() for s in sentences])
    SUPPORT_RATE_GAUGE.set(swa)
    NO_EVIDENCE_GAUGE.set(ner)
    CONTRADICTION_GAUGE.set(cr)
    CALIBRATION_GAUGE.set(ece)
    elapsed = time.perf_counter() - start_time
    REQUEST_LATENCY.observe(elapsed)
    logger.info(
        "answer generated",
        query=request.query,
        mode=request.mode,
        elapsed=elapsed,
        trace_id=trace_id,
        swa=swa,
        ner=ner,
        cr=cr,
        ece=ece,
    )
    response = AnswerResponse(
        trace_id=trace_id,
        answer_html=f"<p>{answer_html}</p>",
        sentences=sentences,
        sources=sources,
        confidence_overall=swa,
        metrics_snapshot={"support_rate": swa, "ner": ner, "cr": cr, "ece": ece},
    )
    return response