from __future__ import annotations

from pathlib import Path
import subprocess
import sys

from anomaly_detection.canonical import CANONICAL_CSV_PATH
from anomaly_detection.verification import verify_acceptance_foundation

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VERIFIER_PATH = REPOSITORY_ROOT / "scripts" / "verify_acceptance.py"


def test_verifier_reproduces_counts_and_boundaries() -> None:
    summary = verify_acceptance_foundation()

    assert summary.row_count == 9_380
    assert len(summary.series_ids) == 28
    assert summary.timestamp_count == 335
    assert str(summary.first_timestamp) == "2025-06-30 01:00:00+00:00"
    assert str(summary.last_timestamp) == "2025-07-13 23:00:00+00:00"
    assert summary.originally_missing_count == 2_626
    assert summary.stored_value_at_missing_count == 790
    assert summary.split_row_counts == {
        "training": 2_660,
        "validation": 1_344,
        "continuous_test": 5_376,
    }
    assert summary.condition_row_counts == {
        "condition_a": 1_344,
        "condition_b": 4_032,
    }


def test_verifier_command_runs_outside_repository_root(tmp_path: Path) -> None:
    completed = subprocess.run(
        [sys.executable, str(VERIFIER_PATH)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert "PASS canonical_sha256" in completed.stdout
    assert "PASS complete_grid: 9380" in completed.stdout
    assert "accepted training remains gated" in completed.stdout


def test_verifier_command_fails_nonzero_on_hash_mismatch(tmp_path: Path) -> None:
    changed = tmp_path / "changed.csv"
    changed.write_bytes(CANONICAL_CSV_PATH.read_bytes() + b"\n")

    completed = subprocess.run(
        [sys.executable, str(VERIFIER_PATH), "--data-path", str(changed)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )

    assert completed.returncode != 0
    assert "SHA-256 mismatch" in completed.stderr
