"""Flask HTTP routes and JSON API endpoints for Duplicate Text Finder."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from flask import (
    Blueprint,
    Response,
    current_app,
    jsonify,
    render_template,
    request,
)

from app.analytics import generate_summary_metrics
from app.charts import ChartKind, render_chart_png
from app.detector import detect_exact_duplicates, find_near_variant_hints
from app.exporter import (
    generate_markdown_report,
    generate_standardized_csv_report,
    generate_text_audit_log,
)
from app.importer import parse_and_import_csv
from app.models import DEFAULT_CATEGORIES
from app.query import query_records
from app.storage import StorageManager
from app.validator import (
    validate_batch_lines,
    validate_positive_int_param,
    validate_priority,
    validate_record_input,
    validate_thresholds,
)

bp = Blueprint("main", __name__)


def _storage() -> StorageManager:
    return current_app.config["STORAGE_MANAGER"]


@bp.get("/")
def index() -> str:
    """Render the main menu-driven Duplicate Text Finder web application."""
    return render_template("index.html", default_categories=list(DEFAULT_CATEGORIES))


@bp.get("/api/health")
def api_health() -> Response:
    """Return application and local storage health details."""
    storage = _storage()
    records, storage_status = storage.load_records()
    return jsonify(
        {
            "status": "ok",
            "app": "Duplicate Text Finder",
            "project_number": 106,
            "record_count": len(records),
            "storage": storage_status,
        }
    )


@bp.get("/api/records")
def api_list_records() -> tuple[Response, int] | Response:
    """Search, filter, sort, and paginate stored records."""
    storage = _storage()
    records, storage_status = storage.load_records()

    keyword = request.args.get("keyword", "")
    category = request.args.get("category", "all")
    status = request.args.get("status", "all")
    sort_by = request.args.get("sort_by", "newest")

    if status not in ("all", "duplicate", "unique"):
        return jsonify({"error": "Invalid status filter. Use 'all', 'duplicate', or 'unique'."}), 400

    priority_raw = request.args.get("priority", "")
    priority_val: int | None = None
    if priority_raw and priority_raw.lower() != "all":
        parsed_pri, pri_err = validate_priority(priority_raw)
        if pri_err:
            return jsonify({"error": pri_err}), 400
        priority_val = parsed_pri

    page, page_err = validate_positive_int_param(
        request.args.get("page"), name="page", default=1, min_val=1, max_val=10000
    )
    if page_err:
        return jsonify({"error": page_err}), 400

    per_page, per_err = validate_positive_int_param(
        request.args.get("per_page"), name="per_page", default=10, min_val=5, max_val=100
    )
    if per_err:
        return jsonify({"error": per_err}), 400

    result = query_records(
        records,
        keyword=keyword,
        category=category,
        status=status,
        priority=priority_val,
        sort_by=sort_by,
        page=page,
        per_page=per_page,
    )
    result["storage"] = storage_status
    return jsonify(result)


@bp.post("/api/records")
def api_create_record() -> tuple[Response, int]:
    """Validate and store a new text entry in both CSV and JSON files."""
    payload = request.get_json(silent=True)
    if payload is None:
        return (
            jsonify(
                {
                    "error": "Invalid or missing JSON request body.",
                    "errors": {"_form": "Request body must be valid JSON."},
                }
            ),
            400,
        )

    validation = validate_record_input(payload, require_record_id=False, require_created_at=False)
    if not validation.is_valid:
        return (
            jsonify(
                {
                    "error": "Validation failed. Please correct the highlighted fields.",
                    "errors": validation.errors,
                }
            ),
            400,
        )

    storage = _storage()
    created = storage.add_record(validation.sanitized_data)
    all_records, storage_status = storage.load_records()
    report = detect_exact_duplicates(all_records)
    matching_analyzed = next((item for item in report.all_analyzed if item.record_id == created.record_id), None)

    return (
        jsonify(
            {
                "message": f"Record {created.record_id} saved to local CSV and JSON storage.",
                "record": created.to_dict(),
                "analysis": matching_analyzed.to_dict() if matching_analyzed else None,
                "storage": storage_status,
            }
        ),
        201,
    )


@bp.delete("/api/records/<record_id>")
def api_delete_record(record_id: str) -> tuple[Response, int]:
    """Delete a record by ID and persist changes to CSV and JSON."""
    storage = _storage()
    deleted = storage.delete_record(record_id)
    if not deleted:
        return jsonify({"error": f"Record '{record_id}' was not found."}), 404
    return jsonify({"message": f"Record '{record_id}' deleted from local storage."}), 200


@bp.post("/api/detect/stored")
def api_detect_stored() -> Response:
    """Run exact duplicate detection across all currently stored records."""
    storage = _storage()
    records, storage_status = storage.load_records()
    report = detect_exact_duplicates(records)
    hints = find_near_variant_hints(records)
    return jsonify(
        {
            "mode": "stored_dataset",
            "report": report.to_dict(),
            "near_variant_hints": hints,
            "storage": storage_status,
        }
    )


@bp.post("/api/detect/batch")
def api_detect_batch() -> tuple[Response, int]:
    """Compare a multi-line batch of text entries (pasted text or uploaded .txt file)."""
    batch_text: Any = None
    save_to_storage = False
    category = "General"
    source = "Batch Compare"
    priority: Any = 3

    if request.files and "file" in request.files:
        uploaded = request.files["file"]
        fname = (uploaded.filename or "").strip()
        if not fname.lower().endswith((".txt", ".csv", ".log")):
            return (
                jsonify(
                    {
                        "error": "Unsupported file type. Upload a .txt, .log, or .csv file.",
                        "errors": {"batch_file": "Supported extensions: .txt, .log, .csv"},
                    }
                ),
                400,
            )
        try:
            batch_text = uploaded.read().decode("utf-8-sig")
        except UnicodeDecodeError:
            return (
                jsonify(
                    {
                        "error": "File must be UTF-8 encoded text.",
                        "errors": {"batch_file": "Unable to decode file as UTF-8 text."},
                    }
                ),
                400,
            )
        save_to_storage = request.form.get("save_to_storage", "false").lower() == "true"
        category = request.form.get("category", "General")
        source = f"File ({fname[:35]})"
        priority = request.form.get("priority", 3)
    else:
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return (
                jsonify(
                    {
                        "error": "Invalid JSON body for batch comparison.",
                        "errors": {"batch_text": "Expected a JSON object with 'batch_text'."},
                    }
                ),
                400,
            )
        batch_text = payload.get("batch_text")
        save_to_storage = bool(payload.get("save_to_storage", False))
        category = payload.get("category", "General")
        source = payload.get("source", "Batch Paste")
        priority = payload.get("priority", 3)

    validation = validate_batch_lines(batch_text)
    if not validation.is_valid:
        return (
            jsonify(
                {
                    "error": "Batch input validation failed.",
                    "errors": validation.errors,
                }
            ),
            400,
        )

    lines: list[str] = validation.sanitized_data["lines"]
    skipped_blanks: list[int] = validation.sanitized_data["skipped_blank_lines"]
    report = detect_exact_duplicates(lines)
    hints = find_near_variant_hints(lines)

    saved_count = 0
    if save_to_storage:
        validated_batch_items: list[dict[str, Any]] = []
        for idx, line in enumerate(lines, start=1):
            row_val = validate_record_input(
                {
                    "text": line,
                    "category": category,
                    "source": source,
                    "priority": priority,
                    "notes": f"Saved from batch compare (line {idx})",
                }
            )
            if not row_val.is_valid:
                return (
                    jsonify(
                        {
                            "error": "Metadata validation failed when saving batch entries.",
                            "errors": row_val.errors,
                        }
                    ),
                    400,
                )
            validated_batch_items.append(row_val.sanitized_data)

        created = _storage().append_records(validated_batch_items)
        saved_count = len(created)

    return (
        jsonify(
            {
                "mode": "batch_input",
                "report": report.to_dict(),
                "near_variant_hints": hints,
                "skipped_blank_lines": skipped_blanks,
                "saved_to_storage_count": saved_count,
            }
        ),
        200,
    )


@bp.get("/api/analytics")
def api_analytics() -> Response:
    """Return dynamic executive summary, trends, and threshold warnings."""
    storage = _storage()
    records, storage_status = storage.load_records()
    thresholds = storage.load_thresholds()
    metrics = generate_summary_metrics(records, thresholds=thresholds)
    return jsonify(
        {
            "metrics": metrics.to_dict(),
            "thresholds": thresholds,
            "storage": storage_status,
        }
    )


@bp.get("/api/charts/<kind>.png")
def api_chart_image(kind: str) -> tuple[Response, int] | Response:
    """Render and serve a live Matplotlib PNG chart."""
    valid_kinds: tuple[ChartKind, ...] = ("distribution", "categories", "trends")
    if kind not in valid_kinds:
        return jsonify({"error": f"Unknown chart kind '{kind}'."}), 404

    storage = _storage()
    records, _ = storage.load_records()
    thresholds = storage.load_thresholds()
    metrics = generate_summary_metrics(records, thresholds=thresholds)
    png_bytes = render_chart_png(metrics, kind)  # type: ignore[arg-type]

    response = Response(png_bytes, mimetype="image/png")
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response


@bp.get("/api/export/<fmt>")
def api_export(fmt: str) -> tuple[Response, int] | Response:
    """Export stored records and summary in Markdown, Plain-Text, or CSV format."""
    storage = _storage()
    records, storage_status = storage.load_records()
    thresholds = storage.load_thresholds()
    metrics = generate_summary_metrics(records, thresholds=thresholds)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    fmt_lower = fmt.lower()
    if fmt_lower == "markdown":
        content = generate_markdown_report(records, metrics, storage_status)
        filename = f"duplicate_text_report_{stamp}.md"
        mimetype = "text/markdown; charset=utf-8"
    elif fmt_lower == "txt":
        content = generate_text_audit_log(records, metrics, storage_status)
        filename = f"duplicate_text_audit_{stamp}.txt"
        mimetype = "text/plain; charset=utf-8"
    elif fmt_lower == "csv":
        content = generate_standardized_csv_report(records)
        filename = f"duplicate_text_standardized_{stamp}.csv"
        mimetype = "text/csv; charset=utf-8"
    else:
        return jsonify({"error": "Unsupported export format. Use 'markdown', 'txt', or 'csv'."}), 400

    if request.args.get("preview") == "1":
        return jsonify({"format": fmt_lower, "filename": filename, "content": content})

    response = Response(content, mimetype=mimetype)
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@bp.post("/api/import/csv")
def api_import_csv() -> tuple[Response, int]:
    """Bulk import a CSV dataset with format validation and row-by-row error log."""
    if "file" not in request.files:
        return (
            jsonify(
                {
                    "error": "No CSV file uploaded. Choose a .csv file first.",
                    "errors": {"file": "Please select a .csv file to import."},
                }
            ),
            400,
        )

    uploaded = request.files["file"]
    filename = uploaded.filename or ""
    raw_bytes = uploaded.read()
    dry_run = request.form.get("dry_run", "false").lower() == "true"

    report, err = parse_and_import_csv(raw_bytes, filename, _storage(), dry_run=dry_run)
    if err or report is None:
        return jsonify({"error": err or "Failed to import CSV.", "errors": {"file": err}}), 400

    return jsonify({"message": "Bulk CSV processing complete.", "report": report.to_dict()}), 200


@bp.get("/api/thresholds")
def api_get_thresholds() -> Response:
    """Return current warning threshold rules."""
    return jsonify({"thresholds": _storage().load_thresholds()})


@bp.post("/api/thresholds")
def api_update_thresholds() -> tuple[Response, int]:
    """Validate and update warning threshold rules."""
    payload = request.get_json(silent=True)
    validation = validate_thresholds(payload)
    if not validation.is_valid:
        return (
            jsonify(
                {
                    "error": "Threshold validation failed.",
                    "errors": validation.errors,
                }
            ),
            400,
        )
    _storage().save_thresholds(validation.sanitized_data)
    return jsonify({"message": "Threshold settings updated.", "thresholds": validation.sanitized_data}), 200


@bp.post("/api/storage/load-sample")
def api_load_sample() -> tuple[Response, int]:
    """Seed or append the bundled 40-entry sample dataset into live CSV & JSON storage."""
    payload = request.get_json(silent=True) or {}
    replace = bool(payload.get("replace", True))
    count, notes = _storage().load_sample_dataset(replace=replace)
    if count == 0:
        return jsonify({"error": "Failed to load sample dataset.", "notes": notes}), 400
    return jsonify({"message": f"Loaded {count} sample records into CSV and JSON storage.", "count": count}), 200


@bp.post("/api/storage/clear")
def api_clear_storage() -> Response:
    """Clear all stored records while keeping clean CSV & JSON templates."""
    removed = _storage().clear_records()
    return jsonify({"message": f"Cleared {removed} record(s). Storage templates remain intact.", "removed": removed})
