"""Core exact duplicate detection engine, completely decoupled from web presentation."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Sequence

from app.models import (
    AnalyzedEntry,
    DuplicateDetectionReport,
    DuplicateGroup,
    TextRecord,
)


def _coerce_to_records(entries: Sequence[TextRecord | str]) -> list[TextRecord]:
    """Normalize raw string lists or TextRecord sequences into TextRecord objects."""
    normalized: list[TextRecord] = []
    for idx, item in enumerate(entries, start=1):
        if isinstance(item, TextRecord):
            normalized.append(item)
        elif isinstance(item, str):
            normalized.append(
                TextRecord(
                    record_id=f"LINE-{idx:04d}",
                    text=item,
                    category="Batch",
                    source="Batch Input",
                    priority=3,
                    due_date="",
                    notes="",
                    created_at="",
                )
            )
        else:
            raise TypeError(f"Unsupported entry type at index {idx}: {type(item).__name__}")
    return normalized


def detect_exact_duplicates(entries: Sequence[TextRecord | str]) -> DuplicateDetectionReport:
    """Compare entries and identify exact text duplicates versus unique entries.

    Comparison uses exact string equality (case-sensitive and whitespace-sensitive)
    so distinct text entries are never falsely merged as duplicates.
    """
    records = _coerce_to_records(entries)
    total = len(records)

    if total == 0:
        return DuplicateDetectionReport(
            total_entries=0,
            unique_only_count=0,
            duplicate_entry_count=0,
            redundant_copy_count=0,
            distinct_duplicate_groups=0,
            duplication_rate_pct=0.0,
            duplicate_groups=[],
            unique_entries=[],
            duplicate_entries=[],
            all_analyzed=[],
        )

    counts: Counter[str] = Counter(record.text for record in records)
    grouped_records: dict[str, list[TextRecord]] = defaultdict(list)
    for record in records:
        grouped_records[record.text].append(record)

    # Build ordered duplicate groups (highest occurrence first, then appearance order).
    duplicate_texts = [
        text
        for text, count in sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
        if count > 1
    ]

    duplicate_groups: list[DuplicateGroup] = []
    group_index_by_text: dict[str, int] = {}

    for group_idx, text in enumerate(duplicate_texts, start=1):
        members = grouped_records[text]
        timestamps = sorted(m.created_at for m in members if m.created_at)
        categories = sorted({m.category for m in members if m.category})
        duplicate_groups.append(
            DuplicateGroup(
                text=text,
                occurrence_count=len(members),
                record_ids=[m.record_id for m in members],
                categories=categories,
                first_seen=timestamps[0] if timestamps else "",
                latest_seen=timestamps[-1] if timestamps else "",
            )
        )
        group_index_by_text[text] = group_idx

    all_analyzed: list[AnalyzedEntry] = []
    unique_entries: list[AnalyzedEntry] = []
    duplicate_entries: list[AnalyzedEntry] = []

    for record in records:
        occ = counts[record.text]
        is_dup = occ > 1
        analyzed = AnalyzedEntry(
            record_id=record.record_id,
            text=record.text,
            category=record.category,
            source=record.source,
            priority=record.priority,
            due_date=record.due_date,
            notes=record.notes,
            created_at=record.created_at,
            is_duplicate=is_dup,
            occurrence_count=occ,
            duplicate_group_index=group_index_by_text.get(record.text),
        )
        all_analyzed.append(analyzed)
        if is_dup:
            duplicate_entries.append(analyzed)
        else:
            unique_entries.append(analyzed)

    redundant_copies = sum(count - 1 for count in counts.values() if count > 1)
    duplication_rate_pct = round((len(duplicate_entries) / total) * 100.0, 2)

    return DuplicateDetectionReport(
        total_entries=total,
        unique_only_count=len(unique_entries),
        duplicate_entry_count=len(duplicate_entries),
        redundant_copy_count=redundant_copies,
        distinct_duplicate_groups=len(duplicate_groups),
        duplication_rate_pct=duplication_rate_pct,
        duplicate_groups=duplicate_groups,
        unique_entries=unique_entries,
        duplicate_entries=duplicate_entries,
        all_analyzed=all_analyzed,
    )


def find_near_variant_hints(entries: Sequence[TextRecord | str]) -> list[dict[str, object]]:
    """Identify strings that differ only in casing/outer whitespace (NOT counted as exact duplicates)."""
    records = _coerce_to_records(entries)
    buckets: dict[str, set[str]] = defaultdict(set)
    for record in records:
        normalized_key = " ".join(record.text.strip().lower().split())
        if normalized_key:
            buckets[normalized_key].add(record.text)

    hints: list[dict[str, object]] = []
    for normalized_key, variants in buckets.items():
        if len(variants) > 1:
            hints.append(
                {
                    "normalized_key": normalized_key,
                    "distinct_exact_variants": sorted(variants),
                    "variant_count": len(variants),
                }
            )
    return hints
