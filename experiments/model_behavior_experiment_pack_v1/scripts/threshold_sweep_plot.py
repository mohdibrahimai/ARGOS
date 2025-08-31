#!/usr/bin/env python3
"""
Plot precision/recall/abstain vs verifier threshold.

Inputs:
  --csv expects additional columns: threshold (float) and metrics for mode 'B3'.
You can generate such CSV by re-running eval at various thresholds or by editing.
"""
import argparse, pandas as pd, matplotlib.pyplot as plt

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--out_prefix", default="experiments/plots/threshold_sweep")
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    if "threshold" not in df.columns:
        raise SystemExit("CSV must include a 'threshold' column")

    df = df[df["mode"]=="B3"]
    df = df.groupby("threshold", as_index=False)[["citation_precision","citation_recall","abstain_rate"]].mean()

    # precision
    fig1 = plt.figure()
    plt.plot(df["threshold"], df["citation_precision"])
    plt.xlabel("Verifier threshold")
    plt.ylabel("Citation precision")
    fig1.savefig(f"{args.out_prefix}_precision.png", dpi=160)

    # recall
    fig2 = plt.figure()
    plt.plot(df["threshold"], df["citation_recall"])
    plt.xlabel("Verifier threshold")
    plt.ylabel("Citation recall")
    fig2.savefig(f"{args.out_prefix}_recall.png", dpi=160)

    # abstain
    fig3 = plt.figure()
    plt.plot(df["threshold"], df["abstain_rate"])
    plt.xlabel("Verifier threshold")
    plt.ylabel("Abstain rate")
    fig3.savefig(f"{args.out_prefix}_abstain.png", dpi=160)

if __name__ == "__main__":
    main()
