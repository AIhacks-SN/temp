import csv
import io
import tempfile
import unittest
from pathlib import Path

from feedback import (
    FixtureError,
    aggregate_by_product,
    filter_feedback,
    load_feedback,
    parse_uploaded_feedback,
    to_csv,
)


class FeedbackTests(unittest.TestCase):
    def test_loads_valid_bundled_fixture(self):
        records = load_feedback()

        self.assertEqual(len(records), 12)
        self.assertEqual({record["product"] for record in records}, {"Atlas Notes", "Beacon Boards", "Cloudberry Calendar"})

    def test_rejects_missing_required_column(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.csv"
            with path.open("w", newline="", encoding="utf-8") as fixture:
                writer = csv.writer(fixture)
                writer.writerow(["feedback_id", "product"])
                writer.writerow(["FB-001", "Atlas Notes"])

            with self.assertRaisesRegex(FixtureError, "missing required columns"):
                load_feedback(path)

    def test_product_filter_reduces_rows_and_changes_aggregate(self):
        records = load_feedback()
        filtered = filter_feedback(records, ["Atlas Notes"])

        self.assertLess(len(filtered), len(records))
        self.assertEqual(aggregate_by_product(records), {"Atlas Notes": 4, "Beacon Boards": 4, "Cloudberry Calendar": 4})
        self.assertEqual(aggregate_by_product(filtered), {"Atlas Notes": 4})

    def test_parse_uploaded_feedback_accepts_valid_csv(self):
        upload = io.StringIO(
            "feedback_id,submitted_date,product,rating,category,comment\n"
            "FB-101,2026-05-01,Atlas Notes,4,usability,Great import experience.\n"
        )

        records = parse_uploaded_feedback(upload)

        self.assertEqual(records, [
            {
                "feedback_id": "FB-101",
                "submitted_date": "2026-05-01",
                "product": "Atlas Notes",
                "rating": 4,
                "category": "usability",
                "comment": "Great import experience.",
            }
        ])

    def test_parse_uploaded_feedback_rejects_missing_column(self):
        upload = io.StringIO("feedback_id,product\nFB-101,Atlas Notes\n")

        with self.assertRaisesRegex(FixtureError, "uploaded file is missing required columns"):
            parse_uploaded_feedback(upload)

    def test_to_csv_round_trips_through_parse_uploaded_feedback(self):
        records = load_feedback()

        rendered = to_csv(records)

        self.assertEqual(parse_uploaded_feedback(io.StringIO(rendered)), records)


if __name__ == "__main__":
    unittest.main()
