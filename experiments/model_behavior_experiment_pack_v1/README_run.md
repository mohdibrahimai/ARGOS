# Model Behaviour Experiment Pack (v1)

This pack gives you a same-day path to strong receipts for **experimentation** and **data→behaviour intuition** using HELMSMAN + ARGOS.

## Quickstart (Simulated Run Now, Real Integration Later)
```bash
# 1) (Optional) Create a venv and install requirements
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install pandas matplotlib numpy

# 2) Generate a simulated results CSV (deterministic with --seed)
python scripts/eval.py   --packs packs/ambiguity.jsonl,packs/refusal.jsonl,packs/multilingual.jsonl   --modes B0,B1,B2,B3   --contract contracts/clarity.yaml   --retriever configs/retriever.json   --verifier configs/verifier.json   --temperature 0.2   --seed 42   --simulate 1   --out experiments/runs/2025-09-01_helmsman-argos_ablation.csv

# 3) Make a simple text heatmap (hallucination by mode)
python scripts/plot_2x2_heatmap.py   --csv experiments/runs/2025-09-01_helmsman-argos_ablation.csv   --out experiments/plots/heatmap_hallucination.png

# 4) (Optional) Threshold sweep (edit CSV to add `threshold` per-run or re-run with varying configs)
# Then plot precision/recall/abstain vs threshold:
python scripts/threshold_sweep_plot.py   --csv experiments/runs/2025-09-01_helmsman-argos_ablation.csv   --out_prefix experiments/plots/threshold_sweep

# 5) Bootstrap CI for mean differences (e.g., adherence gain B1 vs B0)
python scripts/bootstrap_ci.py   --csv experiments/runs/2025-09-01_helmsman-argos_ablation.csv   --metric contract_adherence   --a B1 --b B0
```

## Real Integration Notes
- Replace `pseudo_metrics()` in `scripts/eval.py` with real calls to your **ARGOS** (retriever/answer/verifier) and **HELMSMAN** (contracts) pipeline.
- Ensure the output row schema remains identical to keep plotting/CI scripts working.
- Record env + SHAs in `experiments/Results.md`.

## Files Overview
- `experiments/prereg.md` — pre-registered hypotheses, metrics, analysis plan.
- `packs/*.jsonl` — ambiguity/refusal/multilingual prompts (20 each).
- `contracts/clarity.yaml` — HELMSMAN contract example.
- `configs/*.json` — ARGOS retriever/verifier configs.
- `scripts/eval.py` — evaluation harness (simulate now, integrate later).
- `scripts/plot_2x2_heatmap.py` — text heatmap for hallucination by mode.
- `scripts/threshold_sweep_plot.py` — precision/recall/abstain vs threshold.
- `scripts/bootstrap_ci.py` — bootstrap 95% CIs for mean differences.
- `experiments/runs/*.csv` — results live here.
- `experiments/plots/*.png` — plots live here.
- `experiments/Results.md`, `experiments/decisions.md` — human-readable receipts.

## License
MIT suggested for this pack (add a LICENSE file in your repo).
