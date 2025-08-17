"""Fetch the FEVER dataset and save it under the seeds directory.

This script downloads the FEVER dataset from its official source and writes
JSON lines files into the `seeds/data/fever` directory.  Only a small subset
may be downloaded by default for demonstration purposes.

In this stub implementation the script merely prints a notice.  In a real
deployment you would implement actual dataset download and extraction here.
"""

import sys


def main() -> None:
    print("[fetch_fever] Dataset download not implemented in this stub.")


if __name__ == "__main__":
    sys.exit(main())