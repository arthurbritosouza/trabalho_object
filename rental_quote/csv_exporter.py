from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Mapping


def export_breakdown_to_csv(breakdown: Iterable[Mapping[str, float]], filepath: str | Path) -> Path:
    """Write the monthly breakdown to a CSV file."""

    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["month", "rent", "contract", "total"]
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        for row in breakdown:
            writer.writerow(row)
    return path
