from __future__ import annotations

import pandas as pd
import pytest

from anomaly_detection.periods import (
    TEST_REPORTING_CONDITIONS,
    TRUE_SPLITS,
    test_condition_for_timestamp as condition_for_timestamp,
    true_split_for_timestamp,
)


@pytest.mark.parametrize(
    ("timestamp", "expected"),
    [
        ("2025-06-30 01:00:00+00:00", "training"),
        ("2025-07-03 23:59:59+00:00", "training"),
        ("2025-07-04 00:00:00+00:00", "validation"),
        ("2025-07-05 23:59:59+00:00", "validation"),
        ("2025-07-06 00:00:00+00:00", "continuous_test"),
        ("2025-07-13 23:59:59+00:00", "continuous_test"),
        ("2025-07-14 00:00:00+00:00", None),
    ],
)
def test_true_splits_are_half_open(timestamp: str, expected: str | None) -> None:
    assert true_split_for_timestamp(timestamp) == expected


def test_timezone_aware_boundaries_are_normalized_before_assignment() -> None:
    assert (
        true_split_for_timestamp("2025-07-04 02:00:00+02:00") == "validation"
    )


def test_timezone_naive_period_assignment_is_rejected() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        true_split_for_timestamp(pd.Timestamp("2025-07-04 00:00:00"))


def test_july_8_assigns_conditions_without_creating_a_true_split() -> None:
    before_boundary = "2025-07-07 23:59:59+00:00"
    at_boundary = "2025-07-08 00:00:00+00:00"

    assert condition_for_timestamp(before_boundary) == "condition_a"
    assert condition_for_timestamp(at_boundary) == "condition_b"
    assert true_split_for_timestamp(before_boundary) == "continuous_test"
    assert true_split_for_timestamp(at_boundary) == "continuous_test"
    assert len(TRUE_SPLITS) == 3
    assert len(TEST_REPORTING_CONDITIONS) == 2
    assert "condition_a" not in {period.name for period in TRUE_SPLITS}
    assert "condition_b" not in {period.name for period in TRUE_SPLITS}


@pytest.mark.parametrize(
    ("timestamp", "expected"),
    [
        ("2025-07-06 00:00:00+00:00", "condition_a"),
        ("2025-07-07 23:59:59+00:00", "condition_a"),
        ("2025-07-08 00:00:00+00:00", "condition_b"),
        ("2025-07-13 23:59:59+00:00", "condition_b"),
        ("2025-07-14 00:00:00+00:00", None),
        ("2025-07-05 23:59:59+00:00", None),
    ],
)
def test_reporting_conditions_are_half_open(
    timestamp: str,
    expected: str | None,
) -> None:
    assert condition_for_timestamp(timestamp) == expected
