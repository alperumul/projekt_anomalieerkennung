from __future__ import annotations

from pathlib import Path
import shutil

import pandas as pd
import pytest

from anomaly_detection.canonical import (
    CANONICAL_CSV_PATH,
    CANONICAL_SHA256,
    EXPECTED_COLUMNS,
    EXPECTED_FIRST_TIMESTAMP,
    EXPECTED_LAST_TIMESTAMP,
    EXPECTED_SERIES_IDS,
    DataContractError,
    file_sha256,
    load_canonical_data,
)


def test_loads_exact_canonical_snapshot() -> None:
    frame = load_canonical_data()

    assert len(frame) == 9_380
    assert frame["series_id"].nunique() == 28
    assert frame["timestamp_utc"].nunique() == 335
    assert frame["timestamp_utc"].min() == EXPECTED_FIRST_TIMESTAMP
    assert frame["timestamp_utc"].max() == EXPECTED_LAST_TIMESTAMP
    assert str(frame["timestamp_utc"].dt.tz) == "UTC"
    assert int((~frame["target_observed_mask"]).sum()) == 2_626
    assert int((frame["war_fehlend"] & frame["visitors"].notna()).sum()) == 790
    assert not frame.duplicated(["series_id", "timestamp_utc"]).any()
    assert len(frame) == 28 * 335


def test_preserves_exact_unicode_series_identity() -> None:
    frame = load_canonical_data()

    assert frozenset(frame["series_id"]) == frozenset(EXPECTED_SERIES_IDS)
    assert "Alicestraße 2" in frozenset(frame["series_id"])
    assert "Kurpark - Eingang Parkstraße" in frozenset(frame["series_id"])
    assert "Innenstadt" in frozenset(frame["series_id"])
    assert "Kurpark" in frozenset(frame["series_id"])


def test_target_observed_mask_uses_flag_and_visitor_presence() -> None:
    frame = load_canonical_data()
    expected = ~frame["war_fehlend"] & frame["visitors"].notna()

    pd.testing.assert_series_equal(
        frame["target_observed_mask"],
        expected,
        check_names=False,
    )
    stored_values = frame["war_fehlend"] & frame["visitors"].notna()
    assert int(stored_values.sum()) == 790
    assert not frame.loc[stored_values, "target_observed_mask"].any()


def test_rejects_hash_mismatch(tmp_path: Path) -> None:
    changed = tmp_path / "changed.csv"
    shutil.copyfile(CANONICAL_CSV_PATH, changed)
    with changed.open("a", encoding="utf-8") as handle:
        handle.write("\n")

    with pytest.raises(DataContractError, match="SHA-256 mismatch"):
        load_canonical_data(changed)


@pytest.mark.parametrize("kind", ["missing", "unexpected"])
def test_rejects_missing_or_unexpected_columns(
    mutated_canonical_csv,
    kind: str,
) -> None:
    def change(frame: pd.DataFrame) -> pd.DataFrame:
        if kind == "missing":
            return frame.drop(columns=[EXPECTED_COLUMNS[-1]])
        frame["unexpected"] = "not-authoritative"
        return frame

    path, changed_hash = mutated_canonical_csv(change)

    with pytest.raises(DataContractError, match="schema"):
        load_canonical_data(path, expected_sha256=changed_hash)


def test_rejects_unknown_boolean_values(mutated_canonical_csv) -> None:
    def change(frame: pd.DataFrame) -> pd.DataFrame:
        frame.loc[0, "war_fehlend"] = "unknown"
        return frame

    path, changed_hash = mutated_canonical_csv(change)

    with pytest.raises(DataContractError, match="unknown boolean"):
        load_canonical_data(path, expected_sha256=changed_hash)


@pytest.mark.parametrize(
    "invalid_timestamp",
    ["not-a-timestamp", "2025-06-30 01:00:00"],
)
def test_rejects_invalid_or_timezone_naive_timestamps(
    mutated_canonical_csv,
    invalid_timestamp: str,
) -> None:
    def change(frame: pd.DataFrame) -> pd.DataFrame:
        frame.loc[0, "timestamp"] = invalid_timestamp
        return frame

    path, changed_hash = mutated_canonical_csv(change)

    with pytest.raises(DataContractError, match="Timestamps must"):
        load_canonical_data(path, expected_sha256=changed_hash)


def test_normalizes_explicit_non_utc_offset(mutated_canonical_csv) -> None:
    def change(frame: pd.DataFrame) -> pd.DataFrame:
        frame.loc[0, "timestamp"] = "2025-06-30 03:00:00+02:00"
        return frame

    path, changed_hash = mutated_canonical_csv(change)
    loaded = load_canonical_data(path, expected_sha256=changed_hash)

    assert loaded.loc[0, "timestamp_utc"] == EXPECTED_FIRST_TIMESTAMP
    assert str(loaded["timestamp_utc"].dt.tz) == "UTC"


def test_rejects_duplicate_series_hour_keys(mutated_canonical_csv) -> None:
    def change(frame: pd.DataFrame) -> pd.DataFrame:
        return pd.concat([frame, frame.iloc[[0]]], ignore_index=True)

    path, changed_hash = mutated_canonical_csv(change)

    with pytest.raises(DataContractError, match="Duplicate"):
        load_canonical_data(path, expected_sha256=changed_hash)


def test_rejects_changed_series_population(mutated_canonical_csv) -> None:
    def change(frame: pd.DataFrame) -> pd.DataFrame:
        frame.loc[frame["name"] == "Innenstadt", "name"] = "Innenstadt "
        return frame

    path, changed_hash = mutated_canonical_csv(change)

    with pytest.raises(DataContractError, match="series population"):
        load_canonical_data(path, expected_sha256=changed_hash)


def test_repository_relative_path_does_not_depend_on_working_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    frame = load_canonical_data()

    assert len(frame) == 9_380
    assert file_sha256(CANONICAL_CSV_PATH) == CANONICAL_SHA256
