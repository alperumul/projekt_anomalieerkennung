"""UTC true-split and reporting-condition definitions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import pandas as pd


@dataclass(frozen=True)
class UtcPeriod:
    """A named half-open UTC period."""

    name: str
    start: pd.Timestamp
    end: pd.Timestamp

    def contains(self, timestamp: str | datetime | pd.Timestamp) -> bool:
        value = normalize_utc_timestamp(timestamp)
        return self.start <= value < self.end


TRAINING = UtcPeriod(
    "training",
    pd.Timestamp("2025-06-30 01:00:00+00:00"),
    pd.Timestamp("2025-07-04 00:00:00+00:00"),
)
VALIDATION = UtcPeriod(
    "validation",
    pd.Timestamp("2025-07-04 00:00:00+00:00"),
    pd.Timestamp("2025-07-06 00:00:00+00:00"),
)
CONTINUOUS_TEST = UtcPeriod(
    "continuous_test",
    pd.Timestamp("2025-07-06 00:00:00+00:00"),
    pd.Timestamp("2025-07-14 00:00:00+00:00"),
)

CONDITION_A = UtcPeriod(
    "condition_a",
    CONTINUOUS_TEST.start,
    pd.Timestamp("2025-07-08 00:00:00+00:00"),
)
CONDITION_B = UtcPeriod(
    "condition_b",
    CONDITION_A.end,
    CONTINUOUS_TEST.end,
)

TRUE_SPLITS = (TRAINING, VALIDATION, CONTINUOUS_TEST)
TEST_REPORTING_CONDITIONS = (CONDITION_A, CONDITION_B)


def normalize_utc_timestamp(
    timestamp: str | datetime | pd.Timestamp,
) -> pd.Timestamp:
    """Require timezone information and normalize an instant to UTC."""

    value = pd.Timestamp(timestamp)
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"Timestamp must be timezone-aware: {timestamp!r}")
    return value.tz_convert("UTC")


def true_split_for_timestamp(
    timestamp: str | datetime | pd.Timestamp,
) -> str | None:
    """Return the true split name, or ``None`` when outside the study timeline."""

    for period in TRUE_SPLITS:
        if period.contains(timestamp):
            return period.name
    return None


def test_condition_for_timestamp(
    timestamp: str | datetime | pd.Timestamp,
) -> str | None:
    """Return the reporting condition inside the single continuous test split."""

    for condition in TEST_REPORTING_CONDITIONS:
        if condition.contains(timestamp):
            return condition.name
    return None
