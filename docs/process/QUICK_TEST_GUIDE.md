# QUICK_TEST_GUIDE.md — BMA-Plan UI Manual Test Checklist

Last updated: 2026-05-09
Applies to: proto/ui.html (Fast UI Testability Polish sprint)

---

## Prerequisites

1. Server running: `uvicorn server:app --port 8011`
2. PDF available: `20250616_RAMA4 APARTMENT PERMIT rev 1.pdf` in root
3. Browser: Chrome or Edge, viewport 1440×900

---

## Test 1: Empty State Landing Screen

**Steps:**
1. Open `http://localhost:8011` without a PDF loaded
2. Confirm the empty state card shows:
   - Title: "BMA-Plan"
   - Three action buttons: 📂 เปิด PDF | ตัวอย่าง | 📂 Project
   - Workflow steps: 1 เปิด PDF → 2 Set Scale → 3 Page Setup → 4 Measure → 5 Review → 6 Export
3. Click "ตัวอย่าง" — confirm PDF loads and empty state disappears

**Pass:** Empty state visible, buttons clickable, sample loads

---

## Test 2: Open PDF and Set Scale

**Steps:**
1. Open PDF via "เปิด PDF" button in topbar or empty state
2. Confirm:
   - `#scale-badge` shows orange/warn state
   - `Set Scale` button in topbar shows orange highlight (`.scale-cta`)
   - Scale notice overlay appears at bottom
3. Click Set Scale, draw calibration line, enter distance (e.g. 7.71), confirm
4. Confirm:
   - Scale badge turns green
   - `Set Scale` button loses orange highlight
   - Scale notice changes to "พร้อมวัดพื้นที่"

**Pass:** Scale CTA visually prominent before setting, disappears after

---

## Test 3: Page Info in Sidebar

**Steps:**
1. After PDF loaded: check `#lp-page-info` strip below sidebar header
2. Confirm it shows: `ชื่อหน้า · tag category · scale status`
3. Navigate to another page — confirm info updates

**Pass:** Page info reflects current page name, tag, and scale state

---

## Test 4: Topbar Zone-A Visual Grouping

**Steps:**
1. Observe topbar zone-a with PDF loaded
2. Confirm visual separator (thin line) between "ตัวอย่าง" and "Set Scale"
3. File group: เปิด PDF | เปิด Project | ตัวอย่าง
4. Workflow group: Set Scale | Page Setup

**Pass:** Two groups visually separated

---

## Test 5: Left Panel Tab Switching

**Steps:**
1. Click "Objects" tab — confirm objects list area appears, sheets/search hidden
2. Click "Properties" tab — confirm properties editor appears
3. Click "Sheets" tab — confirm full sidebar content restored
4. Draw an area polygon, click on canvas — confirm Properties tab activates automatically

**Pass:** Tabs switch correctly, auto-switch on selection

---

## Test 6: Left Properties Panel Sections (Sprint 6)

**Steps:**
1. Select any object to activate Properties tab
2. Confirm three sections visible:
   - **Basic**: Object, Name, Layer, Type, Parent (for openings)
   - **Measurement**: Color, Opacity, Label, Gross/Net metrics
   - **Metadata**: Semantic Tag, Use Category, Profile, Category, Report, Count Rule
3. Edit Name — confirm canvas label updates

**Pass:** Three sections, fields functional

---

## Test 7: Right Panel Layers-First

**Steps:**
1. After PDF loads, right panel should show Layers section at top
2. Confirm layer rows: พื้นที่หลัก, พื้นที่ย่อย, ช่องว่าง, เส้นอ้างอิง, ป้าย
3. Each row has: count, visibility toggle (👁), lock toggle (🔒/🔓)
4. Confirm "Legacy / Compatibility" note appears below layers
5. Select an object — confirm Properties section appears below layers

**Pass:** Layers section first, compat sections below with note

---

## Test 8: Review / Check Panel (Sprint 8)

**Steps:**
1. Draw some areas and openings (including one without a name, one unlinked opening)
2. Click "สรุป" button in topbar
3. Confirm check panel opens with:
   - Measurement summary (พื้นที่, ที่ดิน, ช่องว่าง, สุทธิ)
   - QA Warnings section with sub-groups: ⚠ Warning and ℹ Info
   - If no warnings: green checkmark "✓ ไม่พบ warning เบื้องต้น"
4. Click ↻ to refresh

**Pass:** Warnings grouped by severity (error / warning / info)

---

## Test 9: Export Panel Readiness (Sprint 9)

**Steps:**
1. With measured areas in place, click "Export รายงาน"
2. Confirm export panel shows readiness summary bar:
   - พื้นที่ N รายการ (X.X ตร.ม.)
   - ที่ดิน X.X ตร.ม.
   - Scale: ✓ พร้อม or ⚠ ยังไม่ตั้ง
   - QA: ✓ ผ่าน or ⚠ N warnings
3. Confirm Excel Export button works

**Pass:** Readiness bar shown, export functions work

---

## Test 10: Core Workflow Regression

**Steps:**
1. Open PDF
2. Set Scale (calibration)
3. Page Setup (assign page tags)
4. Draw area polygon (พื้นที่)
5. Draw opening inside it and link parent
6. Export Excel — confirm file downloads

**Stop if any step fails.**

**Pass:** Full workflow completes without error

---

## Automated Tests

Run after any manual test session:

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py   # PASS
python proto/e2e_ui_test.py smoke                             # PASS
python proto/e2e_ui_test.py full                              # PASS
```
