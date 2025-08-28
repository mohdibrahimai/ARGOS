import os; os.makedirs("artifacts", exist_ok=True)
open("artifacts/summary.md","w",encoding="utf-8").write(
    "## python-services\nBaseline pass. Add Makefile:ci or run_demo later."
)
print("Wrote artifacts/summary.md")
