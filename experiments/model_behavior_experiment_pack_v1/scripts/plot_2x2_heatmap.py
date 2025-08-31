#!/usr/bin/env python3
"""
Create a 2×2 heatmap-style table (printed as text PNG) for hallucination rate
across retrieval/verifier combinations derived from B0..B3.

Note: uses matplotlib only, no seaborn, one plot per figure, no explicit colors.
"""
import argparse, pandas as pd, matplotlib.pyplot as plt

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--out", default="experiments/plots/heatmap_hallucination.png")
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    # Map modes to retrieval/verifier flags
    mapping = {
        "B0": (0,0),
        "B1": (0,0),  # contracts only (no retrieval/verifier) - keep separate in text
        "B2": (1,1),
        "B3": (1,1),
    }
    # Compute means by mode
    means = df.groupby("mode", as_index=False)["hallucination_rate"].mean()
    text = []
    for m in ["B0","B1","B2","B3"]:
        v = means[means["mode"]==m]["hallucination_rate"].values
        val = float(v[0]) if len(v) else float("nan")
        text.append(f"{m}: {val:.3f}")

    fig = plt.figure(figsize=(6,3))
    plt.axis("off")
    plt.text(0.01, 0.8, "Hallucination Rate by Mode", fontsize=14)
    for i, line in enumerate(text):
        plt.text(0.05, 0.6 - i*0.15, line, fontsize=12)
    plt.tight_layout()
    fig.savefig(args.out, dpi=160)

if __name__ == "__main__":
    main()
