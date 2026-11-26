"""Executive summary and analytics computation from live stored records."""

from __future__ import annotations

import math
from collections import defaultdict
from datetime import date
from typing import Any

from app.detector import detect_exact_duplicates
from app.models import SummaryMetrics, TextRecord
from app.warnings import evaluate_warnings


def generate_summary_metrics(
    records: list[TextRecord],
    thresholds: dict[str, Any] | None = None,
    reference_date: date | None = None,
) -> SummaryMetrics:
    """Compute executive summary metrics, category breakdowns, trends, and warnings."""
    report = detect_exact_duplicates(records)
    warnings = evaluate_warnings(records, report, thresholds=thresholds, reference_date=reference_date)

    total = len(records)
    if total == 0:
        return SummaryMetrics(
            total_records=0,
            unique_entries=0,
            duplicate_entries=0,
            redundant_copies=0,
            distinct_duplicate_texts=0,
            duplication_rate_pct=0.0,
            avg_text_length=0.0,
            std_dev_text_length=0.0,
            avg_word_count=0.0,
            avg_priority=0.0,
            min_text_length=0,
            max_text_length=0,
            status_label="Empty Dataset",
            status_level="neutral",
            category_breakdown=[],
            daily_trends=[],
            top_duplicates=[],
            warnings=[],
        )

    lengths = [len(r.text) for r in records]
    word_counts = [len(r.text.split()) for r in records]
    priorities = [r.priority for r in records]

    avg_len = sum(lengths) / total
    variance = sum((length - avg_len) ** 2 for length in lengths) / total
    std_dev_len = math.sqrt(variance)

    avg_words = sum(word_counts) / total
    avg_pri = sum(priorities) / total

    # Category breakdown
    cat_buckets: dict[str, list[Any]] = defaultdict(list)
    for entry in report.all_analyzed:
        cat_buckets[entry.category].append(entry)

    category_breakdown: list[dict[str, Any]] = []
    for category, items in sorted(cat_buckets.items(), key=lambda pair: (-len(pair[1]), pair[0])):
        cat_total = len(items)
        cat_dups = sum(1 for item in items if item.is_duplicate)
        cat_unique = cat_total - cat_dups
        cat_rate = round((cat_dups / cat_total) * 100.0, 2) if cat_total else 0.0
        cat_avg_pri = round(sum(item.priority for item in items) / cat_total, 2) if cat_total else 0.0
        category_breakdown.append(
            {
                "category": category,
                "total": cat_total,
                "unique": cat_unique,
                "duplicates": cat_dups,
                "duplicate_rate_pct": cat_rate,
                "avg_priority": cat_avg_pri,
            }
        )

    # Daily trends by created_at date
    day_buckets: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "duplicates": 0, "unique": 0})
    for entry in report.all_analyzed:
        day_key = entry.created_at[:10] if len(entry.created_at) >= 10 else "Unknown"
        day_buckets[day_key]["total"] += 1
        if entry.is_duplicate:
            day_buckets[day_key]["duplicates"] += 1
        else:
            day_buckets[day_key]["unique"] += 1

    daily_trends = [
        {
            "date": day,
            "total": counts["total"],
            "duplicates": counts["duplicates"],
            "unique": counts["unique"],
        }
        for day, counts in sorted(day_buckets.items())
    ]

    # Top duplicate groups
    top_duplicates = [
        {
            "text": grp.text,
            "occurrence_count": grp.occurrence_count,
            "record_ids": grp.record_ids,
            "categories": grp.categories,
        }
        for grp in report.duplicate_groups[:10]
    ]

    # Overall status indicator
    has_critical_warning = any(w.severity == "critical" for w in warnings)
    dup_rate = report.duplication_rate_pct
    if has_critical_warning or dup_rate > 35.0:
        status_label = "Action Needed"
        status_level = "critical"
    elif dup_rate > 15.0 or any(w.severity == "warning" for w in warnings):
        status_label = "Moderate Duplication"
        status_level = "warning"
    else:
        status_label = "Healthy Integrity"
        status_level = "healthy"

    return SummaryMetrics(
        total_records=total,
        unique_entries=report.unique_only_count,
        duplicate_entries=report.duplicate_entry_count,
        redundant_copies=report.redundant_copy_count,
        distinct_duplicate_texts=report.distinct_duplicate_groups,
        duplication_rate_pct=dup_rate,
        avg_text_length=round(avg_len, 2),
        std_dev_text_length=round(std_dev_len, 2),
        avg_word_count=round(avg_words, 2),
        avg_priority=round(avg_pri, 2),
        min_text_length=min(lengths),
        max_text_length=max(lengths),
        status_label=status_label,
        status_level=status_level,
        category_breakdown=category_breakdown,
        daily_trends=daily_trends,
        top_duplicates=top_duplicates,
        warnings=warnings,
    )
