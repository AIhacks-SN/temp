"""Loading, filtering and export helpers for the synthetic feedback fixture."""

from __future__ import annotations

import csv
import io
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Iterable, TextIO


REQUIRED_COLUMNS = (
    "feedback_id",
    "submitted_date",
    "product",
    "rating",
    "category",
    "comment",
)
FIXTURE_PATH = Path(__file__).resolve().parent / "data" / "product_feedback.csv"


class FixtureError(Exception):
    """A user-facing problem with the bundled feedback fixture."""


def _parse_rows(reader: csv.DictReader, error_label: str) -> list[dict[str, object]]:
    """Validate and coerce CSV rows shared by the bundled fixture and uploads."""

    columns = reader.fieldnames or []
    missing = [column for column in REQUIRED_COLUMNS if column not in columns]
    if missing:
        names = ", ".join(missing)
        raise FixtureError(f"The {error_label} is missing required columns: {names}.")

    records: list[dict[str, object]] = []
    for line_number, row in enumerate(reader, start=2):
        try:
            submitted_date = date.fromisoformat(row["submitted_date"] or "")
            rating = int(row["rating"] or "")
        except (TypeError, ValueError) as error:
            raise FixtureError(
                f"The {error_label} has an invalid date or rating on line {line_number}."
            ) from error

        if not 1 <= rating <= 5:
            raise FixtureError(f"The {error_label} has a rating outside 1-5 on line {line_number}.")

        records.append(
            {
                "feedback_id": row["feedback_id"] or "",
                "submitted_date": submitted_date.isoformat(),
                "product": row["product"] or "",
                "rating": rating,
                "category": row["category"] or "",
                "comment": row["comment"] or "",
            }
        )
    return records


def load_feedback(path: Path = FIXTURE_PATH) -> list[dict[str, object]]:
    """Load and validate feedback records from a local CSV file."""

    try:
        with path.open(newline="", encoding="utf-8") as fixture:
            return _parse_rows(csv.DictReader(fixture), "feedback fixture")
    except FileNotFoundError as error:
        raise FixtureError("The bundled feedback fixture could not be found.") from error
    except OSError as error:
        raise FixtureError("The bundled feedback fixture could not be read locally.") from error


def parse_uploaded_feedback(uploaded: TextIO | io.BytesIO) -> list[dict[str, object]]:
    """Validate and coerce feedback rows from a session-only upload.

    The caller is responsible for holding the parsed result only in memory
    (for example in Streamlit session state); this function never writes to
    disk, so an uploaded file stays session-temporary.
    """

    raw = uploaded.read()
    text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
    return _parse_rows(csv.DictReader(io.StringIO(text)), "uploaded file")


def to_csv(records: Iterable[dict[str, object]]) -> str:
    """Render feedback records back to CSV text for download."""

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=REQUIRED_COLUMNS)
    writer.writeheader()
    writer.writerows(records)
    return buffer.getvalue()


def filter_feedback(records: Iterable[dict[str, object]], products: Iterable[str]) -> list[dict[str, object]]:
    """Return records whose product is in the selected product set."""

    selected_products = set(products)
    return [record for record in records if record["product"] in selected_products]


def aggregate_by_product(records: Iterable[dict[str, object]]) -> dict[str, int]:
    """Count feedback records by product in stable product order."""

    counts = Counter(str(record["product"]) for record in records)
    return dict(sorted(counts.items()))
