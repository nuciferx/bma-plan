# Invent — Print canvas view (with measurement overlays) per page

- **idea_id:** ideas-2026-05-19-print-canvas-per-page
- **Captured:** 2026-05-19 17:15 via /idea
- **Status:** invent-at-checkpoint
- **Source:** `~/.claude/ideas/IDEAS.md` @ 2026-05-19 17:15
- **Backlog row:** `docs/status/PHASE_INDEX.md` → § ideas 2026-05-19
- **Tags:** bma-plan, export, print, p-med

## Raw idea
> สั่ง print ใน canvas ในแต่ละหน้าได้

## Open questions (from /idea)
1. ส่งเครื่องพิมพ์จริง หรือ export PDF/PNG?
2. ทีละหน้าที่เลือกอยู่ หรือทุกหน้าครั้งเดียว?

## Research

### 1. In-repo prior art

- `/export-pdf` endpoint (`proto/server.py:593–700+`) — fully functional PDF+annotations export using PyMuPDF. Flattens measurement overlays (polys, lines, refs, parking, dimensions) onto the source PDF, handles rotation, renders per-selected page. **This is the incumbent export path for "print canvas with overlays."**
- `RUN_EXPORT_READY_PANEL_POLISH.md` (2026-05-10) — export widget already surfaces XLSX/page selection + scale/report-target checklist. No print-specific UX yet.
- No existing `canvas.toDataURL()` / PNG export / `window.print()` infrastructure in `proto/ui.html` — canvas render is JPEG only (server-side via `/page/{n}`).
- `/export-xlsx` + `/export-xlsx-summary` (`proto/server.py:809–1500+`) — measurement data export to Excel, not canvas visual export.

**Key finding:** The "print canvas view with measurement overlays" **already exists as PDF+annotations export**. The open question is whether the user wants (1) an alternative channel (direct printer / PNG / HTML-printable view) or (2) UX improvement on the existing PDF path.

### 2. Library scan

| lib | claim | status | note |
|---|---|---|---|
| jsPDF + html2canvas | client-side HTML→PDF generation; canvas-aware via `toDataURL()` | viable but non-ideal | MIT, ~80–120 KB combined gzip. Single-file inline-JS context = foot-gun. |
| html2pdf.js | pure JS wrapper combining jsPDF + html2canvas | viable but non-ideal | MIT. Simpler API but same dependency burden. |
| print-js | client-side print window for HTML/PDF/image | viable but non-ideal | MIT, ~15 KB. Opens `window.print()` with content — does NOT generate PDF. Best for printer-only flow. |
| canvas native `toDataURL()` | browser canvas → data URL PNG/JPEG | viable, lightweight | Zero dependencies. **Best fit for inline-JS context** if printer-flow desired. |

**Verdict:** Direct-to-printer → `toDataURL()` + `window.print()` (zero deps). PDF file export → existing `/export-pdf` is already superior (server-side PyMuPDF rendering, rotation aware).

### 3. CAD / GIS / graphics prior art

- **AutoCAD** — Layout viewports + annotative objects. "Plot to PDF" or direct printer. Vector-native, not canvas-render.
- **Bluebeam Revu** — Markup IS the PDF. Export = "save marked PDF." Print = direct printer on the marked PDF. **No "canvas render then print" phase.**
- **Foxit PhantomPDF** — Measurement tools annotate the PDF inline. Print = direct printer on marked PDF. No canvas-render step.
- **QGIS** — Layout mode → server-renders to PDF/PNG. Desktop CAD, no browser canvas.
- **PlanGrid** — Server-renders marked PDF. No separate "print canvas view" step.

**Key finding:** Incumbents do NOT have a distinct "render canvas, then print" phase. They either (a) mark the native PDF, (b) use layout viewports, or (c) server-render the result.

### 4. Literature / algorithms

