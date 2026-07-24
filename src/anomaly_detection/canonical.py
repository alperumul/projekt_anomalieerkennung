"""Load and validate the pinned canonical Bad Nauheim CSV snapshot."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re

import pandas as pd

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_CSV_PATH = (
    REPOSITORY_ROOT / "new-data" / "data" / "bad_nauheim_bereinigt.csv"
)
CANONICAL_SHA256 = (
    "af807e38e63a253eea4a3639649c67744b0a34b839b80ee7c6682a55ea62991f"
)

EXPECTED_COLUMNS = (
    "timestamp",
    "name",
    "visitors",
    "avgDuration",
    "locationId",
    "lat",
    "lon",
    "war_fehlend",
)
EXPECTED_SERIES_IDS = (
    "Alicestraße 2",
    "Friedrichstraße 11",
    "Hauptstraße 36",
    "Hauptstraße 52 Marktplatz",
    "Hauptstraße 8",
    "Innenstadt",
    "Karlstraße 15",
    "Karlstraße 6",
    "Kurpark",
    "Kurpark - Eingang Kolonnaden",
    "Kurpark - Eingang Kurhaus",
    "Kurpark - Eingang Parkstraße",
    "Kurpark - Eingang Sprudelhof",
    "Kurpark - Großer Teich - Toilette",
    "Kurpark - Großer Teich Nord Ost",
    "Kurpark - Großer Teich Süd Ost",
    "Kurpark - Zentrum Süd",
    "Kurstraße 13",
    "Kurstraße 7",
    "Parkstraße 24",
    "Parkstraße 4",
    "Reinhardstraße 19",
    "Reinhardstraße 2",
    "Rosengarten",
    "Schulstraße 6",
    "Stresemannstraße 38",
    "Stresemannstraße 6",
    "Trafohaus Zanderstraße",
)

EXPECTED_ROW_COUNT = 9_380
EXPECTED_TIMESTAMP_COUNT = 335
EXPECTED_FIRST_TIMESTAMP = pd.Timestamp("2025-06-30 01:00:00+00:00")
EXPECTED_LAST_TIMESTAMP = pd.Timestamp("2025-07-13 23:00:00+00:00")
EXPECTED_ORIGINALLY_MISSING_COUNT = 2_626
EXPECTED_STORED_VALUE_AT_MISSING_COUNT = 790

_NUMERIC_COLUMNS = ("visitors", "avgDuration", "locationId", "lat", "lon")
_TIMESTAMP_PATTERN = re.compile(
    r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})"
)
_BOOLEAN_VALUES = {"true": True, "false": False}


class DataContractError(ValueError):
    """Raised when input violates the current shared data contract."""


def file_sha256(path: Path) -> str:
    """Return a lowercase SHA-256 digest without loading the whole file at once."""

    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_source(path: Path) -> pd.DataFrame:
    try:
        frame = pd.read_csv(
            path,
            dtype="string",
            keep_default_na=False,
            encoding="utf-8",
            encoding_errors="strict",
        )
    except (OSError, UnicodeError, pd.errors.ParserError) as error:
        raise DataContractError(f"Cannot read canonical CSV as UTF-8: {error}") from error

    actual_columns = tuple(frame.columns)
    if actual_columns != EXPECTED_COLUMNS:
        missing = sorted(set(EXPECTED_COLUMNS) - set(actual_columns))
        unexpected = sorted(set(actual_columns) - set(EXPECTED_COLUMNS))
        raise DataContractError(
            "Unexpected canonical CSV schema "
            f"(expected order {EXPECTED_COLUMNS!r}, missing={missing!r}, "
            f"unexpected={unexpected!r}, actual={actual_columns!r})"
        )
    return frame


def _parse_timestamps(values: pd.Series) -> pd.Series:
    malformed = ~values.str.fullmatch(_TIMESTAMP_PATTERN.pattern)
    if malformed.any():
        examples = values.loc[malformed].drop_duplicates().head(3).tolist()
        raise DataContractError(
            "Timestamps must use YYYY-MM-DD HH:MM:SS with an explicit UTC offset; "
            f"invalid values include {examples!r}"
        )

    try:
        parsed = pd.to_datetime(
            values,
            format="%Y-%m-%d %H:%M:%S%z",
            errors="raise",
            utc=True,
        )
    except (ValueError, TypeError) as error:
        raise DataContractError(f"Invalid timestamp value: {error}") from error
    return parsed


def _parse_booleans(values: pd.Series) -> pd.Series:
    normalized = values.str.strip().str.casefold()
    unknown = ~normalized.isin(_BOOLEAN_VALUES)
    if unknown.any():
        examples = values.loc[unknown].drop_duplicates().head(3).tolist()
        raise DataContractError(
            "war_fehlend contains unknown boolean values; "
            f"expected True or False, found {examples!r}"
        )
    return normalized.map(_BOOLEAN_VALUES).astype(bool)


def _parse_numeric(values: pd.Series, column: str) -> pd.Series:
    nullable = values.mask(values == "", pd.NA)
    try:
        return pd.to_numeric(nullable, errors="raise")
    except (ValueError, TypeError) as error:
        raise DataContractError(f"{column} contains a non-numeric value: {error}") from error


def _validate_snapshot(frame: pd.DataFrame) -> None:
    if frame["series_id"].isna().any() or (frame["series_id"] == "").any():
        raise DataContractError("series_id must be the non-empty canonical name value")

    duplicate_keys = frame.duplicated(["series_id", "timestamp_utc"], keep=False)
    if duplicate_keys.any():
        examples = (
            frame.loc[duplicate_keys, ["series_id", "timestamp_utc"]]
            .head(3)
            .to_dict("records")
        )
        raise DataContractError(
            "Duplicate (series_id, timestamp_utc) keys found; "
            f"examples={examples!r}"
        )

    if len(frame) != EXPECTED_ROW_COUNT:
        raise DataContractError(
            f"Expected {EXPECTED_ROW_COUNT} rows, found {len(frame)}"
        )

    actual_series = frozenset(frame["series_id"].unique())
    expected_series = frozenset(EXPECTED_SERIES_IDS)
    if actual_series != expected_series:
        raise DataContractError(
            "Unexpected series population "
            f"(missing={sorted(expected_series - actual_series)!r}, "
            f"unexpected={sorted(actual_series - expected_series)!r})"
        )

    timestamps = pd.DatetimeIndex(frame["timestamp_utc"].unique()).sort_values()
    expected_timestamps = pd.date_range(
        EXPECTED_FIRST_TIMESTAMP,
        EXPECTED_LAST_TIMESTAMP,
        freq="h",
    )
    if not timestamps.equals(expected_timestamps):
        raise DataContractError(
            "Unexpected canonical timeline "
            f"(expected {EXPECTED_TIMESTAMP_COUNT} hourly timestamps from "
            f"{EXPECTED_FIRST_TIMESTAMP} through {EXPECTED_LAST_TIMESTAMP}, "
            f"found {len(timestamps)} from "
            f"{timestamps.min() if len(timestamps) else None} through "
            f"{timestamps.max() if len(timestamps) else None})"
        )

    actual_grid = pd.MultiIndex.from_frame(
        frame[["series_id", "timestamp_utc"]]
    ).sort_values()
    expected_grid = pd.MultiIndex.from_product(
        [EXPECTED_SERIES_IDS, expected_timestamps],
        names=["series_id", "timestamp_utc"],
    ).sort_values()
    if not actual_grid.equals(expected_grid):
        raise DataContractError("Canonical data is not the complete 28 x 335 grid")

    originally_missing = int((~frame["target_observed_mask"]).sum())
    if originally_missing != EXPECTED_ORIGINALLY_MISSING_COUNT:
        raise DataContractError(
            f"Expected {EXPECTED_ORIGINALLY_MISSING_COUNT} originally missing "
            f"series-hours, found {originally_missing}"
        )

    stored_at_missing = int(
        (frame["war_fehlend"] & frame["visitors"].notna()).sum()
    )
    if stored_at_missing != EXPECTED_STORED_VALUE_AT_MISSING_COUNT:
        raise DataContractError(
            f"Expected {EXPECTED_STORED_VALUE_AT_MISSING_COUNT} stored visitor "
            f"values where war_fehlend=True, found {stored_at_missing}"
        )


def load_canonical_data(
    path: str | Path | None = None,
    *,
    expected_sha256: str = CANONICAL_SHA256,
) -> pd.DataFrame:
    """Load the canonical CSV and fail on every pinned snapshot invariant.

    ``expected_sha256`` is injectable so focused tests can reach later
    validation stages after making an intentional fixture mutation.
    """

    source_path = Path(path) if path is not None else CANONICAL_CSV_PATH
    if not source_path.is_file():
        raise DataContractError(f"Canonical CSV does not exist: {source_path}")

    actual_sha256 = file_sha256(source_path)
    if actual_sha256 != expected_sha256:
        raise DataContractError(
            "Canonical CSV SHA-256 mismatch "
            f"(expected {expected_sha256}, found {actual_sha256})"
        )

    source = _read_source(source_path)
    timestamps = _parse_timestamps(source["timestamp"])
    war_fehlend = _parse_booleans(source["war_fehlend"])

    frame = pd.DataFrame(
        {
            "timestamp_utc": timestamps,
            "series_id": source["name"].copy(),
            **{
                column: _parse_numeric(source[column], column)
                for column in _NUMERIC_COLUMNS
            },
            "war_fehlend": war_fehlend,
        }
    )
    frame["target_observed_mask"] = (
        ~frame["war_fehlend"] & frame["visitors"].notna()
    )

    _validate_snapshot(frame)
    return frame
