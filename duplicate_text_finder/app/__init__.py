"""Flask application factory for Duplicate Text Finder."""

from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify

from app.routes import bp
from app.storage import StorageManager


def create_app(data_dir: Path | str | None = None) -> Flask:
    """Create and configure the Flask application instance."""
    base_dir = Path(__file__).resolve().parent.parent
    resolved_data_dir = Path(data_dir) if data_dir is not None else base_dir / "data"

    app = Flask(
        __name__,
        template_folder=str(base_dir / "templates"),
        static_folder=str(base_dir / "static"),
    )
    app.config["MAX_CONTENT_LENGTH"] = 4 * 1024 * 1024  # 4 MB safe upload limit
    storage = StorageManager(resolved_data_dir)
    # Verify/initialize local CSV and JSON templates at startup without crashing
    storage.load_records()
    storage.load_thresholds()
    app.config["STORAGE_MANAGER"] = storage

    app.register_blueprint(bp)

    @app.errorhandler(413)
    def handle_file_too_large(_err: Exception):
        return jsonify({"error": "Uploaded file exceeds the 4 MB size limit."}), 413

    @app.errorhandler(404)
    def handle_not_found(_err: Exception):
        return jsonify({"error": "Requested resource or endpoint was not found."}), 404

    @app.errorhandler(500)
    def handle_internal_error(_err: Exception):
        return jsonify({"error": "An unexpected server error occurred. Storage remains safe."}), 500

    return app
