"""Backward-compatible alias for the current design-contract verifier."""

from __future__ import annotations

from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPOSITORY_ROOT / "src"
sys.path.insert(0, str(SOURCE_ROOT))

from anomaly_detection.verification import run_verifier_cli  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(run_verifier_cli())
