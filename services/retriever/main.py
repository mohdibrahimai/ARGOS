"""FastAPI server for the ARGOS retriever service.

This service provides a `/v1/search` endpoint that accepts a query and
returns a list of candidate sources drawn from a simple seed corpus.  It also
exposes Prometheus metrics under `/metrics` and health/readiness probes.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from shared.logging_utils import configure_logging
from shared.schemas import Citation, Mode

from .retriever import Document, get_retriever

app = FastAPI(title="ARGOS Retriever", version="0.1.0")

# Configure logging
logger = configure_logging("retriever")

# Allow the UI to call this service directly from the browser in dev mode
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Prometheus metrics
REQUEST_COUNT = Counter(
    "argos_retriever_requests_total",
    "Total number of search requests to the retriever",
    ["mode"],
)
REQUEST_LATENCY = Histogram(
    "argos_retriever_latency_seconds",
    "Latency of retriever search requests",
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0),
)


@app.get("/healthz", tags=["health"])
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz", tags=["health"])
async def ready() -> Dict[str, str]:
    # In this simple implementation, the service is ready if the retriever can be instantiated
    try:
        get_retriever()
        return {"status": "ready"}
    except Exception as exc:
        logger.error("retriever not ready", error=str(exc))
        raise HTTPException(status_code=503, detail="Retriever not ready")


@app.get("/metrics")
async def metrics() -> Response:
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


@app.post("/v1/search", tags=["search"])
async def search(body: Dict[str, Any]) -> JSONResponse:
    """Search for relevant documents given a query.

    Expected body:
    {
        "query": "string",
        "top_k": 6,
        "trace_id": "uuid"
    }
    """
    query: str = body.get("query")
    top_k: int = body.get("top_k", 6)
    trace_id: str = body.get("trace_id", "unknown")
    mode: str = body.get("mode", "fast")
    if not query:
        raise HTTPException(status_code=400, detail="Query must be provided")
    start_time = time.perf_counter()
    REQUEST_COUNT.labels(mode).inc()
    retriever = get_retriever()
    results = retriever.search(query, top_k=top_k)
    elapsed = time.perf_counter() - start_time
    REQUEST_LATENCY.observe(elapsed)
    logger.info(
        "search completed",
        query=query,
        top_k=top_k,
        elapsed=elapsed,
        results=len(results),
        trace_id=trace_id,
    )
    # Construct response
    sources = []
    for doc, score in results:
        sources.append(
            {
                "source_id": doc.source_id,
                "title": doc.title,
                "url": doc.url,
                "snippet": doc.content[:200] + ("…" if len(doc.content) > 200 else ""),
                "score": score,
            }
        )
    return JSONResponse(
        {
            "trace_id": trace_id,
            "results": sources,
        }
    )