- **Browser print model (`@media print`)** — declarative, operates on the DOM. Canvas elements don't print directly; must convert via `toDataURL()` to `<img>`. Standard pattern.
- **Canvas resolution for print** — default 96 DPI vs print 300+ DPI. Need `devicePixelRatio` scaling or server-side render. BMA-Plan already renders at `RS=1.5` via PyMuPDF.
- **Multi-page print** — `@media print` + `page-break-after: always` per page div. No native canvas-per-page pagination.

**Key finding:** Browser-native canvas print is low-resolution and requires manual page iteration. Server-side rendering (existing `/export-pdf`) is superior.

### 5. Competitor measurement UX

- **Bluebeam Revu** — "Save marked PDF" or "Print marked PDF (direct printer)." No intermediate export.
- **Foxit / PlanGrid / Procore / On-Screen Takeoff** — Mark the PDF → export marked PDF or data table. No "canvas → print" workflow.

**Key finding:** None of the incumbents have a distinct "print canvas view" feature.

---

### Verdict: **PRIOR_ART_MATURE** (with caveat)

The feature the user asked for — "print canvas view with measurement overlays per page" — is **already fully implemented** via `/export-pdf`. It flattens overlays onto the PDF, supports selected pages, handles rotation.

**Open questions resolve to:**
1. **"export PDF/PNG?"** → PDF export already exists. PNG would be a new endpoint.
2. **"ทีละหน้า / ทุกหน้า?"** → existing path already supports both (user picks pages in Export panel).

Per `/bma-invent` MATURE rule: SKIP diverge/score/spike. Go directly to CHECKPOINT.

## Recommendation

The user has **3 distinct paths**, and only the human can decide which one is wanted:

### Path A — **No new sprint** (educate)
The existing PDF+annotations export already does "print canvas overlays per page." Just teach the user: Export Panel → PDF+annotations → pick pages → save → print the result. **Cost: 0 LOC**. Likely if the user didn't realize this existed.

### Path B — **Add "Print to printer" button** (small UX)
Add a button beside the existing PDF export: opens `window.print()` on a synthetic page that embeds `canvas.toDataURL()` per selected page with `page-break-after: always`. Bypasses "save PDF first, then open, then print" friction.
- **Cost:** ~50–80 LOC in `proto/ui.html` only. No server change. No forbidden surface touched.
- **Risk:** Print resolution is `RS=1.5` canvas at 96 DPI — looks fuzzy on 300+ DPI printers. Mitigation: server-render fresh at 2× via existing `/page/{n}?scale=…` or just call `/export-pdf` + auto-open + auto-print.
- **Sprint card:** normal sprint, no invent needed.

### Path C — **Add `/export-png` endpoint** (new export channel)
ZIP of high-resolution PNGs per page (canvas + overlays). Useful if user wants to embed in slides / docs / reports.
- **Cost:** ~120–180 LOC server (`/export-png`) + ~40 LOC UI button. Server uses existing render pipeline + draws overlays via Pillow.
- **Risk:** Overlay rendering on server needs to match canvas exactly (the same poly/path/dim math). The `/export-pdf` codepath already does this via PyMuPDF; mirroring it for raster output is mechanical.
- **Sprint card:** normal sprint, no invent needed.

**My recommendation:** **Path A first** (zero work, may resolve immediately). If user still wants more, **Path B** (printer button) is the cheapest win — fixes the "save → open → print" friction without a new export format.

## Decision

**2026-05-19 — GO (Path B + Path C bundle)**

User chose to ship both:
- **Path B** → `INV-2026-05-19-003a` Print to printer button (~50-80 LOC, `ui.html` only, zero forbidden-surface, zero schema)
- **Path C** → `INV-2026-05-19-003b` `/export-png` ZIP endpoint (~160-220 LOC server + UI, depends-on 003a for UX alignment, requires `full` E2E)

Sprint cards filed in `docs/status/PHASE_INDEX.md` § Active sprint queue (queued). `/bma-dev-loop` will pick them up. Path A (educate) NOT selected — user wants the new affordances despite existing `/export-pdf` coverage.

Status: **invent-done-go** → handed off to dev loop.
