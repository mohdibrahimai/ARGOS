"""Placeholder for ONNX export of the verifier model.

In a full implementation this script would load a trained PyTorch model
checkpoint and export it to ONNX format with dynamic axes, writing the
result into the Triton model repository.  Here we simply create a dummy
ONNX file to satisfy the repository structure.
"""

import os
import sys


def main() -> None:
    output_path = os.getenv("ONNX_OUTPUT", "verifier.onnx")
    # Write a tiny dummy file
    with open(output_path, "wb") as f:
        f.write(b"ONNX_PLACEHOLDER")
    print(f"[verifier/onnx_export] Wrote dummy ONNX model to {output_path}")


if __name__ == "__main__":
    sys.exit(main())