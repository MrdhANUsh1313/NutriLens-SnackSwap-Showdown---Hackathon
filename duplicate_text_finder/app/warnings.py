"""Automated threshold warning indicators derived from actual stored records and explicit rules."""

from __future__ import annotations

import math
from datetime import date, datetime
from typing import Any

from app.models import (
    DEFAULT_THRESHOLDS,
    DuplicateDetectionReport,
    TextRecord,
    WarningFlag,
)


def evaluate_warnings(
    records: list[TextRecord],
    detection_report: DuplicateDetectionReport,
    thresholds: dict[str, Any] | None = None,
    reference_date: date | None = None,
) -> list[WarningFlag]:
    """Evaluate overdue deadlines, anomalous entries, and critical limit breaches."""
    cfg = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
    today = reference_date or date.today()
    warnings: list[WarningFlag] = []

    if not records:
        return warnings

    # 1. Overdue deadlines (from actual record.due_date values)
    overdue_ids: list[str] = []
    due_today_ids: list[str] = []
    for rec in records:
        if rec.due_date:
            try:
                due_dt = datetime.strptime(rec.due_date, "%Y-%m-%d").date()
                if due_dt < today:
                    overdue_ids.append(rec.record_id)
                elif due_dt == today:
                    due_today_ids.append(rec.record_id)
            except ValueError:
                continue

    if overdue_ids:
        warnings.append(
            WarningFlag(
                severity="critical",
                warning_type="overdue_deadline",
                title="Overdue Record Deadlines Detected",
                message=f"{len(overdue_ids)} record(s) have a due date earlier than {today.isoformat()}.",
                affected_record_ids=overdue_ids,
                rule=f"record.due_date < {today.isoformat()}",
            )
        )

    if due_today_ids:
        warnings.append(
            WarningFlag(
                severity="warning",
                warning_type="overdue_deadline",
                title="Deadlines Due Today",
                message=f"{len(due_today_ids)} record(s) are due today ({today.isoformat()}).",
                affected_record_ids=due_today_ids,
                rule=f"record.due_date == {today.isoformat()}",
            )
        )

    # 2. Anomalous entries
    min_repeat = int(cfg["min_repeat_anomaly_count"])
    high_repeat_groups = [
        g for g in detection_report.duplicate_groups if g.occurrence_count >= min_repeat
    ]
    if high_repeat_groups:
        affected = [rid for grp in high_repeat_groups for rid in grp.record_ids]
        warnings.append(
            WarningFlag(
                severity="warning",
                warning_type="anomalous_entry",
                title="High-Frequency Repetition Anomaly",
                message=(
                    f"{len(high_repeat_groups)} exact text string(s) appear {min_repeat} or more times "
                    f"({len(affected)} total records)."
                ),
                affected_record_ids=affected,
                rule=f"occurrence_count >= {min_repeat}",
            )
        )

    short_len_limit = int(cfg["short_text_anomaly_len"])
    short_ids = [r.record_id for r in records if len(r.text.strip()) <= short_len_limit]
    if short_ids:
        warnings.append(
            WarningFlag(
                severity="info",
                warning_type="anomalous_entry",
                title="Ultra-Short Boundary Text Entries",
                message=(
                    f"{len(short_ids)} record(s) have trimmed text length <= {short_len_limit} characters."
                ),
                affected_record_ids=short_ids,
                rule=f"len(text.strip()) <= {short_len_limit}",
            )
        )

    whitespace_ids = [r.record_id for r in records if r.text != r.text.strip()]
    if whitespace_ids:
        warnings.append(
            WarningFlag(
                severity="warning",
                warning_type="anomalous_entry",
                title="Leading/Trailing Whitespace Anomaly",
                message=(
                    f"{len(whitespace_ids)} record(s) contain leading or trailing spaces, which are treated "
                    "as distinct under exact matching."
                ),
                affected_record_ids=whitespace_ids,
                rule="record.text != record.text.strip()",
            )
        )

    if len(records) >= 5:
        lengths = [len(r.text) for r in records]
        mean_len = sum(lengths) / len(lengths)
        variance = sum((length - mean_len) ** 2 for length in lengths) / len(lengths)
        std_dev = math.sqrt(variance)
        if std_dev > 0:
            upper_bound = mean_len + 2.0 * std_dev
            outlier_ids = [r.record_id for r in records if len(r.text) > upper_bound]
            if outlier_ids:
                warnings.append(
                    WarningFlag(
                        severity="info",
                        warning_type="anomalous_entry",
                        title="Statistical Text-Length Outliers",
                        message=(
                            f"{len(outlier_ids)} record(s) exceed 2 standard deviations above the mean length "
                            f"(>{upper_bound:.1f} chars)."
                        ),
                        affected_record_ids=outlier_ids,
                        rule="len(text) > mean + 2 * std_dev",
                    )
                )

    # 3. Critical limit breaches
    max_dup_rate = float(cfg["max_duplication_rate_pct"])
    if detection_report.duplication_rate_pct > max_dup_rate:
        dup_ids = [e.record_id for e in detection_report.duplicate_entries]
        warnings.append(
            WarningFlag(
                severity="critical",
                warning_type="critical_limit",
                title="Duplication Rate Threshold Breached",
                message=(
                    f"Dataset duplication rate is {detection_report.duplication_rate_pct:.2f}%, "
                    f"exceeding the configured limit of {max_dup_rate:.2f}%."
                ),
                affected_record_ids=dup_ids,
                rule=f"duplication_rate_pct > {max_dup_rate:.2f}%",
            )
        )

    max_cap = int(cfg["max_records_capacity"])
    total_count = len(records)
    if total_count >= max_cap:
        warnings.append(
            WarningFlag(
                severity="critical",
                warning_type="critical_limit",
                title="Configured Record Capacity Reached",
                message=f"Stored records ({total_count}) reached or exceeded capacity limit ({max_cap}).",
                affected_record_ids=[],
                rule=f"total_records >= {max_cap}",
            )
        )
    elif total_count >= math.ceil(max_cap * 0.85):
        warnings.append(
            WarningFlag(
                severity="warning",
                warning_type="critical_limit",
                title="Approaching Record Capacity Limit",
                message=f"Stored records ({total_count}) exceeded 85% of capacity limit ({max_cap}).",
                affected_record_ids=[],
                rule=f"total_records >= 85% of {max_cap}",
            )
        )

    urgent_dup_ids = [
        e.record_id
        for e in detection_report.duplicate_entries
        if e.priority == 5
    ]
    if urgent_dup_ids:
        warnings.append(
            WarningFlag(
                severity="critical",
                warning_type="critical_limit",
                title="Priority 5 (Critical) Entries Have Exact Duplicates",
                message=f"{len(urgent_dup_ids)} maximum-priority (P5) record(s) are duplicated.",
                affected_record_ids=urgent_dup_ids,
                rule="priority == 5 and is_duplicate",
            )
        )

    return warnings
