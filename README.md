# ARGOS — Evidence‑Bound Answering System

ARGOS is a production-grade answering system designed to retrieve diverse evidence from the web or locally indexed corpora, generate answers with inline citations, verify the factuality of each sentence, and report metrics on support and calibration.  This repository contains the full source code and configuration required to run ARGOS locally using Docker Compose and Kubernetes (via Helm), along with a simple user interface and evaluation tooling.

## Repository Layout

```
├── apps/argos-ui/            # Next.js + Tailwind user interface (colored support maps)
├── services/answer-api/      # FastAPI service exposing the /v1/answer endpoint
├── services/retriever/       # Hybrid BM25 + vector search service
├── services/verifier/        # Verifier training, ONNX export, and serving stubs
├── eval/                     # Metric computation (SWA/NER/CR/ECE) and nightly report
├── data-engine/              # Placeholder for failure clustering and counterfactual generation
├── observability/            # Prometheus and Grafana configuration
├── ops/                      # Docker Compose and Helm charts
├── seeds/                    # Minimal seed corpus and dataset fetch scripts
└── shared/                   # Shared schemas, feature flags and utilities
```

### Quick Start

ARGOS can be brought up locally using Docker Compose.  This will start the retriever, answer API, verifier (as a stub), a Prometheus instance, and a Grafana dashboard.  The UI is also included and will be served on port 3000 by default.

```bash
# Clone this repository (already present in the exercise environment)
cd argos

## Build and start all services
make dev-up

## Visit the UI
# Open http://localhost:3000 in your browser to query the system.

## Tear down services
make dev-down

## Run the demo script on the seed corpus
make demo

## Run nightly evaluation and produce HTML report (written to eval/report.html)
make eval-nightly
```

### Demo Queries

The demo script performs a handful of representative queries against the small seed corpus.  These include:

1. **Single-hop question:** “Who won the 2019 Cricket World Cup and where was the final played?”
2. **Multi-hop comparison:** “Compare GPT‑4 vs Llama‑3 70B release timelines and training data disclosures.”
3. **Numeric/date:** “Convert 3,500 INR to USD at the rate on Jan 5, 2022.”
4. **Ambiguous & recency:** “Is visa‑free entry to Thailand available for Indians right now?”
5. **Non‑English:** “¿Cuándo fue lanzado el modelo Gemini 1.5 Pro?”

Each answer returned by ARGOS contains inline citations tied to the seed corpus, color coded spans to indicate support (green), weak evidence (yellow), and unsupported claims (red).  An overall confidence meter summarises the system’s belief in the answer.

### Architecture Overview

ARGOS consists of several cooperating micro‑services:

* **Retriever:** Indexes the seed corpus using both BM25 (via a simple in‑memory store) and vector search (via FAISS).  At query time it returns a ranked list of candidate passages with snippets and metadata.
* **Answer API:** Accepts queries via a REST endpoint, orchestrates retrieval, calls an external LLM to draft an answer (stubbed in this implementation), attaches inline citations, and sends each sentence plus its evidence to the verifier.
* **Verifier:** A placeholder micro‑service that exposes a `/v1/verify` endpoint.  In a full deployment this would run a fine‑tuned cross‑encoder exported to ONNX and served via Triton.  It returns a label (entailed/weak/unsupported/contradicted), a confidence score, and marks unsupported spans.  Here it returns synthetic labels for demonstration.
* **UI:** A Next.js application with Tailwind CSS that renders the answer along with colored spans and hoverable citations.  It also shows an overall confidence meter and collects user feedback.
* **Observability:** Prometheus scrapes metrics from the services and Grafana provides dashboards for key metrics such as Support‑Weighted Accuracy (SWA), No‑Evidence Rate (NER), and Contradiction Rate (CR).  Alerts can be configured in Prometheus and the system is configured for automatic rollback when regressions are detected in canary deployments (see the Helm charts).

### Development Notes

* **Python services** follow strict typing via `mypy` and linting with `ruff` and formatting with `black`.  Logs are emitted via `structlog` using the same structured schema across services.
* **Feature flags** in `shared/flags.py` allow switching between different embedding models, LLM providers, and index backends.  Environment variables override defaults.
* **Metrics** are defined in `eval/metrics.py` and summarised nightly by `eval/nightly_report.py`.  The script writes a simple HTML report with trend lines for SWA, NER, CR, and ECE.
* **Helm charts** under `ops/helm/argos` describe a production‑like deployment.  They include canary and shadow strategies to detect metric regressions and automatically roll back new versions.

For more details see comments in the individual modules.  Have fun exploring ARGOS!