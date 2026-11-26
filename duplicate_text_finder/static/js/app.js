(() => {
  "use strict";

  const VIEW_META = {
    welcome: {
      title: "Welcome to Duplicate Text Finder",
      subtitle: "Compare text entries, catch exact duplicates, validate records, and analyze local CSV/JSON datasets.",
    },
    add: {
      title: "Add & Validate Text Entry",
      subtitle: "Submit a new record with centralized defensive sanitization and boundary validation.",
    },
    detect: {
      title: "Core Duplicate Detection Engine",
      subtitle: "Compare stored records or multi-line batches using strict exact text matching.",
    },
    records: {
      title: "Record Query, Search & Explorer",
      subtitle: "Search by keyword, filter by category or duplicate status, and browse paginated tables.",
    },
    analytics: {
      title: "Executive Summary, Charts & Warnings",
      subtitle: "Live metrics, Matplotlib visualizations, and automated threshold warning flags.",
    },
    io: {
      title: "Bulk CSV Import & Multi-Format Export",
      subtitle: "Import CSV files with row-by-row error logs or export Markdown, TXT, and CSV reports.",
    },
    settings: {
      title: "Local Storage Health & Threshold Rules",
      subtitle: "Inspect CSV/JSON persistence status, manage sample data, and configure warning limits.",
    },
  };

  let currentPage = 1;

  function escapeHtml(value) {
    const str = value === null || value === undefined ? "" : String(value);
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function showToast(message, type = "success") {
    const container = document.getElementById("toast-container");
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => {
      toast.remove();
    }, 3600);
  }

  async function apiFetch(url, options = {}) {
    const response = await fetch(url, options);
    const contentType = response.headers.get("content-type") || "";
    let data = null;
    if (contentType.includes("application/json")) {
      data = await response.json();
    } else {
      data = await response.text();
    }
    return { ok: response.ok, status: response.status, data };
  }

  function switchView(viewName) {
    document.querySelectorAll(".view").forEach((el) => el.classList.remove("active"));
    document.querySelectorAll(".nav-item").forEach((el) => el.classList.remove("active"));

    const targetView = document.getElementById(`view-${viewName}`);
    const targetNav = document.querySelector(`.nav-item[data-view="${viewName}"]`);
    if (targetView) targetView.classList.add("active");
    if (targetNav) targetNav.classList.add("active");

    const meta = VIEW_META[viewName] || VIEW_META.welcome;
    document.getElementById("page-heading").textContent = meta.title;
    document.getElementById("page-subheading").textContent = meta.subtitle;

    // Close mobile sidebar after selection
    document.getElementById("sidebar").classList.remove("open");

    if (viewName === "welcome") loadDashboardSummary();
    if (viewName === "detect") runStoredDetection();
    if (viewName === "records") loadRecordsTable();
    if (viewName === "analytics") loadAnalyticsAndCharts();
    if (viewName === "settings") loadSettingsView();
  }

  function clearFieldErrors(prefix = "err-") {
    document.querySelectorAll(`[id^="${prefix}"]`).forEach((el) => {
      el.textContent = "";
    });
    document.querySelectorAll(".input-invalid").forEach((el) => {
      el.classList.remove("input-invalid");
    });
  }

  function renderKpis(containerId, items) {
    const el = document.getElementById(containerId);
    el.innerHTML = items
      .map(
        (item) => `
        <div class="kpi-box">
          <span class="kpi-label">${escapeHtml(item.label)}</span>
          <div class="kpi-val ${escapeHtml(item.cls || "")}">${escapeHtml(item.value)}</div>
        </div>
      `
      )
      .join("");
  }

  /* ---------------- WELCOME / HEALTH ---------------- */
  async function loadDashboardSummary() {
    try {
      const res = await apiFetch("/api/analytics");
      if (!res.ok) return;
      const { metrics, storage } = res.data;

      document.getElementById("welcome-total").textContent = metrics.total_records;
      document.getElementById("welcome-unique").textContent = metrics.unique_entries;
      document.getElementById("welcome-duplicates").textContent = metrics.duplicate_entries;
      document.getElementById("welcome-warnings").textContent = metrics.warnings.length;

      document.getElementById("sidebar-record-count").textContent =
        `${metrics.total_records} record(s) · CSV & JSON`;

      const chip = document.getElementById("global-status-chip");
      chip.textContent = metrics.status_label;
      chip.className = `status-chip ${metrics.status_level}`;

      if (storage && storage.recovered && storage.recovery_events.length) {
        showToast(storage.recovery_events[0], "success");
      }
    } catch (_err) {
      showToast("Could not connect to Flask backend.", "error");
    }
  }

  /* ---------------- VIEW 2: ADD & VALIDATE ENTRY ---------------- */
  function initAddForm() {
    const catSelect = document.getElementById("input-category-select");
    const catCustom = document.getElementById("input-category-custom");
    const form = document.getElementById("add-record-form");
    const banner = document.getElementById("add-form-banner");
    const resultCard = document.getElementById("add-result-card");

    catSelect.addEventListener("change", () => {
      if (catSelect.value === "__custom__") {
        catCustom.classList.remove("hidden");
        catCustom.focus();
      } else {
        catCustom.classList.add("hidden");
      }
    });

    document.getElementById("btn-reset-add-form").addEventListener("click", () => {
      form.reset();
      catCustom.classList.add("hidden");
      banner.classList.add("hidden");
      resultCard.classList.add("hidden");
      clearFieldErrors();
    });

    // Validation demo presets
    document.querySelectorAll(".preset-invalid, .preset-valid").forEach((btn) => {
      btn.addEventListener("click", () => {
        clearFieldErrors();
        banner.classList.add("hidden");
        resultCard.classList.add("hidden");
        const preset = btn.dataset.preset;
        document.getElementById("input-text").value = "Sample diagnostic entry";
        catSelect.value = "General";
        catCustom.classList.add("hidden");
        document.getElementById("input-priority").value = "3";
        document.getElementById("input-source").value = "Manual Entry";
        document.getElementById("input-due-date").value = "";
        document.getElementById("input-notes").value = "";

        if (preset === "blank") {
          document.getElementById("input-text").value = "   ";
        } else if (preset === "bad-priority") {
          document.getElementById("input-priority").value = "99";
        } else if (preset === "bad-date") {
          document.getElementById("input-due-date").value = "2026-02-30";
        } else if (preset === "bad-category") {
          catSelect.value = "__custom__";
          catCustom.classList.remove("hidden");
          catCustom.value = "Bad@Cat!";
        } else if (preset === "valid-dup") {
          document.getElementById("input-text").value = "alice.chen@example.com";
          catSelect.value = "Customer";
          document.getElementById("input-notes").value = "Added via UI demonstration";
        }
        form.requestSubmit();
      });
    });

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      clearFieldErrors();
      banner.classList.add("hidden");
      resultCard.classList.add("hidden");

      const categoryVal =
        catSelect.value === "__custom__" ? catCustom.value : catSelect.value;

      const payload = {
        text: document.getElementById("input-text").value,
        category: categoryVal,
        priority: document.getElementById("input-priority").value,
        source: document.getElementById("input-source").value,
        due_date: document.getElementById("input-due-date").value,
        notes: document.getElementById("input-notes").value,
      };

      const res = await apiFetch("/api/records", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        banner.textContent = res.data.error || "Please fix the invalid fields below.";
        banner.className = "form-banner error";
        const errors = res.data.errors || {};
        Object.entries(errors).forEach(([field, msg]) => {
          const errEl = document.getElementById(`err-${field}`);
          if (errEl) errEl.textContent = msg;
          const inputMap = {
            text: "input-text",
            category: catSelect.value === "__custom__" ? "input-category-custom" : "input-category-select",
            priority: "input-priority",
            source: "input-source",
            due_date: "input-due-date",
            notes: "input-notes",
          };
          const targetInput = document.getElementById(inputMap[field]);
          if (targetInput) targetInput.classList.add("input-invalid");
        });
        showToast("Validation caught invalid input. Edit fields and retry.", "error");
        return;
      }

      const rec = res.data.record;
      const analysis = res.data.analysis;
      banner.textContent = res.data.message;
      banner.className = "form-banner success";

      const dupBadge = analysis && analysis.is_duplicate
        ? `<span class="badge badge-red">EXACT DUPLICATE (${analysis.occurrence_count}x in storage)</span>`
        : `<span class="badge badge-teal">UNIQUE ENTRY (1x in storage)</span>`;

      resultCard.innerHTML = `
        <strong>Saved Record ${escapeHtml(rec.record_id)}</strong> ${dupBadge}
        <div class="mt-sm"><strong>Text:</strong> <code>${escapeHtml(rec.text)}</code></div>
        <div><strong>Category:</strong> ${escapeHtml(rec.category)} · <strong>Priority:</strong> P${escapeHtml(rec.priority)}</div>
      `;
      resultCard.classList.remove("hidden");
      showToast(`Saved ${rec.record_id} to CSV & JSON`);
      loadDashboardSummary();
    });
  }

  /* ---------------- VIEW 3: DUPLICATE DETECTION ---------------- */
  function renderNearVariantBox(boxId, hints) {
    const box = document.getElementById(boxId);
    if (!hints || !hints.length) {
      box.classList.add("hidden");
      box.innerHTML = "";
      return;
    }
    const itemsHtml = hints
      .slice(0, 6)
      .map(
        (h) =>
          `<li>${h.distinct_exact_variants.map((v) => `<code>${escapeHtml(v)}</code>`).join(" vs ")}</li>`
      )
      .join("");
    box.innerHTML = `
      <strong>Exact-Match Integrity Note (${hints.length} near-variant set(s) kept separate):</strong>
      These entries differ in capitalization or outer spaces, so the engine correctly keeps them as distinct entries rather than false duplicates:
      <ul class="mt-sm">${itemsHtml}</ul>
    `;
    box.classList.remove("hidden");
  }

  async function runStoredDetection() {
    const res = await apiFetch("/api/detect/stored", { method: "POST" });
    if (!res.ok) {
      showToast("Failed to run duplicate scan.", "error");
      return;
    }
    const { report, near_variant_hints } = res.data;

    renderKpis("stored-detect-kpis", [
      { label: "Total Records", value: report.total_entries },
      { label: "Unique Entries", value: report.unique_only_count },
      { label: "Duplicate Rows", value: report.duplicate_entry_count },
      { label: "Distinct Dup Texts", value: report.distinct_duplicate_groups },
      { label: "Redundant Copies", value: report.redundant_copy_count },
      { label: "Duplication Rate", value: `${report.duplication_rate_pct}%` },
    ]);

    renderNearVariantBox("stored-near-variants", near_variant_hints);

    const groupsBody = document.querySelector("#stored-dup-groups-table tbody");
    if (!report.duplicate_groups.length) {
      groupsBody.innerHTML = `<tr><td colspan="5">No exact duplicates detected in stored records.</td></tr>`;
    } else {
      groupsBody.innerHTML = report.duplicate_groups
        .map(
          (g, idx) => `
          <tr>
            <td>#${idx + 1}</td>
            <td><span class="badge badge-red">${g.occurrence_count}x</span></td>
            <td class="text-cell">${escapeHtml(g.text)}</td>
            <td>${escapeHtml(g.record_ids.join(", "))}</td>
            <td>${escapeHtml(g.categories.join(", "))}</td>
          </tr>
        `
        )
        .join("");
    }

    document.getElementById("stored-dup-count").textContent = report.duplicate_entries.length;
    const dupBody = document.querySelector("#stored-dup-entries-table tbody");
    dupBody.innerHTML = report.duplicate_entries.length
      ? report.duplicate_entries
          .map(
            (e) => `
            <tr>
              <td><code>${escapeHtml(e.record_id)}</code></td>
              <td><span class="badge badge-red">${e.occurrence_count}x</span></td>
              <td>${escapeHtml(e.category)}</td>
              <td class="text-cell">${escapeHtml(e.text)}</td>
            </tr>
          `
          )
          .join("")
      : `<tr><td colspan="4">None</td></tr>`;

    document.getElementById("stored-unique-count").textContent = report.unique_entries.length;
    const uniqBody = document.querySelector("#stored-unique-entries-table tbody");
    uniqBody.innerHTML = report.unique_entries.length
      ? report.unique_entries
          .map(
            (e) => `
            <tr>
              <td><code>${escapeHtml(e.record_id)}</code></td>
              <td>${escapeHtml(e.category)}</td>
              <td class="text-cell">${escapeHtml(e.text)}</td>
            </tr>
          `
          )
          .join("")
      : `<tr><td colspan="3">None</td></tr>`;
  }

  function initDetectView() {
    document.querySelectorAll(".tab-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
        document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
        btn.classList.add("active");
        document.getElementById(`tab-${btn.dataset.tab}`).classList.add("active");
      });
    });

    document.getElementById("btn-run-stored-detect").addEventListener("click", runStoredDetection);

    document.getElementById("btn-batch-sample").addEventListener("click", () => {
      document.getElementById("batch-file-input").value = "";
      document.getElementById("batch-textarea").value = [
        "Invoice #1042 approved",
        "Error 504: Gateway timeout",
        "Invoice #1042 approved",
        "invoice #1042 approved",
        "SKU-5510 USB-C Dock",
        "Error 504: Gateway timeout",
        "Error 504: Gateway timeout",
        "Unique onboarding checklist item",
      ].join("\n");
    });

    document.getElementById("batch-compare-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      clearFieldErrors("err-batch_");
      const banner = document.getElementById("batch-form-banner");
      banner.classList.add("hidden");

      const fileInput = document.getElementById("batch-file-input");
      const saveFlag = document.getElementById("batch-save-checkbox").checked;
      const category = document.getElementById("batch-category").value;
      const priority = document.getElementById("batch-priority").value;

      let res;
      if (fileInput.files && fileInput.files.length > 0) {
        const fd = new FormData();
        fd.append("file", fileInput.files[0]);
        fd.append("save_to_storage", String(saveFlag));
        fd.append("category", category);
        fd.append("priority", priority);
        res = await apiFetch("/api/detect/batch", { method: "POST", body: fd });
      } else {
        res = await apiFetch("/api/detect/batch", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            batch_text: document.getElementById("batch-textarea").value,
            save_to_storage: saveFlag,
            category,
            priority,
          }),
        });
      }

      if (!res.ok) {
        banner.textContent = res.data.error || "Batch validation failed.";
        banner.className = "form-banner error";
        const errors = res.data.errors || {};
        Object.entries(errors).forEach(([k, msg]) => {
          const el = document.getElementById(`err-${k}`);
          if (el) el.textContent = msg;
        });
        return;
      }

      const { report, near_variant_hints, saved_to_storage_count } = res.data;
      if (saved_to_storage_count > 0) {
        banner.textContent = `Comparison complete and saved ${saved_to_storage_count} entries to local CSV & JSON storage.`;
        banner.className = "form-banner success";
        loadDashboardSummary();
      }

      renderKpis("batch-detect-kpis", [
        { label: "Lines Compared", value: report.total_entries },
        { label: "Unique Lines", value: report.unique_only_count },
        { label: "Duplicate Lines", value: report.duplicate_entry_count },
        { label: "Duplicate Groups", value: report.distinct_duplicate_groups },
        { label: "Duplication Rate", value: `${report.duplication_rate_pct}%` },
      ]);

      renderNearVariantBox("batch-near-variants", near_variant_hints);

      const dupBody = document.querySelector("#batch-dup-table tbody");
      dupBody.innerHTML = report.duplicate_groups.length
        ? report.duplicate_groups
            .map(
              (g) => `
              <tr>
                <td><span class="badge badge-red">${g.occurrence_count}x</span></td>
                <td class="text-cell">${escapeHtml(g.text)}</td>
              </tr>
            `
            )
            .join("")
        : `<tr><td colspan="2">No exact duplicates in this batch.</td></tr>`;

      const uniqBody = document.querySelector("#batch-unique-table tbody");
      uniqBody.innerHTML = report.unique_entries.length
        ? report.unique_entries
            .map(
              (u) => `
              <tr>
                <td><code>${escapeHtml(u.record_id)}</code></td>
                <td class="text-cell">${escapeHtml(u.text)}</td>
              </tr>
            `
            )
            .join("")
        : `<tr><td colspan="2">No unique entries in this batch.</td></tr>`;

      document.getElementById("batch-results-area").classList.remove("hidden");
    });
  }

  /* ---------------- VIEW 4: RECORDS EXPLORER & SEARCH ---------------- */
  async function loadRecordsTable(page = currentPage) {
    currentPage = page;
    const params = new URLSearchParams({
      keyword: document.getElementById("filter-keyword").value,
      category: document.getElementById("filter-category").value,
      status: document.getElementById("filter-status").value,
      priority: document.getElementById("filter-priority").value,
      sort_by: document.getElementById("filter-sort").value,
      per_page: document.getElementById("filter-per-page").value,
      page: String(currentPage),
    });

    const res = await apiFetch(`/api/records?${params.toString()}`);
    if (!res.ok) {
      showToast(res.data.error || "Failed to load records.", "error");
      return;
    }

    const { items, pagination, available_categories } = res.data;

    // Populate category dropdown dynamically while preserving selection
    const catSelect = document.getElementById("filter-category");
    const prevCat = catSelect.value;
    catSelect.innerHTML = `<option value="all">All Categories</option>` +
      available_categories
        .map((c) => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`)
        .join("");
    if (available_categories.includes(prevCat) || prevCat === "all") {
      catSelect.value = prevCat;
    }

    const tbody = document.querySelector("#records-table tbody");
    if (!items.length) {
      tbody.innerHTML = `<tr><td colspan="9">No records match the current search or filter criteria.</td></tr>`;
    } else {
      tbody.innerHTML = items
        .map((item) => {
          const statusBadge = item.is_duplicate
            ? `<span class="badge badge-red">DUP (${item.occurrence_count}x)</span>`
            : `<span class="badge badge-teal">UNIQUE</span>`;
          return `
            <tr>
              <td><code>${escapeHtml(item.record_id)}</code></td>
              <td>${statusBadge}</td>
              <td class="text-cell">${escapeHtml(item.text)}</td>
              <td>${escapeHtml(item.category)}</td>
              <td>${escapeHtml(item.source)}</td>
              <td>P${escapeHtml(item.priority)}</td>
              <td>${escapeHtml(item.due_date || "-")}</td>
              <td>${escapeHtml((item.created_at || "").replace("T", " "))}</td>
              <td>
                <button class="btn btn-outline btn-sm btn-del-rec" data-id="${escapeHtml(item.record_id)}" type="button">Delete</button>
              </td>
            </tr>
          `;
        })
        .join("");
    }

    tbody.querySelectorAll(".btn-del-rec").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const id = btn.dataset.id;
        const delRes = await apiFetch(`/api/records/${encodeURIComponent(id)}`, { method: "DELETE" });
        if (delRes.ok) {
          showToast(delRes.data.message);
          loadRecordsTable(currentPage);
          loadDashboardSummary();
        } else {
          showToast(delRes.data.error || "Delete failed.", "error");
        }
      });
    });

    document.getElementById("pagination-info").textContent =
      `Showing ${pagination.showing_from}–${pagination.showing_to} of ${pagination.total_matched} matched (${pagination.total_records} total stored)`;
    document.getElementById("page-indicator").textContent =
      `Page ${pagination.page} / ${pagination.total_pages}`;
    document.getElementById("btn-prev-page").disabled = !pagination.has_prev;
    document.getElementById("btn-next-page").disabled = !pagination.has_next;
  }

  function initRecordsView() {
    document.getElementById("btn-apply-filters").addEventListener("click", () => loadRecordsTable(1));
    document.getElementById("filter-keyword").addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        loadRecordsTable(1);
      }
    });
    document.getElementById("btn-clear-filters").addEventListener("click", () => {
      document.getElementById("filter-keyword").value = "";
      document.getElementById("filter-category").value = "all";
      document.getElementById("filter-status").value = "all";
      document.getElementById("filter-priority").value = "all";
      document.getElementById("filter-sort").value = "newest";
      loadRecordsTable(1);
    });
    ["filter-category", "filter-status", "filter-priority", "filter-sort", "filter-per-page"].forEach((id) => {
      document.getElementById(id).addEventListener("change", () => loadRecordsTable(1));
    });
    document.getElementById("btn-prev-page").addEventListener("click", () => {
      if (currentPage > 1) loadRecordsTable(currentPage - 1);
    });
    document.getElementById("btn-next-page").addEventListener("click", () => {
      loadRecordsTable(currentPage + 1);
    });
  }

  /* ---------------- VIEW 5: ANALYTICS, CHARTS & WARNINGS ---------------- */
  async function loadAnalyticsAndCharts() {
    const res = await apiFetch("/api/analytics");
    if (!res.ok) {
      showToast("Failed to compute analytics.", "error");
      return;
    }
    const { metrics } = res.data;

    renderKpis("analytics-kpi-row", [
      { label: "Total Records", value: metrics.total_records },
      { label: "Unique Entries", value: metrics.unique_entries },
      { label: "Duplicate Rows", value: metrics.duplicate_entries },
      { label: "Redundant Copies", value: metrics.redundant_copies },
      { label: "Duplication Rate", value: `${metrics.duplication_rate_pct}%` },
      { label: "Avg Length (chars)", value: `${metrics.avg_text_length} (σ=${metrics.std_dev_text_length})` },
      { label: "Avg Words", value: metrics.avg_word_count },
      { label: "Avg Priority", value: `${metrics.avg_priority} / 5` },
    ]);

    // Warnings
    const warnBadge = document.getElementById("warnings-count-badge");
    warnBadge.textContent = `${metrics.warnings.length} Flag(s)`;
    const warnList = document.getElementById("warnings-list");
    if (!metrics.warnings.length) {
      warnList.innerHTML = `<div class="warning-card info"><h5>All Clear</h5><p>No overdue deadlines, anomalous entries, or threshold breaches detected.</p></div>`;
    } else {
      warnList.innerHTML = metrics.warnings
        .map(
          (w) => `
          <div class="warning-card ${escapeHtml(w.severity)}">
            <span class="badge ${w.severity === "critical" ? "badge-red" : w.severity === "warning" ? "badge-amber" : "badge-blue"}">${escapeHtml(w.severity.toUpperCase())} · ${escapeHtml(w.warning_type)}</span>
            <h5>${escapeHtml(w.title)}</h5>
            <p>${escapeHtml(w.message)}</p>
            <div class="field-hint">Rule: <code>${escapeHtml(w.rule)}</code></div>
            ${w.affected_record_ids.length ? `<div class="field-hint">Affected IDs: ${escapeHtml(w.affected_record_ids.join(", "))}</div>` : ""}
          </div>
        `
        )
        .join("");
    }

    // Category table
    const catBody = document.querySelector("#analytics-category-table tbody");
    catBody.innerHTML = metrics.category_breakdown.length
      ? metrics.category_breakdown
          .map(
            (c) => `
            <tr>
              <td><strong>${escapeHtml(c.category)}</strong></td>
              <td>${c.total}</td>
              <td>${c.unique}</td>
              <td>${c.duplicates}</td>
              <td>${c.duplicate_rate_pct}%</td>
              <td>${c.avg_priority}</td>
            </tr>
          `
          )
          .join("")
      : `<tr><td colspan="6">No records yet.</td></tr>`;

    // Top duplicates table
    const topBody = document.querySelector("#analytics-top-dups-table tbody");
    topBody.innerHTML = metrics.top_duplicates.length
      ? metrics.top_duplicates
          .map(
            (d) => `
            <tr>
              <td><span class="badge badge-red">${d.occurrence_count}x</span></td>
              <td class="text-cell">${escapeHtml(d.text)}</td>
              <td>${escapeHtml(d.record_ids.join(", "))}</td>
            </tr>
          `
          )
          .join("")
      : `<tr><td colspan="3">No exact duplicates found.</td></tr>`;

    // Refresh Matplotlib PNG images with cache-buster
    const ts = Date.now();
    document.getElementById("chart-distribution").src = `/api/charts/distribution.png?t=${ts}`;
    document.getElementById("chart-categories").src = `/api/charts/categories.png?t=${ts}`;
    document.getElementById("chart-trends").src = `/api/charts/trends.png?t=${ts}`;
  }

  /* ---------------- VIEW 6: IMPORT & EXPORT ---------------- */
  function initImportExportView() {
    document.getElementById("bulk-import-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      clearFieldErrors("err-import_");
      const fileInput = document.getElementById("csv-import-file");
      if (!fileInput.files || !fileInput.files.length) {
        document.getElementById("err-import_file").textContent = "Please choose a .csv file first.";
        return;
      }

      const fd = new FormData();
      fd.append("file", fileInput.files[0]);
      fd.append("dry_run", String(document.getElementById("import-dry-run").checked));

      const res = await apiFetch("/api/import/csv", { method: "POST", body: fd });
      if (!res.ok) {
        document.getElementById("err-import_file").textContent = res.data.error || "CSV import failed.";
        showToast(res.data.error || "CSV import failed.", "error");
        return;
      }

      const { report } = res.data;
      document.getElementById("import-summary-box").classList.remove("hidden");
      renderKpis("import-kpis", [
        { label: "Total Rows", value: report.total_rows },
        { label: "Valid Rows", value: report.valid_count },
        { label: "Invalid Rows", value: report.invalid_count },
        { label: "Saved to Storage", value: report.storage_updated ? "Yes" : "Dry Run" },
      ]);

      const errBody = document.querySelector("#import-errors-table tbody");
      errBody.innerHTML = report.row_errors.length
        ? report.row_errors
            .map((re) => {
              const errMsgs = Object.entries(re.errors)
                .map(([field, msg]) => `<strong>${escapeHtml(field)}:</strong> ${escapeHtml(msg)}`)
                .join("<br>");
              return `
                <tr>
                  <td>Row ${re.row_number}</td>
                  <td>${errMsgs}</td>
                  <td class="text-cell"><code>${escapeHtml(JSON.stringify(re.raw_data))}</code></td>
                </tr>
              `;
            })
            .join("")
        : `<tr><td colspan="3">All rows passed validation with 0 errors.</td></tr>`;

      if (report.storage_updated) {
        showToast(`Imported ${report.valid_count} valid row(s); skipped ${report.invalid_count} invalid row(s).`);
        loadDashboardSummary();
      } else {
        showToast(`Dry run complete: ${report.valid_count} valid, ${report.invalid_count} invalid.`);
      }
    });

    document.querySelectorAll(".btn-preview-export").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const fmt = btn.dataset.fmt;
        const res = await apiFetch(`/api/export/${fmt}?preview=1`);
        if (!res.ok) {
          showToast("Failed to preview export.", "error");
          return;
        }
        document.getElementById("export-preview-title").textContent = `Preview: ${res.data.filename}`;
        document.getElementById("export-preview-content").textContent = res.data.content;
        document.getElementById("export-preview-wrap").classList.remove("hidden");
      });
    });

    document.getElementById("btn-close-preview").addEventListener("click", () => {
      document.getElementById("export-preview-wrap").classList.add("hidden");
    });
  }

  /* ---------------- VIEW 7: STORAGE HEALTH & THRESHOLDS ---------------- */
  async function loadSettingsView() {
    const [healthRes, thRes] = await Promise.all([
      apiFetch("/api/health"),
      apiFetch("/api/thresholds"),
    ]);

    if (healthRes.ok) {
      const s = healthRes.data.storage;
      const healthEl = document.getElementById("storage-health-details");
      const eventsText = s.recovery_events.length
        ? s.recovery_events.join(" | ")
        : "No errors or recovery events";
      healthEl.innerHTML = `
        <div class="health-row"><span>Schema Version</span><strong>${escapeHtml(s.schema_version)}</strong></div>
        <div class="health-row"><span>Active Storage Source</span><strong>${escapeHtml(s.active_source)}</strong></div>
        <div class="health-row"><span>JSON Storage (<code>records.json</code>)</span><strong>${s.json_exists ? "Present & Valid" : "Missing"}</strong></div>
        <div class="health-row"><span>CSV Storage (<code>records.csv</code>)</span><strong>${s.csv_exists ? "Present & Valid" : "Missing"}</strong></div>
        <div class="health-row"><span>Stored Records</span><strong>${s.record_count}</strong></div>
        <div class="health-row"><span>Recovery / Integrity Log</span><span>${escapeHtml(eventsText)}</span></div>
      `;
    }

    if (thRes.ok) {
      const t = thRes.data.thresholds;
      document.getElementById("th-dup-rate").value = t.max_duplication_rate_pct;
      document.getElementById("th-repeat-count").value = t.min_repeat_anomaly_count;
      document.getElementById("th-capacity").value = t.max_records_capacity;
      document.getElementById("th-short-len").value = t.short_text_anomaly_len;
    }
  }

  function initSettingsView() {
    document.getElementById("btn-load-sample").addEventListener("click", async () => {
      const res = await apiFetch("/api/storage/load-sample", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ replace: true }),
      });
      if (res.ok) {
        showToast(res.data.message);
        loadSettingsView();
        loadDashboardSummary();
      } else {
        showToast(res.data.error || "Could not load sample dataset.", "error");
      }
    });

    document.getElementById("btn-clear-storage").addEventListener("click", async () => {
      if (!confirm("Clear all stored records and reset empty CSV/JSON templates?")) return;
      const res = await apiFetch("/api/storage/clear", { method: "POST" });
      if (res.ok) {
        showToast(res.data.message);
        loadSettingsView();
        loadDashboardSummary();
      }
    });

    document.getElementById("thresholds-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      clearFieldErrors("err-");
      const banner = document.getElementById("thresholds-banner");
      banner.classList.add("hidden");

      const payload = {
        max_duplication_rate_pct: document.getElementById("th-dup-rate").value,
        min_repeat_anomaly_count: document.getElementById("th-repeat-count").value,
        max_records_capacity: document.getElementById("th-capacity").value,
        short_text_anomaly_len: document.getElementById("th-short-len").value,
      };
      const res = await apiFetch("/api/thresholds", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        banner.textContent = res.data.error || "Invalid threshold values.";
        banner.className = "form-banner error";
        Object.entries(res.data.errors || {}).forEach(([k, msg]) => {
          const el = document.getElementById(`err-${k}`);
          if (el) el.textContent = msg;
        });
        return;
      }
      banner.textContent = res.data.message;
      banner.className = "form-banner success";
      showToast("Threshold settings saved.");
      loadDashboardSummary();
    });
  }

  /* ---------------- BOOTSTRAP ---------------- */
  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".nav-item").forEach((btn) => {
      btn.addEventListener("click", () => switchView(btn.dataset.view));
    });

    document.querySelectorAll("[data-goto]").forEach((btn) => {
      btn.addEventListener("click", () => switchView(btn.dataset.goto));
    });

    document.getElementById("menu-toggle").addEventListener("click", () => {
      document.getElementById("sidebar").classList.toggle("open");
    });

    document.getElementById("btn-refresh-all").addEventListener("click", () => {
      loadDashboardSummary();
      const activeNav = document.querySelector(".nav-item.active");
      if (activeNav) switchView(activeNav.dataset.view);
    });

    document.getElementById("btn-refresh-analytics").addEventListener("click", loadAnalyticsAndCharts);

    initAddForm();
    initDetectView();
    initRecordsView();
    initImportExportView();
    initSettingsView();
    loadDashboardSummary();
  });
})();
