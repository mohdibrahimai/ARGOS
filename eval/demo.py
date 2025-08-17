"""Demo script for ARGOS.

This script issues a sequence of queries to the local answer API and prints
the resulting answers with confidence and highlighted sentences.  It serves
as a basic end-to-end smoke test.
"""

import json
import sys
from typing import List

import requests

QUERIES = [
    "Who won the 2019 Cricket World Cup and where was the final played?",
    "Compare GPT-4 vs Llama-3 70B release timelines and training data disclosures.",
    "Convert 3,500 INR to USD at the rate on Jan 5, 2022.",
    "Is visa-free entry to Thailand available for Indians right now?",
    "¿Cuándo fue lanzado el modelo Gemini 1.5 Pro?",
]


def run_query(query: str, url: str = "http://localhost:8000/v1/answer") -> None:
    body = {"query": query, "mode": "fast", "top_k": 6, "trace_id": "demo"}
    try:
        resp = requests.post(url, json=body, timeout=5)
        resp.raise_for_status()
    except Exception as exc:
        print(f"Error querying: {exc}")
        return
    data = resp.json()
    print(f"\n=== Query: {query} ===")
    print(f"Answer (confidence {data['confidence_overall']:.2f}):")
    # Print raw HTML stripped of tags
    answer_text = data['answer_html'].replace('<p>', '').replace('</p>', '')
    print(answer_text)
    print("Sentences with labels:")
    for s in data['sentences']:
        label = s['verifier']['label']
        conf = s['verifier']['confidence']
        print(f" - [{label} @ {conf:.2f}] {s['text']}")
    print("Sources:")
    for src in data['sources']:
        print(f" - {src['title']} ({src['url']})")


def main() -> None:
    for q in QUERIES:
        run_query(q)


if __name__ == "__main__":
    sys.exit(main())