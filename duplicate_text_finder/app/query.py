"""Record query, keyword search, multi-criteria filtering, and pagination helpers."""

from __future__ import annotations

import math
from typing import Any

from app.detector import detect_exact_duplicates
from app.models import AnalyzedEntry, TextRecord


def query_records(
    records: list[TextRecord],
    *,
    keyword: str = "",
    category: str = "all",
    status: str = "all",
    priority: int | None = None,
    sort_by: str = "newest",
    page: int = 1,
    per_page: int = 10,
) -> dict[str, Any]:
    """Filter, annotate with duplicate status, sort, and paginate stored records."""
    report = detect_exact_duplicates(records)
    analyzed: list[AnalyzedEntry] = report.all_analyzed

    kw = keyword.strip().lower()
    cat_filter = category.strip()

    filtered: list[AnalyzedEntry] = []
    for entry in analyzed:
        if kw:
            haystack = " ".join(
                [
                    entry.record_id,
                    entry.text,
                    entry.category,
                    entry.source,
                    entry.notes,
                ]
            ).lower()
            if kw not in haystack:
                continue

        if cat_filter and cat_filter.lower() != "all":
            if entry.category.lower() != cat_filter.lower():
                continue

        if status == "duplicate" and not entry.is_duplicate:
            continue
        if status == "unique" and entry.is_duplicate:
            continue

        if priority is not None and entry.priority != priority:
            continue

        filtered.append(entry)

    # Sorting
    if sort_by == "oldest":
        filtered.sort(key=lambda e: (e.created_at, e.record_id))
    elif sort_by == "priority_desc":
        filtered.sort(key=lambda e: (-e.priority, e.record_id))
    elif sort_by == "occurrences_desc":
        filtered.sort(key=lambda e: (-e.occurrence_count, e.text, e.record_id))
    elif sort_by == "text_asc":
        filtered.sort(key=lambda e: (e.text.lower(), e.record_id))
    else:  # "newest" default
        filtered.sort(key=lambda e: (e.created_at, e.record_id), reverse=True)

    total_matched = len(filtered)
    total_pages = max(1, math.ceil(total_matched / per_page)) if total_matched > 0 else 1
    safe_page = min(max(1, page), total_pages)
    start_idx = (safe_page - 1) * per_page
    end_idx = start_idx + per_page
    page_items = filtered[start_idx:end_idx]

    available_categories = sorted({r.category for r in records if r.category})

    return {
        "items": [item.to_dict() for item in page_items],
        "pagination": {
            "page": safe_page,
            "per_page": per_page,
            "total_matched": total_matched,
            "total_records": len(records),
            "total_pages": total_pages,
            "has_prev": safe_page > 1,
            "has_next": safe_page < total_pages,
            "showing_from": start_idx + 1 if total_matched > 0 else 0,
            "showing_to": min(end_idx, total_matched),
        },
        "available_categories": available_categories,
        "filters": {
            "keyword": keyword,
            "category": category,
            "status": status,
            "priority": priority,
            "sort_by": sort_by,
        },
    }
