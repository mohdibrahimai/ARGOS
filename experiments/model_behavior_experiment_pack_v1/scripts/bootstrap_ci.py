#!/usr/bin/env python3
"""
Compute bootstrapped 95% CI for mean differences between modes for a metric.
Example:
  python scripts/bootstrap_ci.py --csv experiments/runs/*.csv --metric contract_adherence --a B1 --b B0
"""
import argparse, glob, numpy as np, pandas as pd

def ci_diff(a, b, iters=10000, seed=42):
    rng = np.random.default_rng(seed)
    diffs = []
    n = min(len(a), len(b))
    for _ in range(iters):
        ai = rng.choice(a, size=n, replace=True)
        bi = rng.choice(b, size=n, replace=True)
        diffs.append(ai.mean() - bi.mean())
    diffs = np.array(diffs)
    return float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--metric", required=True)
    ap.add_argument("--a", required=True, help="mode A, e.g., B1")
    ap.add_argument("--b", required=True, help="mode B, e.g., B0")
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    a = df[df["mode"]==args.a][args.metric].astype(float).values
    b = df[df["mode"]==args.b][args.metric].astype(float).values
    lo, hi = ci_diff(a, b)
    print(f"{args.metric} | {args.a} - {args.b}: 95% CI = [{lo:.4f}, {hi:.4f}] (n={min(len(a), len(b))})")

if __name__ == "__main__":
    main()
