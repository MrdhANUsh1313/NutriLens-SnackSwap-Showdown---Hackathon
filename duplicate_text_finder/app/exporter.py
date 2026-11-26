"""Multi-format report generation (Markdown, Plain-Text Audit Log, Standardized CSV)."""

from __future__ import annotations

import csv
import io
from datetime import datetime
from typing import Any

from app.detector import detect_exact_duplicates
from app.models import SummaryMetrics, TextRecord


def _truncate(value: str, width: int) -> str:
    single_line = value.replace("\n", " ")
    if len(single_line) <= width:
        return single_line
    return single_line[: max(1, width - 3)] + "..."


def generate_markdown_report(
    records: list[TextRecord],
    metrics: SummaryMetrics,
    storage_status: dict[str, Any],
) -> str:
    """Build a structured Markdown summary report for external review."""
    report = detect_exact_duplicates(records)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines: list[str] = [
        "# Duplicate Text Finder — Executive Summary Report",
        "",
        f"- **Generated At:** {now_str}",
        f"- **Dataset Status:** {metrics.status_label}",
        f"- **Storage Source:** {storage_status.get('active_source', 'records.json')}",
        "",
        "## 1. Key Summary Metrics",
        "",
        "| Metric | Value |",
        "| --- | --- |",
        f"| Total Records | {metrics.total_records} |",
        f"| Unique Entries | {metrics.unique_entries} |",
        f"| Duplicate Entries (Total Occurrences) | {metrics.duplicate_entries} |",
        f"| Redundant Copies | {metrics.redundant_copies} |",
        f"| Distinct Duplicated Texts | {metrics.distinct_duplicate_texts} |",
        f"| Duplication Rate | {metrics.duplication_rate_pct:.2f}% |",
        f"| Average Text Length | {metrics.avg_text_length:.2f} chars (std dev {metrics.std_dev_text_length:.2f}) |",
        f"| Average Word Count | {metrics.avg_word_count:.2f} words |",
        f"| Average Priority | {metrics.avg_priority:.2f} / 5.0 |",
        "",
        "## 2. Threshold Warning Indicators",
        "",
    ]

    if not metrics.warnings:
        lines.append("No active warning flags detected.")
    else:
        lines.extend(
            [
                "| Severity | Type | Title | Details | Rule |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for w in metrics.warnings:
            lines.append(
                f"| {w.severity.upper()} | {w.warning_type} | {w.title} | {w.message} | `{w.rule}` |"
            )

    lines.extend(["", "## 3. Category Breakdown", ""])
    if not metrics.category_breakdown:
        lines.append("No category data available.")
    else:
        lines.extend(
            [
                "| Category | Total | Unique | Duplicates | Duplicate Rate | Avg Priority |",
                "| --- | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in metrics.category_breakdown:
            lines.append(
                f"| {row['category']} | {row['total']} | {row['unique']} | {row['duplicates']} | "
                f"{row['duplicate_rate_pct']:.2f}% | {row['avg_priority']:.2f} |"
            )

    lines.extend(["", "## 4. Exact Duplicate Groups", ""])
    if not report.duplicate_groups:
        lines.append("No exact duplicates found in the current dataset.")
    else:
        lines.extend(
            [
                "| Group # | Occurrences | Record IDs | Categories | Exact Text |",
                "| ---: | ---: | --- | --- | --- |",
            ]
        )
        for idx, grp in enumerate(report.duplicate_groups, start=1):
            safe_text = grp.text.replace("|", "\\|").replace("\n", " ")
            lines.append(
                f"| {idx} | {grp.occurrence_count} | {', '.join(grp.record_ids)} | "
                f"{', '.join(grp.categories)} | `{safe_text}` |"
            )

    lines.extend(["", "## 5. Complete Analyzed Records", ""])
    if not report.all_analyzed:
        lines.append("No records stored.")
    else:
        lines.extend(
            [
                "| Record ID | Status | Count | Category | Priority | Due Date | Text |",
                "| --- | --- | ---: | --- | ---: | --- | --- |",
            ]
        )
        for item in report.all_analyzed:
            status_lbl = "DUPLICATE" if item.is_duplicate else "UNIQUE"
            safe_text = item.text.replace("|", "\\|").replace("\n", " ")
            lines.append(
                f"| {item.record_id} | {status_lbl} | {item.occurrence_count} | {item.category} | "
                f"{item.priority} | {item.due_date or '-'} | {safe_text} |"
            )

    return "\n".join(lines) + "\n"


def generate_text_audit_log(
    records: list[TextRecord],
    metrics: SummaryMetrics,
    storage_status: dict[str, Any],
) -> str:
    """Build a formatted plain-text audit log with consistent column widths and separators."""
    report = detect_exact_duplicates(records)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sep = "=" * 96
    sub_sep = "-" * 96

    lines: list[str] = [
        sep,
        "DUPLICATE TEXT FINDER - AUDIT & DIAGNOSTIC LOG",
        sep,
        f"Generated Timestamp : {now_str}",
        f"Overall Status      : {metrics.status_label} ({metrics.status_level.upper()})",
        f"Storage Source      : {storage_status.get('active_source', 'records.json')}",
        f"Total Records       : {metrics.total_records}",
        f"Unique Entries      : {metrics.unique_entries}",
        f"Duplicate Entries   : {metrics.duplicate_entries} ({metrics.distinct_duplicate_texts} distinct groups)",
        f"Redundant Copies    : {metrics.redundant_copies}",
        f"Duplication Rate    : {metrics.duplication_rate_pct:.2f}%",
        f"Avg Text Length     : {metrics.avg_text_length:.2f} chars (min={metrics.min_text_length}, max={metrics.max_text_length})",
        f"Avg Priority        : {metrics.avg_priority:.2f} / 5.0",
        "",
        "THRESHOLD WARNINGS",
        sub_sep,
    ]

    if not metrics.warnings:
        lines.append("  [OK] No threshold warnings triggered.")
    else:
        for w in metrics.warnings:
            ids_str = ", ".join(w.affected_record_ids) if w.affected_record_ids else "Dataset-wide"
            lines.append(f"  [{w.severity.upper():8}] {w.title} | Rule: {w.rule}")
            lines.append(f"             Detail : {w.message}")
            lines.append(f"             Records: {ids_str}")

    lines.extend(["", "EXACT DUPLICATE GROUPS", sub_sep])
    if not report.duplicate_groups:
        lines.append("  None detected.")
    else:
        header = f"  {'GRP':<4} | {'CNT':>3} | {'RECORD IDS':<26} | {'TEXT PREVIEW':<52}"
        lines.append(header)
        lines.append("  " + "-" * 92)
        for idx, grp in enumerate(report.duplicate_groups, start=1):
            ids_preview = _truncate(", ".join(grp.record_ids), 26)
            txt_preview = _truncate(grp.text, 52)
            lines.append(f"  {idx:<4} | {grp.occurrence_count:>3} | {ids_preview:<26} | {txt_preview:<52}")

    lines.extend(["", "ANALYZED RECORDS LOG", sub_sep])
    if not report.all_analyzed:
        lines.append("  No records stored.")
    else:
        rec_header = f"  {'ID':<10} | {'STATUS':<9} | {'CNT':>3} | {'CATEGORY':<12} | {'PRI':>3} | {'TEXT':<42}"
        lines.append(rec_header)
        lines.append("  " + "-" * 92)
        for entry in report.all_analyzed:
            status_lbl = "DUPLICATE" if entry.is_duplicate else "UNIQUE"
            lines.append(
                f"  {entry.record_id:<10} | {status_lbl:<9} | {entry.occurrence_count:>3} | "
                f"{_truncate(entry.category, 12):<12} | {entry.priority:>3} | {_truncate(entry.text, 42):<42}"
            )

    lines.append(sep)
    return "\n".join(lines) + "\n"


def generate_standardized_csv_report(records: list[TextRecord]) -> str:
    """Export all stored records enriched with exact duplicate status and occurrence count."""
    report = detect_exact_duplicates(records)
    output = io.StringIO()
    fieldnames = [
        "record_id",
        "text",
        "category",
        "source",
        "priority",
        "due_date",
        "created_at",
        "duplicate_status",
        "occurrence_count",
        "duplicate_group_index",
        "notes",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for entry in report.all_analyzed:
        writer.writerow(
            {
                "record_id": entry.record_id,
                "text": entry.text,
                "category": entry.category,
                "source": entry.source,
                "priority": entry.priority,
                "due_date": entry.due_date,
                "created_at": entry.created_at,
                "duplicate_status": "duplicate" if entry.is_duplicate else "unique",
                "occurrence_count": entry.occurrence_count,
                "duplicate_group_index": entry.duplicate_group_index or "",
                "notes": entry.notes,
            }
        )
    return output.getvalue()
