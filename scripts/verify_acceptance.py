"""Run the current canonical-data acceptance-verifier foundation."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPOSITORY_ROOT / "src"
sys.path.insert(0, str(SOURCE_ROOT))

from anomaly_detection.canonical import CANONICAL_CSV_PATH, DataContractError  # noqa: E402
from anomaly_detection.verification import (  # noqa: E402
    format_summary,
    verify_acceptance_foundation,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the pinned Session 1 canonical-data invariants."
    )
    parser.add_argument(
        "--data-path",
        type=Path,
        default=CANONICAL_CSV_PATH,
        help="CSV to check against the pinned canonical contract.",
    )
    arguments = parser.parse_args()

    try:
        summary = verify_acceptance_foundation(arguments.data_path)
    except (DataContractError, AssertionError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print(format_summary(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
