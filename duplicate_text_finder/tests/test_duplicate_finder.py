"""Comprehensive automated test suite for Duplicate Text Finder."""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path

from app import create_app
from app.analytics import generate_summary_metrics
from app.detector import detect_exact_duplicates, find_near_variant_hints
from app.storage import StorageManager
from app.validator import validate_batch_lines, validate_record_input


class DuplicateTextFinderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="dtf_test_"))
        self.project_data_dir = Path(__file__).resolve().parent.parent / "data"
        # Copy sample datasets into temp test directory for isolated testing
        shutil.copy2(self.project_data_dir / "sample_dataset.json", self.temp_dir / "sample_dataset.json")
        shutil.copy2(self.project_data_dir / "sample_dataset.csv", self.temp_dir / "sample_dataset.csv")

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # 1. Defensive Input Validation
    def test_validation_rejects_invalid_types_and_boundaries(self) -> None:
        blank_res = validate_record_input({"text": "   \t  ", "category": "General"})
        self.assertFalse(blank_res.is_valid)
        self.assertIn("text", blank_res.errors)

        bool_pri = validate_record_input({"text": "Hello", "category": "General", "priority": True})
        self.assertFalse(bool_pri.is_valid)
        self.assertIn("priority", bool_pri.errors)

        oob_pri = validate_record_input({"text": "Hello", "category": "General", "priority": 99})
        self.assertFalse(oob_pri.is_valid)
        self.assertIn("priority", oob_pri.errors)

        bad_date = validate_record_input({"text": "Hello", "category": "General", "due_date": "2026-02-30"})
        self.assertFalse(bad_date.is_valid)
        self.assertIn("due_date", bad_date.errors)

        bad_cat = validate_record_input({"text": "Hello", "category": "Bad@Cat!"})
        self.assertFalse(bad_cat.is_valid)
        self.assertIn("category", bad_cat.errors)

        non_dict = validate_record_input(["not", "a", "dict"])
        self.assertFalse(non_dict.is_valid)

    def test_validation_sanitizes_control_chars_and_accepts_boundaries(self) -> None:
        res = validate_record_input(
            {
                "text": "A\x00B",
                "category": "General",
                "priority": "1",
                "due_date": "2026-12-31",
            }
        )
        self.assertTrue(res.is_valid)
        self.assertEqual(res.sanitized_data["text"], "AB")
        self.assertEqual(res.sanitized_data["priority"], 1)

        batch_err = validate_batch_lines("   \n   ")
        self.assertFalse(batch_err.is_valid)

    # 2. Core Exact Duplicate Detection Engine
    def test_exact_duplicate_detection_distinguishes_variants(self) -> None:
        entries = [
            "Order #1024",
            "Order #1024",
            "order #1024",
            "Order #1024 ",
            "Unique Item",
        ]
        report = detect_exact_duplicates(entries)
        self.assertEqual(report.total_entries, 5)
        self.assertEqual(report.duplicate_entry_count, 2)
        self.assertEqual(report.unique_only_count, 3)
        self.assertEqual(report.distinct_duplicate_groups, 1)
        self.assertEqual(report.redundant_copy_count, 1)
        self.assertEqual(report.duplicate_groups[0].text, "Order #1024")

        hints = find_near_variant_hints(entries)
        self.assertEqual(len(hints), 1)
        self.assertEqual(hints[0]["variant_count"], 3)

    # 3. Persistence & Corrupted File Recovery
    def test_missing_and_corrupted_storage_recovery(self) -> None:
        storage = StorageManager(self.temp_dir)
        records, status = storage.load_records()
        self.assertEqual(records, [])
        self.assertTrue(status["json_exists"])
        self.assertTrue(status["csv_exists"])
        self.assertTrue(status["recovered"])

        # Add record and verify persistence across new StorageManager instance
        created = storage.add_record({"text": "Persistent record", "category": "General", "priority": 3})
        storage2 = StorageManager(self.temp_dir)
        reloaded, _ = storage2.load_records()
        self.assertEqual(len(reloaded), 1)
        self.assertEqual(reloaded[0].record_id, created.record_id)

        # Corrupt JSON; verify automatic recovery from CSV without crash
        (self.temp_dir / "records.json").write_text("{corrupted json", encoding="utf-8")
        recovered_recs, rec_status = storage2.load_records()
        self.assertEqual(len(recovered_recs), 1)
        self.assertTrue(rec_status["recovered"])

        # Corrupt both JSON and CSV; verify clean template recreation
        (self.temp_dir / "records.json").write_text("not-json", encoding="utf-8")
        (self.temp_dir / "records.csv").write_text("bad_col1,bad_col2\n1,2\n", encoding="utf-8")
        empty_recs, both_status = storage2.load_records()
        self.assertEqual(empty_recs, [])
        self.assertTrue(both_status["recovered"])

    # 4. Sample Dataset + Analytics + Warnings + Charts + Exports + Bulk Import via Flask
    def test_end_to_end_flask_workflow(self) -> None:
        app = create_app(data_dir=self.temp_dir)
        client = app.test_client()

        # Verify welcome page renders cleanly
        home_res = client.get("/")
        self.assertEqual(home_res.status_code, 200)
        self.assertIn(b"Duplicate Text Finder", home_res.data)

        # Verify batch detection endpoint
        batch_res = client.post(
            "/api/detect/batch",
            json={"batch_text": "alpha\nbeta\nalpha\nAlpha", "save_to_storage": False},
        )
        self.assertEqual(batch_res.status_code, 200)
        self.assertEqual(batch_res.get_json()["report"]["duplicate_entry_count"], 2)
        self.assertEqual(batch_res.get_json()["report"]["unique_only_count"], 2)

        # Load 40-entry sample dataset
        seed_res = client.post("/api/storage/load-sample", json={"replace": True})
        self.assertEqual(seed_res.status_code, 200)
        self.assertEqual(seed_res.get_json()["count"], 40)

        # Verify invalid POST returns 400 and does not crash or corrupt storage
        bad_post = client.post("/api/records", json={"text": "   ", "category": "General", "priority": "abc"})
        self.assertEqual(bad_post.status_code, 400)
        self.assertIn("text", bad_post.get_json()["errors"])
        self.assertIn("priority", bad_post.get_json()["errors"])

        # Add valid new entry
        good_post = client.post(
            "/api/records",
            json={
                "text": "alice.chen@example.com",
                "category": "Customer",
                "priority": 4,
                "due_date": "2026-12-25",
            },
        )
        self.assertEqual(good_post.status_code, 201)
        self.assertTrue(good_post.get_json()["analysis"]["is_duplicate"])

        # Simulate app restart by creating a new Flask app pointing to same data_dir
        restarted_app = create_app(data_dir=self.temp_dir)
        restarted_client = restarted_app.test_client()

        health = restarted_client.get("/api/health").get_json()
        self.assertEqual(health["record_count"], 41)

        # Query & Search
        search_res = restarted_client.get("/api/records?keyword=gateway&category=Log&status=duplicate&page=1&per_page=10")
        self.assertEqual(search_res.status_code, 200)
        search_data = search_res.get_json()
        self.assertEqual(search_data["pagination"]["total_matched"], 4)

        # Analytics & Warnings
        analytics_res = restarted_client.get("/api/analytics")
        self.assertEqual(analytics_res.status_code, 200)
        metrics = analytics_res.get_json()["metrics"]
        self.assertEqual(metrics["total_records"], 41)
        self.assertGreater(metrics["duplicate_entries"], 0)
        self.assertGreater(len(metrics["warnings"]), 0)

        # Matplotlib Charts
        for kind in ("distribution", "categories", "trends"):
            chart_res = restarted_client.get(f"/api/charts/{kind}.png")
            self.assertEqual(chart_res.status_code, 200)
            self.assertEqual(chart_res.mimetype, "image/png")
            self.assertTrue(chart_res.data.startswith(b"\x89PNG\r\n\x1a\n"))

        # Multi-format Exports
        for fmt in ("markdown", "txt", "csv"):
            exp_res = restarted_client.get(f"/api/export/{fmt}")
            self.assertEqual(exp_res.status_code, 200)
            self.assertGreater(len(exp_res.data), 100)

        # Bulk CSV Import with mixed valid + invalid rows
        sample_bulk_path = self.project_data_dir / "sample_bulk_import_test.csv"
        with sample_bulk_path.open("rb") as fh:
            import_res = restarted_client.post(
                "/api/import/csv",
                data={"file": (fh, "sample_bulk_import_test.csv"), "dry_run": "false"},
                content_type="multipart/form-data",
            )
        self.assertEqual(import_res.status_code, 200)
        imp_report = import_res.get_json()["report"]
        self.assertEqual(imp_report["total_rows"], 10)
        self.assertEqual(imp_report["valid_count"], 5)
        self.assertEqual(imp_report["invalid_count"], 5)
        self.assertEqual(len(imp_report["row_errors"]), 5)

        # Verify storage now has 41 + 5 = 46 records
        final_health = restarted_client.get("/api/health").get_json()
        self.assertEqual(final_health["record_count"], 46)

    def test_empty_dataset_charts_and_metrics(self) -> None:
        app = create_app(data_dir=self.temp_dir)
        client = app.test_client()
        res = client.get("/api/charts/distribution.png")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data.startswith(b"\x89PNG\r\n\x1a\n"))

        summary = generate_summary_metrics([], reference_date=date(2026, 11, 26))
        self.assertEqual(summary.total_records, 0)
        self.assertEqual(summary.status_label, "Empty Dataset")


if __name__ == "__main__":
    unittest.main()
