from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pandas as pd
import pytest

from anomaly_detection.canonical import CANONICAL_CSV_PATH, file_sha256


@pytest.fixture
def mutated_canonical_csv(
    tmp_path: Path,
) -> Callable[[Callable[[pd.DataFrame], pd.DataFrame]], tuple[Path, str]]:
    """Create a deliberately changed full-size CSV and return its new hash."""

    def create(
        mutation: Callable[[pd.DataFrame], pd.DataFrame],
    ) -> tuple[Path, str]:
        source = pd.read_csv(
            CANONICAL_CSV_PATH,
            dtype="string",
            keep_default_na=False,
            encoding="utf-8",
        )
        changed = mutation(source.copy())
        destination = tmp_path / "changed.csv"
        changed.to_csv(destination, index=False, encoding="utf-8")
        return destination, file_sha256(destination)

    return create
