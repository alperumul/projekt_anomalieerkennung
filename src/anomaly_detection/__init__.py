"""Shared foundations for the Bad Nauheim anomaly-detection study."""

from .canonical import (
    CANONICAL_CSV_PATH,
    CANONICAL_SHA256,
    DataContractError,
    load_canonical_data,
)

__all__ = [
    "CANONICAL_CSV_PATH",
    "CANONICAL_SHA256",
    "DataContractError",
    "load_canonical_data",
]
