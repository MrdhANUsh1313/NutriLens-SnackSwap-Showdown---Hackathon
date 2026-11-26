"""Bulk CSV dataset importing with format validation and row-by-row error logging."""

from __future__ import annotations

import csv
import io
from typing import Any

from app.models import BulkImportReport, ImportRowError
from app.storage import StorageManager
from app.validator import validate_record_input

REQUIRED_IMPORT_COLUMNS = {"text", "category"}


def parse_and_import_csv(
    raw_bytes: bytes,
    filename: str,
    storage: StorageManager,
    *,
    dry_run: bool = False,
) -> tuple[BulkImportReport | None, str | None]:
    """Validate an uploaded CSV file, log row-level errors, and persist valid records."""
    safe_name = (filename or "upload.csv").strip()
    if not safe_name.lower().endswith(".csv"):
        return None, "Invalid file format. Please upload a .csv file."

    if not raw_bytes or not raw_bytes.strip():
        return None, "The uploaded CSV file is empty."

    try:
        decoded_text = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        return None, "File encoding error. CSV file must be UTF-8 encoded."

    try:
        reader = csv.DictReader(io.StringIO(decoded_text))
        if not reader.fieldnames:
            return None, "CSV file is missing a header row."
        cleaned_headers = [h.strip() if isinstance(h, str) else "" for h in reader.fieldnames]
        reader.fieldnames = cleaned_headers
        missing_cols = sorted(REQUIRED_IMPORT_COLUMNS - set(cleaned_headers))
        if missing_cols:
            return None, (
                f"Invalid CSV schema: missing required column(s): {', '.join(missing_cols)}. "
                "Required columns: text, category."
            )
        rows = list(reader)
    except csv.Error as exc:
        return None, f"Malformed CSV structure: {exc}"

    if not rows:
        return None, "CSV file contains a header row but no data rows."

    valid_payloads: list[dict[str, Any]] = []
    row_errors: list[ImportRowError] = []

    for row_num, raw_row in enumerate(rows, start=2):  # Row 1 is the header
        extra_values = raw_row.get(None)
        clean_row = {k: v for k, v in raw_row.items() if k is not None}

        if extra_values:
            row_errors.append(
                ImportRowError(
                    row_number=row_num,
                    raw_data=clean_row,
                    errors={"_row": "Row contains more columns than defined in the CSV header."},
                )
            )
            continue

        if not clean_row.get("source"):
            clean_row["source"] = f"CSV Import ({safe_name[:30]})"

        validation = validate_record_input(clean_row, require_record_id=False, require_created_at=False)
        if not validation.is_valid:
            row_errors.append(
                ImportRowError(
                    row_number=row_num,
                    raw_data=clean_row,
                    errors=validation.errors,
                )
            )
            continue

        valid_payloads.append(validation.sanitized_data)

    imported_records = []
    storage_updated = False
    if valid_payloads and not dry_run:
        imported_records = storage.append_records(valid_payloads)
        storage_updated = True

    report = BulkImportReport(
        filename=safe_name,
        total_rows=len(rows),
        valid_count=len(valid_payloads),
        invalid_count=len(row_errors),
        imported_records=imported_records,
        row_errors=row_errors,
        storage_updated=storage_updated,
    )
    return report, None
