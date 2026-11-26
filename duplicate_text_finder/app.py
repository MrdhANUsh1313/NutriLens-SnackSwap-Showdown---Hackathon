"""Application entry point for Duplicate Text Finder (Project #106)."""

from __future__ import annotations

import os

from app import create_app

application = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5050"))
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    print(f"Duplicate Text Finder running at http://127.0.0.1:{port}")
    application.run(host="127.0.0.1", port=port, debug=debug_mode)
