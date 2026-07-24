from __future__ import annotations

from pathlib import Path

from anomaly_detection.canonical import CANONICAL_CSV_PATH
from anomaly_detection.verification import (
    run_verifier_cli,
    verify_acceptance_foundation,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DESIGN_VERIFIER_PATH = REPOSITORY_ROOT / "scripts" / "verify_design_contract.py"
COMPATIBILITY_VERIFIER_PATH = REPOSITORY_ROOT / "scripts" / "verify_acceptance.py"


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


def test_verifier_command_runs_outside_repository_root(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.chdir(tmp_path)

    return_code = run_verifier_cli([])
    captured = capsys.readouterr()

    assert return_code == 0, captured.err
    assert "PASS canonical_sha256" in captured.out
    assert "PASS complete_grid: 9380" in captured.out
    assert (
        "PASS true_split_rows: "
        "{'training': 2660, 'validation': 1344, 'continuous_test': 5376}"
        in captured.out
    )
    assert (
        "PASS reporting_condition_rows: "
        "{'condition_a': 1344, 'condition_b': 4032}"
        in captured.out
    )
    assert "accepted training remains gated" in captured.out


def test_verifier_command_fails_nonzero_on_hash_mismatch(
    tmp_path: Path,
    capsys,
) -> None:
    changed = tmp_path / "changed.csv"
    changed.write_bytes(CANONICAL_CSV_PATH.read_bytes() + b"\n")

    return_code = run_verifier_cli(["--data-path", str(changed)])
    captured = capsys.readouterr()

    assert return_code != 0
    assert "SHA-256 mismatch" in captured.err


def test_current_verifier_entry_points_do_not_encode_superseded_splits() -> None:
    for verifier_path in (DESIGN_VERIFIER_PATH, COMPATIBILITY_VERIFIER_PATH):
        source = verifier_path.read_text(encoding="utf-8")

        assert "train-core" not in source
        assert "train-tail" not in source
        assert "SPLITS =" not in source
        assert "run_verifier_cli" in source
