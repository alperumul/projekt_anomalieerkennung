"""Verify the locked 28-series, two-condition design contract.

This is the current design-contract command. It verifies the canonical snapshot,
the shared training and validation periods, and the separate Condition A and
Condition B reporting periods inside the overall test timeline.
"""

from __future__ import annotations

from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPOSITORY_ROOT / "src"
sys.path.insert(0, str(SOURCE_ROOT))

from anomaly_detection.verification import run_verifier_cli  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(run_verifier_cli())
