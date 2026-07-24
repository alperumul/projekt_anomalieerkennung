"""Current Session 1 acceptance checks for the canonical data foundation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .canonical import (
    CANONICAL_CSV_PATH,
    CANONICAL_SHA256,
    EXPECTED_FIRST_TIMESTAMP,
    EXPECTED_LAST_TIMESTAMP,
    EXPECTED_ORIGINALLY_MISSING_COUNT,
    EXPECTED_ROW_COUNT,
    EXPECTED_SERIES_IDS,
    EXPECTED_STORED_VALUE_AT_MISSING_COUNT,
    EXPECTED_TIMESTAMP_COUNT,
    file_sha256,
    load_canonical_data,
)
from .periods import test_condition_for_timestamp, true_split_for_timestamp


@dataclass(frozen=True)
class AcceptanceSummary:
    """Machine-checkable values emitted by the Session 1 verifier."""

    sha256: str
    row_count: int
    series_ids: tuple[str, ...]
    timestamp_count: int
    first_timestamp: pd.Timestamp
    last_timestamp: pd.Timestamp
    originally_missing_count: int
    stored_value_at_missing_count: int
    split_row_counts: dict[str, int]
    condition_row_counts: dict[str, int]


def verify_acceptance_foundation(
    path: str | Path = CANONICAL_CSV_PATH,
) -> AcceptanceSummary:
    """Validate the pinned snapshot plus the frozen split/condition definitions."""

    source_path = Path(path)
    frame = load_canonical_data(source_path)

    split_names = frame["timestamp_utc"].map(true_split_for_timestamp)
    if split_names.isna().any():
        raise AssertionError("A canonical timestamp falls outside all true splits")

    condition_names = frame["timestamp_utc"].map(test_condition_for_timestamp)
    test_rows = split_names == "continuous_test"
    if condition_names.loc[test_rows].isna().any():
        raise AssertionError("A continuous-test timestamp has no reporting condition")
    if condition_names.loc[~test_rows].notna().any():
        raise AssertionError("A non-test timestamp was assigned a test condition")

    split_counts = {
        key: int(value)
        for key, value in split_names.value_counts(sort=False).to_dict().items()
    }
    expected_split_counts = {
        "training": 28 * 95,
        "validation": 28 * 48,
        "continuous_test": 28 * 192,
    }
    if split_counts != expected_split_counts:
        raise AssertionError(
            f"Unexpected true-split row counts: {split_counts!r}"
        )

    condition_counts = {
        key: int(value)
        for key, value in condition_names.dropna()
        .value_counts(sort=False)
        .to_dict()
        .items()
    }
    expected_condition_counts = {
        "condition_a": 28 * 48,
        "condition_b": 28 * 144,
    }
    if condition_counts != expected_condition_counts:
        raise AssertionError(
            f"Unexpected reporting-condition row counts: {condition_counts!r}"
        )

    timestamps = frame["timestamp_utc"]
    return AcceptanceSummary(
        sha256=file_sha256(source_path),
        row_count=len(frame),
        series_ids=tuple(sorted(frame["series_id"].unique())),
        timestamp_count=int(timestamps.nunique()),
        first_timestamp=timestamps.min(),
        last_timestamp=timestamps.max(),
        originally_missing_count=int((~frame["target_observed_mask"]).sum()),
        stored_value_at_missing_count=int(
            (frame["war_fehlend"] & frame["visitors"].notna()).sum()
        ),
        split_row_counts=split_counts,
        condition_row_counts=condition_counts,
    )


def format_summary(summary: AcceptanceSummary) -> str:
    """Format a concise human-readable successful verification report."""

    checks = (
        ("canonical_sha256", summary.sha256, CANONICAL_SHA256),
        ("rows", summary.row_count, EXPECTED_ROW_COUNT),
        ("series", len(summary.series_ids), len(EXPECTED_SERIES_IDS)),
        ("timestamps", summary.timestamp_count, EXPECTED_TIMESTAMP_COUNT),
        ("first_timestamp", summary.first_timestamp, EXPECTED_FIRST_TIMESTAMP),
        ("last_timestamp", summary.last_timestamp, EXPECTED_LAST_TIMESTAMP),
        (
            "originally_missing",
            summary.originally_missing_count,
            EXPECTED_ORIGINALLY_MISSING_COUNT,
        ),
        (
            "stored_values_at_missing",
            summary.stored_value_at_missing_count,
            EXPECTED_STORED_VALUE_AT_MISSING_COUNT,
        ),
        ("complete_grid", summary.row_count, 28 * 335),
    )
    lines = [f"PASS {name}: {actual}" for name, actual, expected in checks if actual == expected]
    if len(lines) != len(checks):
        raise AssertionError("A verifier summary differs from the frozen expectations")
    lines.extend(
        (
            f"PASS exact_series_ids: {len(summary.series_ids)} verified",
            f"PASS true_split_rows: {summary.split_row_counts!r}",
            f"PASS reporting_condition_rows: {summary.condition_row_counts!r}",
            "Session 1 acceptance foundation verified; accepted training remains gated.",
        )
    )
    return "\n".join(lines)
