"""Metric computations for ARGOS.

This module provides functions for computing Support‑Weighted Accuracy (SWA),
No‑Evidence Rate (NER), Contradiction Rate (CR), and Expected Calibration
Error (ECE) given a list of sentences with verifier annotations.  Each
function accepts a list of sentences represented as dictionaries similar to
those returned by `Sentence.dict()`.  They are intentionally simple and
lightweight for demonstration purposes.
"""

from __future__ import annotations

from typing import Dict, List, Tuple


def _tokenize(text: str) -> List[str]:
    """Split text into tokens on whitespace.  Does not preserve punctuation."""
    return text.strip().split()


def _span_token_indices(text: str, span: Tuple[int, int]) -> List[int]:
    """Return indices of tokens covered by a char span."""
    tokens = _tokenize(text)
    positions = []
    offset = 0
    for idx, token in enumerate(tokens):
        start = text.find(token, offset)
        end = start + len(token)
        if start < span[1] and end > span[0]:
            positions.append(idx)
        offset = end
    return positions


def support_weighted_accuracy(sentences: List[Dict]) -> float:
    """Compute Support‑Weighted Accuracy (SWA).

    SWA = (Σ_i w_i * supported_tokens_i) / (Σ_i w_i * total_tokens_i)
    where supported tokens are those not within unsupported spans.
    """
    num = 0.0
    den = 0.0
    for s in sentences:
        text: str = s.get("text", "")
        weight: float = s.get("weight", 1.0)
        tokens = _tokenize(text)
        total = len(tokens)
        unsupported_spans: List[Tuple[int, int]] = s.get("verifier", {}).get("unsupported_spans", [])
        unsupported_token_idxs: set[int] = set()
        for span in unsupported_spans:
            for idx in _span_token_indices(text, span):
                unsupported_token_idxs.add(idx)
        supported = total - len(unsupported_token_idxs)
        num += weight * supported
        den += weight * total
    return num / den if den else 0.0


def no_evidence_rate(sentences: List[Dict]) -> float:
    """Compute the No‑Evidence Rate (NER).

    NER = fraction of tokens with zero verifiable support, i.e., those covered
    by unsupported spans.
    """
    unsupported = 0
    total = 0
    for s in sentences:
        text: str = s.get("text", "")
        tokens = _tokenize(text)
        total += len(tokens)
        unsupported_spans: List[Tuple[int, int]] = s.get("verifier", {}).get("unsupported_spans", [])
        unsupported_token_idxs: set[int] = set()
        for span in unsupported_spans:
            unsupported_token_idxs.update(_span_token_indices(text, span))
        unsupported += len(unsupported_token_idxs)
    return unsupported / total if total else 0.0


def contradiction_rate(sentences: List[Dict]) -> float:
    """Compute the Contradiction Rate (CR).

    In this stub implementation CR is computed as the fraction of tokens
    falling inside unsupported spans labelled as contradicted.  Since our
    verifier stub does not produce a per‑span label, we treat all
    unsupported spans as unsupported but not contradicted.
    """
    # Without span-level labels, return zero for contradiction rate
    return 0.0


def calibration_error(sentences: List[Dict], num_buckets: int = 10) -> float:
    """Compute Expected Calibration Error (ECE).

    This metric compares the average predicted confidence of sentences to
    their empirical support (fraction of tokens supported).  Sentences are
    bucketed by predicted confidence.
    """
    # Bucket boundaries
    bucket_bounds = [i / num_buckets for i in range(num_buckets + 1)]
    bucket_totals = [0 for _ in range(num_buckets)]
    bucket_supports = [0.0 for _ in range(num_buckets)]
    bucket_confidences = [0.0 for _ in range(num_buckets)]
    for s in sentences:
        conf = s.get("verifier", {}).get("confidence", 0.5)
        # Determine bucket index
        idx = min(int(conf * num_buckets), num_buckets - 1)
        tokens = _tokenize(s.get("text", ""))
        total_tokens = len(tokens)
        if total_tokens == 0:
            continue
        unsupported_spans = s.get("verifier", {}).get("unsupported_spans", [])
        unsupported_token_idxs: set[int] = set()
        for span in unsupported_spans:
            unsupported_token_idxs.update(_span_token_indices(s.get("text", ""), span))
        supported_tokens = total_tokens - len(unsupported_token_idxs)
        support_fraction = supported_tokens / total_tokens
        bucket_totals[idx] += 1
        bucket_supports[idx] += support_fraction
        bucket_confidences[idx] += conf
    ece = 0.0
    total_sentences = sum(bucket_totals)
    if total_sentences == 0:
        return 0.0
    for i in range(num_buckets):
        if bucket_totals[i] == 0:
            continue
        avg_conf = bucket_confidences[i] / bucket_totals[i]
        avg_support = bucket_supports[i] / bucket_totals[i]
        ece += (bucket_totals[i] / total_sentences) * abs(avg_conf - avg_support)
    return ece


__all__ = [
    "support_weighted_accuracy",
    "no_evidence_rate",
    "contradiction_rate",
    "calibration_error",
]