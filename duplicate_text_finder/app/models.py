"""Data models, schema constants, and operational state structures for Duplicate Text Finder."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

SCHEMA_VERSION = "1.0"

CSV_FIELDNAMES = (
    "record_id",
    "text",
    "category",
    "source",
    "priority",
    "due_date",
    "notes",
    "created_at",
)

DEFAULT_CATEGORIES = (
    "General",
    "Customer",
    "Support",
    "Log",
    "Email",
    "Inventory",
    "Product",
    "Document",
    "Finance",
    "Other",
)

MIN_TEXT_LENGTH = 1
MAX_TEXT_LENGTH = 2000
MIN_CATEGORY_LENGTH = 2
MAX_CATEGORY_LENGTH = 40
MIN_SOURCE_LENGTH = 2
MAX_SOURCE_LENGTH = 50
MIN_PRIORITY = 1
MAX_PRIORITY = 5
MAX_NOTES_LENGTH = 300

DEFAULT_THRESHOLDS = {
    "max_duplication_rate_pct": 25.0,
    "min_repeat_anomaly_count": 3,
    "max_records_capacity": 500,
    "short_text_anomaly_len": 3,
}


@dataclass
class TextRecord:
    """Represents a single validated text entry stored in CSV and JSON."""

    record_id: str
    text: str
    category: str
    source: str
    priority: int = 3
    due_date: str = ""
    notes: str = ""
    created_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert record to a JSON/CSV-serializable dictionary."""
        return asdict(self)


@dataclass
class ValidationResult:
    """Outcome of defensive validation for user or file inputs."""

    is_valid: bool
    sanitized_data: dict[str, Any] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DuplicateGroup:
    """Represents a group of records sharing exact duplicate text."""

    text: str
    occurrence_count: int
    record_ids: list[str]
    categories: list[str]
    first_seen: str
    latest_seen: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AnalyzedEntry:
    """A text entry annotated with exact duplicate detection metadata."""

    record_id: str
    text: str
    category: str
    source: str
    priority: int
    due_date: str
    notes: str
    created_at: str
    is_duplicate: bool
    occurrence_count: int
    duplicate_group_index: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DuplicateDetectionReport:
    """Complete result from the exact duplicate detection engine."""

    total_entries: int
    unique_only_count: int
    duplicate_entry_count: int
    redundant_copy_count: int
    distinct_duplicate_groups: int
    duplication_rate_pct: float
    duplicate_groups: list[DuplicateGroup]
    unique_entries: list[AnalyzedEntry]
    duplicate_entries: list[AnalyzedEntry]
    all_analyzed: list[AnalyzedEntry]

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_entries": self.total_entries,
            "unique_only_count": self.unique_only_count,
            "duplicate_entry_count": self.duplicate_entry_count,
            "redundant_copy_count": self.redundant_copy_count,
            "distinct_duplicate_groups": self.distinct_duplicate_groups,
            "duplication_rate_pct": self.duplication_rate_pct,
            "duplicate_groups": [g.to_dict() for g in self.duplicate_groups],
            "unique_entries": [e.to_dict() for e in self.unique_entries],
            "duplicate_entries": [e.to_dict() for e in self.duplicate_entries],
            "all_analyzed": [e.to_dict() for e in self.all_analyzed],
        }


@dataclass
class WarningFlag:
    """Automated threshold warning flag derived from actual record rules."""

    severity: str  # "critical" | "warning" | "info"
    warning_type: str  # "overdue_deadline" | "anomalous_entry" | "critical_limit"
    title: str
    message: str
    affected_record_ids: list[str]
    rule: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SummaryMetrics:
    """Executive summary metrics calculated from stored records."""

    total_records: int
    unique_entries: int
    duplicate_entries: int
    redundant_copies: int
    distinct_duplicate_texts: int
    duplication_rate_pct: float
    avg_text_length: float
    std_dev_text_length: float
    avg_word_count: float
    avg_priority: float
    min_text_length: int
    max_text_length: int
    status_label: str
    status_level: str
    category_breakdown: list[dict[str, Any]]
    daily_trends: list[dict[str, Any]]
    top_duplicates: list[dict[str, Any]]
    warnings: list[WarningFlag]

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_records": self.total_records,
            "unique_entries": self.unique_entries,
            "duplicate_entries": self.duplicate_entries,
            "redundant_copies": self.redundant_copies,
            "distinct_duplicate_texts": self.distinct_duplicate_texts,
            "duplication_rate_pct": self.duplication_rate_pct,
            "avg_text_length": self.avg_text_length,
            "std_dev_text_length": self.std_dev_text_length,
            "avg_word_count": self.avg_word_count,
            "avg_priority": self.avg_priority,
            "min_text_length": self.min_text_length,
            "max_text_length": self.max_text_length,
            "status_label": self.status_label,
            "status_level": self.status_level,
            "category_breakdown": self.category_breakdown,
            "daily_trends": self.daily_trends,
            "top_duplicates": self.top_duplicates,
            "warnings": [w.to_dict() for w in self.warnings],
        }


@dataclass
class ImportRowError:
    """Validation error detail for a single row during bulk CSV import."""

    row_number: int
    raw_data: dict[str, Any]
    errors: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class BulkImportReport:
    """Summary of a bulk CSV import operation."""

    filename: str
    total_rows: int
    valid_count: int
    invalid_count: int
    imported_records: list[TextRecord]
    row_errors: list[ImportRowError]
    storage_updated: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "filename": self.filename,
            "total_rows": self.total_rows,
            "valid_count": self.valid_count,
            "invalid_count": self.invalid_count,
            "imported_records": [r.to_dict() for r in self.imported_records],
            "row_errors": [e.to_dict() for e in self.row_errors],
            "storage_updated": self.storage_updated,
        }
