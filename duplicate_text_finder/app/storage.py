"""Local CSV and JSON persistence with schema validation and fault-tolerant recovery."""

from __future__ import annotations

import csv
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from app.models import (
    CSV_FIELDNAMES,
    DEFAULT_THRESHOLDS,
    SCHEMA_VERSION,
    TextRecord,
)
from app.validator import validate_record_input, validate_thresholds


class StorageManager:
    """Manages synchronized CSV and JSON storage with automatic recovery templates."""

    def __init__(self, data_dir: Path | str) -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.json_path = self.data_dir / "records.json"
        self.csv_path = self.data_dir / "records.csv"
        self.thresholds_path = self.data_dir / "thresholds.json"
        self.sample_json_path = self.data_dir / "sample_dataset.json"
        self.sample_csv_path = self.data_dir / "sample_dataset.csv"

    def _now_iso(self) -> str:
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    def _backup_corrupted_file(self, path: Path) -> str | None:
        """Preserve a corrupted file as a timestamped backup before recreating clean template."""
        if not path.exists():
            return None
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = path.with_name(f"{path.name}.corrupted_{stamp}.bak")
        try:
            shutil.copy2(path, backup_path)
            return backup_path.name
        except OSError:
            return None

    def create_clean_json_template(self, records: list[TextRecord] | None = None) -> None:
        """Write a clean JSON storage file matching the expected schema."""
        payload = {
            "schema_version": SCHEMA_VERSION,
            "updated_at": self._now_iso(),
            "records": [r.to_dict() for r in (records or [])],
        }
        tmp_path = self.json_path.with_suffix(".json.tmp")
        with tmp_path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
        tmp_path.replace(self.json_path)

    def create_clean_csv_template(self, records: list[TextRecord] | None = None) -> None:
        """Write a clean CSV storage file with standard header and rows."""
        tmp_path = self.csv_path.with_suffix(".csv.tmp")
        with tmp_path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(CSV_FIELDNAMES))
            writer.writeheader()
            for record in records or []:
                writer.writerow(record.to_dict())
        tmp_path.replace(self.csv_path)

    def _validate_record_dict(self, raw: Any) -> tuple[TextRecord | None, dict[str, str] | None]:
        """Validate a deserialized record dictionary against the TextRecord schema."""
        result = validate_record_input(raw, require_record_id=True, require_created_at=True)
        if not result.is_valid:
            return None, result.errors
        data = result.sanitized_data
        record = TextRecord(
            record_id=data["record_id"],
            text=data["text"],
            category=data["category"],
            source=data["source"],
            priority=int(data["priority"]),
            due_date=data.get("due_date", ""),
            notes=data.get("notes", ""),
            created_at=data["created_at"],
        )
        return record, None

    def _read_json_records(self) -> tuple[list[TextRecord] | None, list[str], int]:
        """Attempt to load and schema-validate records from records.json."""
        events: list[str] = []
        skipped_invalid = 0
        try:
            with self.json_path.open("r", encoding="utf-8") as fh:
                content = fh.read()
            if not content.strip():
                raise json.JSONDecodeError("Empty JSON file", content, 0)
            payload = json.loads(content)
        except FileNotFoundError:
            events.append("records.json was missing; initialized clean JSON storage template.")
            return None, events, skipped_invalid
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            backup = self._backup_corrupted_file(self.json_path)
            suffix = f" (backed up to {backup})" if backup else ""
            events.append(f"records.json was corrupted ({exc.__class__.__name__}){suffix}; recreated clean template.")
            return None, events, skipped_invalid
        except OSError as exc:
            events.append(f"Error reading records.json ({exc}); attempting recovery.")
            return None, events, skipped_invalid

        if not isinstance(payload, dict) or not isinstance(payload.get("records"), list):
            backup = self._backup_corrupted_file(self.json_path)
            suffix = f" (backed up to {backup})" if backup else ""
            events.append(f"records.json failed schema validation{suffix}; recreated clean template.")
            return None, events, skipped_invalid

        valid_records: list[TextRecord] = []
        seen_ids: set[str] = set()
        for item in payload["records"]:
            rec, _err = self._validate_record_dict(item)
            if rec is None or rec.record_id in seen_ids:
                skipped_invalid += 1
                continue
            seen_ids.add(rec.record_id)
            valid_records.append(rec)

        if skipped_invalid > 0:
            events.append(f"Skipped {skipped_invalid} schema-invalid or duplicate-ID record(s) in records.json.")
        return valid_records, events, skipped_invalid

    def _read_csv_records(self) -> tuple[list[TextRecord] | None, list[str], int]:
        """Attempt to load and schema-validate records from records.csv."""
        events: list[str] = []
        skipped_invalid = 0
        try:
            with self.csv_path.open("r", encoding="utf-8", newline="") as fh:
                reader = csv.DictReader(fh)
                fieldnames = reader.fieldnames
                if not fieldnames or not set(CSV_FIELDNAMES).issubset(set(fieldnames)):
                    raise csv.Error("Missing required CSV header columns")
                rows = list(reader)
        except FileNotFoundError:
            events.append("records.csv was missing; initialized clean CSV storage template.")
            return None, events, skipped_invalid
        except (csv.Error, UnicodeDecodeError, OSError) as exc:
            backup = self._backup_corrupted_file(self.csv_path)
            suffix = f" (backed up to {backup})" if backup else ""
            events.append(f"records.csv was invalid/corrupted ({exc}){suffix}; recreated clean template.")
            return None, events, skipped_invalid

        valid_records: list[TextRecord] = []
        seen_ids: set[str] = set()
        for row in rows:
            rec, _err = self._validate_record_dict(row)
            if rec is None or rec.record_id in seen_ids:
                skipped_invalid += 1
                continue
            seen_ids.add(rec.record_id)
            valid_records.append(rec)

        if skipped_invalid > 0:
            events.append(f"Skipped {skipped_invalid} schema-invalid row(s) in records.csv.")
        return valid_records, events, skipped_invalid

    def load_records(self) -> tuple[list[TextRecord], dict[str, Any]]:
        """Load records reliably from JSON/CSV storage, recovering cleanly from errors."""
        json_records, json_events, json_skipped = self._read_json_records()
        csv_records, csv_events, csv_skipped = self._read_csv_records()

        events: list[str] = [*json_events, *csv_events]
        status: dict[str, Any] = {
            "json_exists": self.json_path.exists(),
            "csv_exists": self.csv_path.exists(),
            "schema_version": SCHEMA_VERSION,
            "recovery_events": events,
            "skipped_invalid_rows": json_skipped + csv_skipped,
            "recovered": len(events) > 0,
        }

        if json_records is not None:
            records = json_records
            if csv_records is None or len(csv_records) != len(json_records):
                self.create_clean_csv_template(records)
                if csv_records is not None:
                    events.append("Synchronized records.csv with records.json.")
            status["active_source"] = "records.json"
        elif csv_records is not None:
            records = csv_records
            self.create_clean_json_template(records)
            events.append("Recovered records.json from records.csv.")
            status["active_source"] = "records.csv (recovered)"
        else:
            records = []
            self.create_clean_json_template([])
            self.create_clean_csv_template([])
            status["active_source"] = "clean_template"

        status["json_exists"] = self.json_path.exists()
        status["csv_exists"] = self.csv_path.exists()
        status["record_count"] = len(records)
        return records, status

    def save_records(self, records: list[TextRecord]) -> None:
        """Persist the full record list to both JSON and CSV files."""
        self.create_clean_json_template(records)
        self.create_clean_csv_template(records)

    def generate_next_id(self, existing_records: list[TextRecord]) -> str:
        """Generate the next sequential DTF-XXXX record ID."""
        max_num = 0
        for rec in existing_records:
            if rec.record_id.startswith("DTF-"):
                suffix = rec.record_id[4:]
                if suffix.isdigit():
                    max_num = max(max_num, int(suffix))
        return f"DTF-{max_num + 1:04d}"

    def add_record(self, validated_data: dict[str, Any]) -> TextRecord:
        """Create a new TextRecord from validated data and persist to CSV & JSON."""
        records, _ = self.load_records()
        record_id = validated_data.get("record_id") or self.generate_next_id(records)
        existing_ids = {r.record_id for r in records}
        while record_id in existing_ids:
            record_id = self.generate_next_id(records)

        new_record = TextRecord(
            record_id=record_id,
            text=validated_data["text"],
            category=validated_data["category"],
            source=validated_data.get("source", "Manual Entry"),
            priority=int(validated_data.get("priority", 3)),
            due_date=validated_data.get("due_date", ""),
            notes=validated_data.get("notes", ""),
            created_at=validated_data.get("created_at") or self._now_iso(),
        )
        records.append(new_record)
        self.save_records(records)
        return new_record

    def append_records(self, validated_items: list[dict[str, Any]]) -> list[TextRecord]:
        """Append multiple validated records in one atomic CSV + JSON write."""
        records, _ = self.load_records()
        created: list[TextRecord] = []
        existing_ids = {r.record_id for r in records}
        next_num = 0
        for rec in records:
            if rec.record_id.startswith("DTF-") and rec.record_id[4:].isdigit():
                next_num = max(next_num, int(rec.record_id[4:]))

        for item in validated_items:
            candidate_id = item.get("record_id")
            if not candidate_id or candidate_id in existing_ids:
                next_num += 1
                candidate_id = f"DTF-{next_num:04d}"
                while candidate_id in existing_ids:
                    next_num += 1
                    candidate_id = f"DTF-{next_num:04d}"
            existing_ids.add(candidate_id)

            new_rec = TextRecord(
                record_id=candidate_id,
                text=item["text"],
                category=item["category"],
                source=item.get("source", "CSV Import"),
                priority=int(item.get("priority", 3)),
                due_date=item.get("due_date", ""),
                notes=item.get("notes", ""),
                created_at=item.get("created_at") or self._now_iso(),
            )
            records.append(new_rec)
            created.append(new_rec)

        self.save_records(records)
        return created

    def delete_record(self, record_id: str) -> bool:
        """Delete a record by record_id and update CSV & JSON storage."""
        records, _ = self.load_records()
        remaining = [r for r in records if r.record_id != record_id]
        if len(remaining) == len(records):
            return False
        self.save_records(remaining)
        return True

    def clear_records(self) -> int:
        """Remove all stored records and reset clean CSV & JSON templates."""
        records, _ = self.load_records()
        count = len(records)
        self.save_records([])
        return count

    def load_sample_dataset(self, *, replace: bool = True) -> tuple[int, list[str]]:
        """Load the bundled sample dataset (JSON or CSV) through schema validation."""
        raw_items: list[dict[str, Any]] = []
        notes: list[str] = []

        if self.sample_json_path.exists():
            try:
                with self.sample_json_path.open("r", encoding="utf-8") as fh:
                    payload = json.load(fh)
                if isinstance(payload, dict) and isinstance(payload.get("records"), list):
                    raw_items = payload["records"]
            except (OSError, json.JSONDecodeError) as exc:
                notes.append(f"Could not read sample_dataset.json ({exc}); trying sample_dataset.csv.")

        if not raw_items and self.sample_csv_path.exists():
            try:
                with self.sample_csv_path.open("r", encoding="utf-8", newline="") as fh:
                    raw_items = list(csv.DictReader(fh))
            except (OSError, csv.Error) as exc:
                notes.append(f"Could not read sample_dataset.csv ({exc}).")

        if not raw_items:
            return 0, ["No sample dataset file found."]

        validated_items: list[dict[str, Any]] = []
        for item in raw_items:
            res = validate_record_input(item, require_record_id=False, require_created_at=False)
            if res.is_valid:
                validated_items.append(res.sanitized_data)

        if replace:
            self.save_records([])
        inserted = self.append_records(validated_items)
        return len(inserted), notes

    def load_thresholds(self) -> dict[str, Any]:
        """Load threshold configuration from JSON, creating defaults if missing or corrupted."""
        try:
            with self.thresholds_path.open("r", encoding="utf-8") as fh:
                raw = json.load(fh)
            res = validate_thresholds(raw)
            if res.is_valid:
                return res.sanitized_data
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            pass

        defaults = dict(DEFAULT_THRESHOLDS)
        self.save_thresholds(defaults)
        return defaults

    def save_thresholds(self, thresholds: dict[str, Any]) -> None:
        """Persist validated threshold configuration to JSON."""
        tmp_path = self.thresholds_path.with_suffix(".json.tmp")
        with tmp_path.open("w", encoding="utf-8") as fh:
            json.dump(thresholds, fh, indent=2)
        tmp_path.replace(self.thresholds_path)
