"""Reproduce the superseded 26-series baseline retained as decision history.

This verifier predates the approved 2026-07-24 population and continuous two-condition test
structure. A PASS confirms only the previous baseline; it must not be used as verification of
the consolidated implementation handoff.

Run from the repository root:

    python scripts/verify_design_contract.py

This script audits availability and window eligibility only. It deliberately does not train a
model. A non-zero exit means the CSV or a documented contract assumption has changed and the
design must be reviewed before experiments continue.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

import numpy as np
import pandas as pd


DATA = Path("new-data/data/bad_nauheim_bereinigt.csv")
WINDOW_HOURS = 24
GAP_PATCH_MAX_HOURS = 2
EXCLUDED_AREA_SERIES = {"Innenstadt", "Kurpark"}


@dataclass(frozen=True)
class Split:
    name: str
    start: str
    end: str
    completeness_k: int


SPLITS = (
    Split("train-core", "2025-06-30 01:00:00+00:00", "2025-07-06 09:00:00+00:00", 0),
    Split("train-tail", "2025-07-06 10:00:00+00:00", "2025-07-07 23:00:00+00:00", 6),
    Split("test", "2025-07-08 00:00:00+00:00", "2025-07-13 23:00:00+00:00", 6),
)

EXPECTED_FACTS = {
    "rows_before_filter": 9_380,
    "sensors_before_filter": 28,
    "timestamps": 335,
    "rows_after_filter": 8_710,
    "sensors_after_filter": 26,
    "originally_missing": 2_456,
    "stored_interpolations_restored_to_missing": 745,
}

EXPECTED_WINDOWS = {
    ("train-core", 0): (2_988, 3_469),
    ("train-tail", 6): (373, 816),
    ("test", 6): (730, 1_158),
    ("train-tail", 4): (370, 798),
    ("test", 4): (403, 1_033),
}

EARLIER_SPLITS = (
    ("training", "2025-06-30 01:00:00+00:00", "2025-07-07 23:00:00+00:00"),
    ("validation", "2025-07-08 00:00:00+00:00", "2025-07-10 23:00:00+00:00"),
    ("test", "2025-07-11 00:00:00+00:00", "2025-07-13 23:00:00+00:00"),
)

EXPECTED_EARLIER = {
    "training": (88.0, 569, 14),
    "validation": (56.0, 0, 5),
    "test": (44.7, 0, 3),
}


def _as_bool(series: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series
    return series.astype(str).str.strip().str.lower().isin({"true", "1"})


def load_population() -> tuple[pd.DataFrame, dict[str, int]]:
    table = pd.read_csv(DATA)
    table["timestamp"] = pd.to_datetime(table["timestamp"], utc=True)
    table["war_fehlend"] = _as_bool(table["war_fehlend"])

    facts = {
        "rows_before_filter": len(table),
        "sensors_before_filter": table["name"].nunique(),
        "timestamps": table["timestamp"].nunique(),
    }

    table = table.loc[~table["name"].isin(EXCLUDED_AREA_SERIES)].copy()
    table["target_observed"] = (~table["war_fehlend"]) & table["visitors"].notna()
    facts.update(
        {
            "rows_after_filter": len(table),
            "sensors_after_filter": table["name"].nunique(),
            "originally_missing": int((~table["target_observed"]).sum()),
            "stored_interpolations_restored_to_missing": int(
                (table["war_fehlend"] & table["visitors"].notna()).sum()
            ),
        }
    )

    counts_per_sensor = table.groupby("name")["timestamp"].nunique()
    assert (counts_per_sensor == EXPECTED_FACTS["timestamps"]).all(), (
        "Every retained sensor must have the complete 335-hour grid"
    )
    assert facts == EXPECTED_FACTS, f"Dataset facts changed: {facts!r}"
    return table, facts


def patch_short_gaps(observed: np.ndarray) -> np.ndarray:
    """Make <=2-hour runs available within one split.

    Interior runs are linearly interpolated later in z-space. At a split edge, the one
    available within-split anchor is carried backward/forward. Runs with no anchor or more
    than two missing hours remain unavailable. This function tracks availability only.
    """
    available = observed.copy()
    index = 0
    while index < len(available):
        if available[index]:
            index += 1
            continue
        end = index
        while end < len(available) and not available[end]:
            end += 1
        run_length = end - index
        has_anchor = index > 0 or end < len(available)
        if run_length <= GAP_PATCH_MAX_HOURS and has_anchor:
            available[index:end] = True
        index = end
    return available


def eligible_starts(available: np.ndarray, k: int) -> np.ndarray:
    if len(available) < WINDOW_HOURS:
        return np.array([], dtype=int)
    missing = (~available).astype(int)
    cumulative = np.concatenate(([0], np.cumsum(missing)))
    missing_per_window = cumulative[WINDOW_HOURS:] - cumulative[:-WINDOW_HOURS]
    return np.flatnonzero(missing_per_window <= k)


def count_contract_windows(part: pd.DataFrame, k: int) -> tuple[int, int]:
    reconstruction_windows = 0
    scored_original_hours: set[tuple[str, pd.Timestamp]] = set()

    for sensor_name, sensor in part.groupby("name", sort=False):
        sensor = sensor.sort_values("timestamp").reset_index(drop=True)
        original = sensor["target_observed"].to_numpy(dtype=bool)
        available = patch_short_gaps(original)
        starts = eligible_starts(available, k)
        reconstruction_windows += len(starts)

        for start in starts:
            stop = start + WINDOW_HOURS
            for position in np.flatnonzero(original[start:stop]) + start:
                scored_original_hours.add((sensor_name, sensor.loc[position, "timestamp"]))

    return reconstruction_windows, len(scored_original_hours)


def count_earlier_slice(part: pd.DataFrame) -> tuple[float, int, int]:
    coverage = float(round(100 * part["target_observed"].mean(), 1))
    complete_windows = 0
    minimum_observed = WINDOW_HOURS

    for _, sensor in part.groupby("name", sort=False):
        original = sensor.sort_values("timestamp")["target_observed"].to_numpy(dtype=bool)
        if len(original) < WINDOW_HOURS:
            continue
        observed_per_window = np.convolve(
            original.astype(int), np.ones(WINDOW_HOURS, dtype=int), mode="valid"
        )
        complete_windows += int((observed_per_window == WINDOW_HOURS).sum())
        minimum_observed = min(minimum_observed, int(observed_per_window.min()))

    return coverage, complete_windows, minimum_observed


def main() -> None:
    table, facts = load_population()
    digest = sha256(DATA.read_bytes()).hexdigest()

    print(f"source: {DATA.as_posix()}")
    print(f"sha256: {digest}")
    print("dataset facts:")
    for key, value in facts.items():
        print(f"  {key}: {value}")

    print("\nautoencoder windows (reconstruction, distinct original scored hours):")
    split_by_name = {split.name: split for split in SPLITS}
    for key, expected in EXPECTED_WINDOWS.items():
        split_name, k = key
        split = split_by_name[split_name]
        part = table.loc[table["timestamp"].between(split.start, split.end)]
        actual = count_contract_windows(part, k)
        print(f"  {split_name:10s} k={k}: {actual}")
        assert actual == expected, f"Window counts changed for {split_name}, k={k}: {actual}"

    print("\nearlier rejected split (coverage %, complete windows, minimum observations):")
    for name, start, end in EARLIER_SPLITS:
        part = table.loc[table["timestamp"].between(start, end)]
        actual = count_earlier_slice(part)
        print(f"  {name:10s}: {actual}")
        assert actual == EXPECTED_EARLIER[name], f"Earlier-split facts changed for {name}: {actual}"

    print("\nPASS: all historical 26-series baseline facts reproduce.")


if __name__ == "__main__":
    main()
