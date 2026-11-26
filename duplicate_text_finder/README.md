# Duplicate Text Finder (Project #106)

**Hackathon:** Python for Good  
**Domain:** Digital Tools & Productivity  
**Tech Stack:** Python 3.10+ (verified on 3.15), Flask, Matplotlib, HTML5, CSS3, Vanilla JavaScript, Local CSV & JSON Storage

Duplicate Text Finder compares text entries using strict exact string matching, validates incoming inputs defensively, persists records locally to synchronized `records.csv` and `records.json` files, and generates live analytics, Matplotlib charts, threshold warnings, and multi-format reports.

---

## Project Structure

```text
duplicate_text_finder/
├── app/
│   ├── __init__.py       # Flask application factory & error handlers
│   ├── models.py         # Dataclasses & schema constants
│   ├── validator.py      # Centralized sanitization, regex & boundary validation
│   ├── detector.py       # Modular exact duplicate detection engine
│   ├── storage.py        # Synchronized CSV/JSON persistence & crash recovery
│   ├── query.py          # Keyword search, category/status filtering, pagination
│   ├── analytics.py      # Live summary metrics, averages, trends
│   ├── warnings.py       # Overdue deadlines, anomalies & critical limit flags
│   ├── charts.py         # Matplotlib PNG chart generation (Agg backend)
│   ├── exporter.py       # Markdown, Plain-Text audit log & CSV exports
│   ├── importer.py       # Bulk CSV import with row-by-row error log
│   └── routes.py         # Flask HTTP & JSON API routes
├── data/
│   ├── sample_dataset.json        # 40-entry realistic sample dataset (JSON)
│   ├── sample_dataset.csv         # 40-entry realistic sample dataset (CSV)
│   ├── sample_bulk_import_test.csv# 10-row test CSV (5 valid + 5 invalid rows)
│   ├── records.json               # Live JSON storage
│   └── records.csv                # Live CSV storage
├── static/
│   ├── css/style.css
│   └── js/app.js
├── templates/
│   └── index.html
├── tests/
│   └── test_duplicate_finder.py
├── app.py                # Flask entry point
├── requirements.txt
└── run_app.ps1
```

---

## Setup & Execution Instructions

### 1. Create and Activate Python Virtual Environment

From inside `duplicate_text_finder/`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Run the Web Application

```powershell
python app.py
```

Or use the convenience PowerShell launcher:

```powershell
.\run_app.ps1
```

Then open your browser at: **http://127.0.0.1:5050**

### 4. Run Automated Tests

```powershell
python -m unittest discover -s tests -v
```
