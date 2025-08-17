"""Placeholder for the verifier training script.

In a production deployment this script would fine‑tune a cross‑encoder model
on FEVER/HotpotQA derived sentence–evidence pairs and save a PyTorch
checkpoint.  It could optionally support distributed training via DDP and
emit training metrics.  For the purposes of this exercise the script does
nothing beyond printing a message.
"""

import sys


def main() -> None:
    print("[verifier/train] Training routine not implemented in this stub.")


if __name__ == "__main__":
    sys.exit(main())