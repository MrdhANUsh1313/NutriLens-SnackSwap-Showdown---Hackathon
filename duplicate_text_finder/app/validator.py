"""Centralized defensive input sanitization and validation routines."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from app.models import (
    DEFAULT_THRESHOLDS,
    MAX_CATEGORY_LENGTH,
    MAX_NOTES_LENGTH,
    MAX_PRIORITY,
    MAX_SOURCE_LENGTH,
    MAX_TEXT_LENGTH,
    MIN_CATEGORY_LENGTH,
    MIN_PRIORITY,
    MIN_SOURCE_LENGTH,
    MIN_TEXT_LENGTH,
    ValidationResult,
)

# Strip ASCII control characters except newline (\n) and tab (\t).
CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
CATEGORY_RE = re.compile(rf"^[A-Za-z0-9 _-]{{{MIN_CATEGORY_LENGTH},{MAX_CATEGORY_LENGTH}}}$")
SOURCE_RE = re.compile(rf"^[A-Za-z0-9 _./-]{{{MIN_SOURCE_LENGTH},{MAX_SOURCE_LENGTH}}}$")
RECORD_ID_RE = re.compile(r"^DTF-\d{4,}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}$")
INT_RE = re.compile(r"^[+-]?\d+$")


def sanitize_string(value: Any, *, strip_outer: bool = True) -> tuple[str | None, str | None]:
    """Ensure value is a valid string (not bool/list/dict/None) and sanitize control chars."""
    if value is None:
        return "", None
    if isinstance(value, bool) or not isinstance(value, str):
        return None, f"Expected text string, received {type(value).__name__}."
    cleaned = value.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = CONTROL_CHAR_RE.sub("", cleaned)
    if strip_outer:
        cleaned = cleaned.strip()
    return cleaned, None


def validate_priority(raw_priority: Any, *, default: int = 3) -> tuple[int | None, str | None]:
    """Validate priority as an integer within [1, 5] without accepting booleans or floats."""
    if raw_priority is None or (isinstance(raw_priority, str) and raw_priority.strip() == ""):
        return default, None
    if isinstance(raw_priority, bool):
        return None, "Priority must be a whole number between 1 and 5, not a boolean."
    if isinstance(raw_priority, int):
        parsed = raw_priority
    elif isinstance(raw_priority, str):
        candidate = raw_priority.strip()
        if not INT_RE.match(candidate):
            return None, "Priority must be a valid whole number between 1 and 5."
        parsed = int(candidate)
    else:
        return None, f"Priority must be an integer between {MIN_PRIORITY} and {MAX_PRIORITY}."

    if parsed < MIN_PRIORITY or parsed > MAX_PRIORITY:
        return None, f"Priority must be between {MIN_PRIORITY} and {MAX_PRIORITY} (received {parsed})."
    return parsed, None


def validate_due_date(raw_due_date: Any) -> tuple[str | None, str | None]:
    """Validate optional due date in strict YYYY-MM-DD format."""
    cleaned, err = sanitize_string(raw_due_date, strip_outer=True)
    if err:
        return None, f"Due date invalid: {err}"
    if not cleaned:
        return "", None
    if not DATE_RE.match(cleaned):
        return None, "Due date must follow YYYY-MM-DD format (e.g. 2026-12-31)."
    try:
        datetime.strptime(cleaned, "%Y-%m-%d")
    except ValueError:
        return None, f"Due date '{cleaned}' is not a valid calendar date."
    return cleaned, None


def validate_record_input(
    payload: Any,
    *,
    require_record_id: bool = False,
    require_created_at: bool = False,
) -> ValidationResult:
    """Validate and sanitize a single text record submission or stored record."""
    if not isinstance(payload, dict):
        return ValidationResult(
            is_valid=False,
            errors={"_form": "Input payload must be a JSON object or key-value dictionary."},
        )

    errors: dict[str, str] = {}
    sanitized: dict[str, Any] = {}

    # 1. Text entry (required, non-blank, preserve exact internal/outer spacing after control strip)
    raw_text = payload.get("text")
    if raw_text is None:
        errors["text"] = "Text entry is required."
        cleaned_text = None
    else:
        cleaned_text, text_err = sanitize_string(raw_text, strip_outer=False)
        if text_err:
            errors["text"] = text_err
        elif cleaned_text is not None:
            if not cleaned_text.strip():
                errors["text"] = "Text entry cannot be blank or whitespace only."
            elif len(cleaned_text) < MIN_TEXT_LENGTH or len(cleaned_text) > MAX_TEXT_LENGTH:
                errors["text"] = (
                    f"Text entry length must be between {MIN_TEXT_LENGTH} and "
                    f"{MAX_TEXT_LENGTH} characters (got {len(cleaned_text)})."
                )
            else:
                sanitized["text"] = cleaned_text

    # 2. Category (required, regex validated)
    raw_category = payload.get("category")
    if raw_category is None or (isinstance(raw_category, str) and not raw_category.strip()):
        errors["category"] = "Category is required (e.g. General, Customer, Log)."
    else:
        cleaned_cat, cat_err = sanitize_string(raw_category, strip_outer=True)
        if cat_err:
            errors["category"] = cat_err
        elif cleaned_cat is not None and not CATEGORY_RE.match(cleaned_cat):
            errors["category"] = (
                f"Category must be {MIN_CATEGORY_LENGTH}-{MAX_CATEGORY_LENGTH} characters "
                "using letters, numbers, spaces, hyphens, or underscores."
            )
        else:
            sanitized["category"] = cleaned_cat

    # 3. Source (defaults to Manual Entry if omitted, validated if supplied)
    raw_source = payload.get("source", "Manual Entry")
    cleaned_source, src_err = sanitize_string(raw_source, strip_outer=True)
    if src_err:
        errors["source"] = src_err
    elif not cleaned_source:
        sanitized["source"] = "Manual Entry"
    elif not SOURCE_RE.match(cleaned_source):
        errors["source"] = (
            f"Source must be {MIN_SOURCE_LENGTH}-{MAX_SOURCE_LENGTH} characters "
            "using letters, numbers, spaces, dots, slashes, hyphens, or underscores."
        )
    else:
        sanitized["source"] = cleaned_source

    # 4. Priority (integer 1..5)
    parsed_priority, pri_err = validate_priority(payload.get("priority", 3), default=3)
    if pri_err:
        errors["priority"] = pri_err
    else:
        sanitized["priority"] = parsed_priority

    # 5. Due date (optional YYYY-MM-DD)
    parsed_due_date, due_err = validate_due_date(payload.get("due_date", ""))
    if due_err:
        errors["due_date"] = due_err
    else:
        sanitized["due_date"] = parsed_due_date

    # 6. Notes (optional <= 300 chars)
    cleaned_notes, notes_err = sanitize_string(payload.get("notes", ""), strip_outer=True)
    if notes_err:
        errors["notes"] = notes_err
    elif cleaned_notes is not None and len(cleaned_notes) > MAX_NOTES_LENGTH:
        errors["notes"] = f"Notes cannot exceed {MAX_NOTES_LENGTH} characters (got {len(cleaned_notes)})."
    else:
        sanitized["notes"] = cleaned_notes or ""

    # 7. Optional or required record_id
    if "record_id" in payload and payload.get("record_id") not in (None, ""):
        cleaned_id, id_err = sanitize_string(payload.get("record_id"), strip_outer=True)
        if id_err:
            errors["record_id"] = id_err
        elif cleaned_id is not None and not RECORD_ID_RE.match(cleaned_id):
            errors["record_id"] = "Record ID must match format DTF-0001."
        else:
            sanitized["record_id"] = cleaned_id
    elif require_record_id:
        errors["record_id"] = "Missing required record_id."

    # 8. Optional or required created_at
    if "created_at" in payload and payload.get("created_at") not in (None, ""):
        cleaned_ts, ts_err = sanitize_string(payload.get("created_at"), strip_outer=True)
        if ts_err:
            errors["created_at"] = ts_err
        elif cleaned_ts is not None:
            normalized_ts = cleaned_ts.replace(" ", "T")
            if not TIMESTAMP_RE.match(normalized_ts):
                errors["created_at"] = "Timestamp must follow YYYY-MM-DDTHH:MM:SS format."
            else:
                try:
                    datetime.strptime(normalized_ts, "%Y-%m-%dT%H:%M:%S")
                    sanitized["created_at"] = normalized_ts
                except ValueError:
                    errors["created_at"] = f"Timestamp '{cleaned_ts}' is not a valid datetime."
    elif require_created_at:
        errors["created_at"] = "Missing required created_at timestamp."

    return ValidationResult(
        is_valid=len(errors) == 0,
        sanitized_data=sanitized,
        errors=errors,
    )


def validate_batch_lines(raw_text_block: Any, *, max_lines: int = 500) -> ValidationResult:
    """Validate a multi-line batch submission for ad-hoc duplicate comparison."""
    cleaned_block, err = sanitize_string(raw_text_block, strip_outer=False)
    if err:
        return ValidationResult(is_valid=False, errors={"batch_text": err})
    if not cleaned_block or not cleaned_block.strip():
        return ValidationResult(
            is_valid=False,
            errors={"batch_text": "Please enter at least one non-empty text line to compare."},
        )

    lines = cleaned_block.split("\n")
    valid_lines: list[str] = []
    skipped_blank_lines: list[int] = []
    line_errors: list[str] = []

    for idx, line in enumerate(lines, start=1):
        if not line.strip():
            skipped_blank_lines.append(idx)
            continue
        if len(line) > MAX_TEXT_LENGTH:
            line_errors.append(
                f"Line {idx} exceeds maximum length of {MAX_TEXT_LENGTH} characters ({len(line)} chars)."
            )
            continue
        valid_lines.append(line)

    if len(valid_lines) > max_lines:
        return ValidationResult(
            is_valid=False,
            errors={"batch_text": f"Batch comparison supports at most {max_lines} entries at once."},
        )

    if line_errors:
        return ValidationResult(
            is_valid=False,
            errors={"batch_text": " ".join(line_errors[:3])},
        )

    if not valid_lines:
        return ValidationResult(
            is_valid=False,
            errors={"batch_text": "All provided lines were blank. Enter valid text entries."},
        )

    return ValidationResult(
        is_valid=True,
        sanitized_data={
            "lines": valid_lines,
            "skipped_blank_lines": skipped_blank_lines,
        },
        errors={},
    )


def validate_positive_int_param(
    raw_value: Any,
    *,
    name: str,
    default: int,
    min_val: int,
    max_val: int,
) -> tuple[int, str | None]:
    """Validate integer query parameters like page and per_page safely."""
    if raw_value is None or str(raw_value).strip() == "":
        return default, None
    raw_str = str(raw_value).strip()
    if not INT_RE.match(raw_str):
        return default, f"Parameter '{name}' must be an integer."
    val = int(raw_str)
    if val < min_val or val > max_val:
        return default, f"Parameter '{name}' must be between {min_val} and {max_val}."
    return val, None


def validate_thresholds(payload: Any) -> ValidationResult:
    """Validate user-configured warning thresholds."""
    if not isinstance(payload, dict):
        return ValidationResult(is_valid=False, errors={"_form": "Thresholds payload must be a dictionary."})

    errors: dict[str, str] = {}
    sanitized: dict[str, Any] = {}

    # max_duplication_rate_pct (1.0 - 100.0)
    raw_rate = payload.get("max_duplication_rate_pct", DEFAULT_THRESHOLDS["max_duplication_rate_pct"])
    try:
        if isinstance(raw_rate, bool):
            raise ValueError("Boolean not allowed")
        rate = float(raw_rate)
        if rate < 1.0 or rate > 100.0:
            errors["max_duplication_rate_pct"] = "Max duplication rate (%) must be between 1 and 100."
        else:
            sanitized["max_duplication_rate_pct"] = round(rate, 2)
    except (TypeError, ValueError):
        errors["max_duplication_rate_pct"] = "Max duplication rate (%) must be a valid number."

    # min_repeat_anomaly_count (2 - 100)
    raw_repeat = payload.get("min_repeat_anomaly_count", DEFAULT_THRESHOLDS["min_repeat_anomaly_count"])
    if isinstance(raw_repeat, bool) or not INT_RE.match(str(raw_repeat).strip()):
        errors["min_repeat_anomaly_count"] = "Repeat anomaly threshold must be an integer."
    else:
        repeat_val = int(str(raw_repeat).strip())
        if repeat_val < 2 or repeat_val > 100:
            errors["min_repeat_anomaly_count"] = "Repeat anomaly threshold must be between 2 and 100."
        else:
            sanitized["min_repeat_anomaly_count"] = repeat_val

    # max_records_capacity (10 - 10000)
    raw_cap = payload.get("max_records_capacity", DEFAULT_THRESHOLDS["max_records_capacity"])
    if isinstance(raw_cap, bool) or not INT_RE.match(str(raw_cap).strip()):
        errors["max_records_capacity"] = "Max records capacity must be an integer."
    else:
        cap_val = int(str(raw_cap).strip())
        if cap_val < 10 or cap_val > 10000:
            errors["max_records_capacity"] = "Max records capacity must be between 10 and 10000."
        else:
            sanitized["max_records_capacity"] = cap_val

    # short_text_anomaly_len (1 - 20)
    raw_short = payload.get("short_text_anomaly_len", DEFAULT_THRESHOLDS["short_text_anomaly_len"])
    if isinstance(raw_short, bool) or not INT_RE.match(str(raw_short).strip()):
        errors["short_text_anomaly_len"] = "Short text anomaly length must be an integer."
    else:
        short_val = int(str(raw_short).strip())
        if short_val < 1 or short_val > 20:
            errors["short_text_anomaly_len"] = "Short text anomaly length must be between 1 and 20."
        else:
            sanitized["short_text_anomaly_len"] = short_val

    return ValidationResult(is_valid=len(errors) == 0, sanitized_data=sanitized, errors=errors)
