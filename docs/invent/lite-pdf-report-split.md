# Invent: lite-pdf-report-split

**Idea source:** ~/.claude/ideas/IDEAS.md @ 2026-05-21 19:48 (+ Refinement 19:55)
**Short-name:** lite-pdf-report-split
**Status:** invent-in-progress (started 2026-05-21)
**Tags:** bma-plan, export, lite, p-med

> **One-line:** Lite ส่งออกรายงาน PDF แบบ landscape, 1 หน้ารายงาน = 1 หน้าแปลน — ซ้ายเป็นภาพแปลนเต็มหน้า + overlay พื้นที่ที่วัด, ขวาเป็นตารางพื้นที่ group ตาม semanticTag + subtotal + รวมทั้งหน้า.

---

## Frame (v2 — RESHAPED 2026-05-21 20:10 at human checkpoint)

> **RESHAPE สรุป:** v1 (approach E, backend PyMuPDF สร้าง PDF ตรงๆ) spike PASS แต่ user เปลี่ยนกรอบที่ checkpoint: ต้องการให้ Export **เปิดหน้าเว็บรายงานแยกใหม่ที่แก้ไขเนื้อหาได้แบบ Microsoft Word (WYSIWYG) ก่อน** แล้วค่อยสั่ง print → PDF / เครื่องพิมพ์. ข้อแม้: หน้า UI ใหม่ต้อง**แยกขาด ไม่ทำให้บวม** ("คนละโมเดล" จาก canvas editor หลัก). editability บังคับ render เป็น HTML/DOM → backend-PDF (E/D/A) แก้ไขไม่ได้ จึงตกไป. v1 sections เก็บไว้ใต้ `## v1 attempt (superseded)`. Research (PRIOR_ART_PARTIAL) ยัง valid.

**Problem** — Lite วัดพื้นที่เสร็จแล้ว แต่ผลลัพธ์ยังเป็นแค่ตัวเลขดิบ. ผู้ใช้ต้องการประกอบเป็น "เอกสารรายงาน" ที่ (1) เห็นแปลน + ตารางพื้นที่คู่กันต่อหน้า, (2) **แก้ไข/เกลาเนื้อหาได้เองก่อนส่ง** (แก้ชื่อห้อง, เพิ่มหมายเหตุ, จัดหัวกระดาษ — เหมือนพิมพ์ใน Word), แล้ว (3) สั่งพิมพ์เป็น PDF หรือเครื่องพิมพ์. ปัจจุบันไม่มีขั้นตอนกลาง "เกลาเอกสาร" เลย.

**Constraints (v2)**
- หน้ารายงานต้องเป็น **หน้า/route แยก** จาก canvas หลัก — แยกไฟล์ HTML ของตัวเอง ไม่ยัดเพิ่มใน `ui-lite.html` (กันบวม; CLAUDE.md size discipline: ui.html ใกล้ trigger 5000 บรรทัด)
- editability = HTML/DOM เท่านั้น (backend สร้าง PDF สำเร็จรูปแก้ไม่ได้)
- print path = browser print / save-as-PDF (`@media print` + `@page`) — ไม่พึ่ง headless Chromium ฝั่ง server
- ทำงานบน raster PDF; lite render หน้าเป็น raster อยู่แล้ว
- Phase 1: area only, no legal/FAR
- group ต้องอ่าน `semanticTag`/`reportTarget` ไม่ใช่ `layer.name`
- การแก้ไขในหน้ารายงาน = ephemeral (ไม่บังคับ write กลับ .bmaplan; ถ้าจะ persist ต้อง additive-only)
- ไม่แตะ proto/; spike อยู่ proto/sandbox/

**Forbidden surfaces ที่ต้องเลี่ยง**
- `polyAreaM2`/`polyMetrics`, `pdfToC`/`cToPdf`/`RS`, `.bmaplan` schema, proto/ui.html, proto/server.py, lite engine math

**Success criteria (v2 — วัดได้ใน spike)**
1. เปิดหน้ารายงานเป็น **หน้าแยก** (new window/route) ที่ไม่ผูกกับ DOM ของ canvas editor — รับข้อมูลผ่าน hand-off (sessionStorage/postMessage/URL) ได้
2. แสดง layout ต่อหน้า: แปลน (ภาพ) ซ้าย + ตารางพื้นที่ group ตาม semanticTag ขวา + หัวกระดาษ
3. **แก้ไขได้แบบ Word**: แก้ชื่อแถว/หมายเหตุ/หัวกระดาษได้ inline; ตัวเลขพื้นที่ที่มาจากการวัด = read-only (กัน user แก้ผิดสัญญา raw-geometry) แต่ field ข้อความแก้ได้
4. สั่ง print → ผลลัพธ์ PDF/หน้าเครื่องพิมพ์ตรงกับที่เห็น (WYSIWYG), หน้าแบ่งถูก (1 แปลน = 1 หน้า, `page-break`)
5. หน้ารายงานเป็น standalone — โหลดเองได้ด้วยข้อมูลตัวอย่าง โดยไม่ต้องมี canvas/engine ทำงานพร้อมกัน (พิสูจน์ "คนละโมเดล/ไม่บวม")

**Out of scope (v2)**
- custom branding/theme (โลโก้/สี/ฟอนต์เลือกได้)
- cross-page roll-up (หน้าสรุปรวมทั้งโปรเจกต์)
- การ persist รายงานที่แก้แล้วกลับลง .bmaplan (พิจารณาภายหลัง ถ้าทำต้อง additive)
- การวัดพื้นที่ใหม่ในหน้ารายงาน (รายงานบริโภคผลการวัด ไม่สร้างใหม่)

---

## v1 attempt (superseded by RESHAPE — backend PyMuPDF, no editing)

> เก็บไว้อ้างอิง. v1 framing: Export = ยิง PDF สำเร็จรูปจาก backend ตรงๆ (ไม่มีขั้นแก้ไข). spike approach E PASS แต่ user ต้องการ editable web report → reshape.

### Frame (v1)

**Problem** — Lite วัดพื้นที่เสร็จแล้ว แต่ไม่มีรายงานที่ส่งต่อให้วิศวกร/ผู้ตรวจดูได้ในหน้าเดียว ต้องสลับดูภาพแปลนกับตัวเลขแยกกัน เสียเวลา + ตรวจสอบยาก. ต้องการรายงาน PDF ที่เห็น "แปลน + ตัวเลขพื้นที่ของแปลนนั้น" คู่กันต่อหนึ่งหน้า.

**Constraints**
- Lite backend = Python (FastAPI) + PyMuPDF + openpyxl อยู่แล้ว — ใช้ stack เดิม
- ทำงานบน raster PDF (lite render หน้าเป็น raster อยู่แล้ว ผ่าน `get_pixmap`)
- Phase 1 boundary: รายงานพื้นที่ล้วน ไม่มี legal/FAR/OSR/pass-fail
- Page-scoped layer model: grouping ต้องอ่าน `semanticTag` / `reportTarget` ไม่ใช่ `layer.name`
- `.bmaplan` schema additive-only — ไม่เพิ่ม field "ชั้น" (ใช้ 1 หน้า = 1 floor อยู่แล้ว)
- ห้ามแตะ proto/ (lite แยกขาด); spike ต้องอยู่ใน proto/sandbox/

**Forbidden surfaces ที่ idea นี้ต้องเลี่ยง**
- `polyAreaM2` / `polyMetrics` — area math (อ่านผลลัพธ์ได้ ห้ามแก้)
- `pdfToC` / `cToPdf` / `RS` — coordinate/scale conversion
- `.bmaplan` schema fields
- ไม่แตะ proto/ui.html, proto/server.py, lite engine math

**Success criteria (วัดได้ใน spike)**
1. Render หน้า PDF เป็นภาพ → ฝังในกรอบซ้ายของหน้า landscape ได้ โดยรักษา aspect ratio (zoom-to-fit ไม่บิด)
2. Overlay polygon ที่วัด + label บนภาพซ้าย ตรงตำแหน่ง (ใช้ coordinate transform เดียวกับ overlay export)
3. ตารางขวา group ตาม semanticTag → แสดง subtotal ต่อกลุ่ม + รวมทั้งหน้า ถูกต้องตรงกับ XLSX summary
4. ตาราง + ภาพ อยู่ครบในหน้าเดียวไม่ overflow (A4/A3 landscape) แม้มี object เยอะ (≥15 แถว)
5. หลายหน้า → หลาย report page เรียงต่อกันใน PDF เดียว

**Out of scope (invent pass นี้)**
- การปรับ template/branding แบบ custom (โลโก้, สี, ฟอนต์เลือกได้)
- รายงานข้าม-หน้า (cross-page roll-up หน้าสรุปรวมทั้งโปรเจกต์) — แยกเป็น idea ถัดไป
- การ export กลับเป็น editable (รายงานนี้ read-only)
- Annotation (text/arrow/highlight) บนภาพ — อันนั้นคือ PDF+annotations export ตัวเดิม

## Research

### 1. In-repo prior art

- `proto/server.py:598` `/export-pdf` — rotate + render annotations + text labels บนหน้า raster; ใช้ `page.insert_image(pixmap)` + `page.draw_polyline()` + `page.insert_text()`.
- `lite/server_lite.py:216` `/export-pdf-overlay` — WYSIWYG overlay (rotation-aware) re-render หน้าเป็น raster + วาด shape ทับ. Pattern พิสูจน์แล้ว: `pix = doc[idx].get_pixmap(matrix=fitz.Matrix(RS, RS))` → `page.insert_image()` + `sh.draw_*()`.
- `proto/server.py:953` `/export-xlsx` + `:1552` `/export-xlsx-summary` — per-page aggregation ตาม `semanticTag` / `reportTarget`. JS group object ตาม `semanticTag` อยู่แล้ว.
- `sprints/completed/2026-05-09-export-metadata-columns-xlsx/` — กำหนด contract การ group ตาม `semanticTag`.
- **ยังไม่มี "report layout" ที่รวม image + table ในหน้าเดียว** — split-layout เป็น greenfield ฝั่ง UX แต่ math/render reuse ได้.

### 2. Library scan
- **PyMuPDF (fitz)** — viable, embedded แล้ว. `insert_image()` (พิสูจน์ใน /export-pdf-overlay), `draw_rect()`, `insert_text()`, `insert_table()` (v1.24+, แต่เส้นตารางต้อง `draw_rect()` เอง). **ตัวเลือกเดียวที่เหมาะ.**
- XlsxWriter — Excel-only, วาด PDF ไม่ได้.
- jsPDF + html2canvas (client) — wrong-shape: bypass backend measurement state.
- WeasyPrint — viable แต่ overkill (ต้อง headless Chromium), ไม่อยู่ใน requirements.
- reportlab — viable แต่ PyMuPDF embedded แล้ว ไม่ต้องเพิ่ม dep.

### 3. CAD/GIS prior art
- **Bluebeam Revu** Summary (Table/Flow) — thumbnail หน้า + measurement table หน้าเดียวกัน. ใกล้สุด.
- Foxit — area → CSV only, ไม่มี report layout.
- PlanSwift — area result ใต้ภาพแปลน, linear ไม่ split.
- QGIS Report Builder — map raster + table ผ่าน template (PIL/reportlab).
- **Insight:** Bluebeam "summary-on-same-page" ใกล้สุด; split image-left + table-right เป็น UX advantage ไม่ใช่ทวนกระแส.

### 4. Literature / known algorithms
- PyMuPDF Story layout (v1.21+) — multi-column flow; primitives (Rect slots, text-into-rect) reuse ได้.
- `page.insert_table(table=rows, rect=...)` (v1.24+) — auto-size column/row, row ไม่ split ข้ามหน้า → multi-page table ต้อง paginate เอง.
- Area grouping = shoelace + group-by-semanticTag (มีในโค้ดแล้ว). ไม่มี novel math.

### 5. Competitor UX
- Bluebeam: measure → Summary → Table style → PDF/CSV; thumbnail (~30% width) + table. "Per-floor = per-page".
- Bluebeam "Include Page Content" — แสดงหน้าเดิมเป็น background หลัง summary table. Lite proposal = split variation (ชัดกว่า).

## Diverge (v1)

5 approaches บนแกนต่างกัน:

- **A — Backend split-canvas landscape** (axis: assembly-location/backend). Endpoint ใหม่ `/export-pdf-report` ข้างๆ `/export-pdf-overlay`. fixed split 58/42, `get_pixmap` → `fit_pixmap_into` left rect, manual `draw_rect` grid + `insert_text`. forbidden_touch: NO. dep: none.
- **B — Client HTML + print-CSS split** (axis: assembly-location/client). CSS grid `[58fr 42fr]` ต่อหน้า, `<canvas>` re-render ซ้าย + `<table>` ขวา, `window.print()`. forbidden_touch: NO. dep: none. **แต่ RS=1.5 ≈ 144 DPI → มัวบน printer 300dpi.**
- **C — Hybrid server-pixmap + client-HTML** (axis: data-flow). `/report-pixmap` + client assemble HTML + `/render-html-to-pdf` ผ่าน `fitz.Story`. forbidden_touch: NO. dep: fitz.Story (≥1.21, ต้องตรวจ version). over-engineered.
- **D — Overflow-first pagination** (axis: overflow-strategy). endpoint เดียวกับ A แต่ paginate ตาราง: `ROWS_PER_SLICE = floor(avail_h / ROW_H)`; ถ้าเกิน → หน้าย่อยเพิ่ม (image ซ้ำ + header "ต่อจากหน้าก่อน"). forbidden_touch: NO.
- **E — Fixed split 60/40, font-scale table to fit** (axis: layout-engine). ไม่เพิ่มหน้า: `ROW_H = min(14, avail_h/row_count)`, `fontsize = clamp(ROW_H*0.65, 5, 10)`, ถ้า < 5pt → truncation row. forbidden_touch: NO. dep: none.

## Score (v1)

| approach | novelty | accuracy | UX | model-fit | boundary | cost | total |
|---|---|---|---|---|---|---|---|
| A backend split-canvas | 3 | 5 | 4 | 5 | 5 | 4 | 26 |
| B client HTML+print-CSS | 3 | 3 | 4 | 4 | 5 | 5 | 24 |
| C hybrid server-pix+client-html | 2 | 4 | 3 | 3 | 5 | 2 | 19 |
| D overflow pagination | 4 | 5 | 3 | 5 | 5 | 3 | 25 |
| **E font-scale to fit** | 3 | 5 | 5 | 5 | 5 | 5 | **28** |

Key: B accuracy=3 เพราะ canvas toDataURL ที่ RS=1.5 มัวบน print จริง. E UX=5 เพราะ "1 plan page = 1 report page" predictable. D accuracy=5 (full font เสมอ) แต่ UX=3 (หลาย PDF page ต่อ 1 หน้าแปลน สับสน).

## Recommendation (v1)

**Spike E (font-scale to fit) ก่อน** — UX สูงสุด, cost ต่ำสุดเท่า B แต่ accuracy สูงกว่า (PDF vector text ไม่มัว), implementation = A + ROW_H clamp, ไม่มี dep ใหม่.
**Fallback: D (overflow pagination)** ถ้า E พบว่า ≥15 แถว fontsize ต่ำกว่า 5pt จนอ่านไม่ออก.
อย่าใช้ B เป็นตัวหลัก — print resolution มัว.

**Phase 5 boundary check:** top (E) `forbidden_surface_touch: NO`, ไม่ข้าม Phase 1. ไม่ต้อง re-rank.

## Spike (v1)

**Scope:** ความเสี่ยงจริงตาม research = **layout geometry** (split ratio, font-scale-to-fit clamp, image aspect-fit, grouped table+subtotal, multi-page). Render primitives (`insert_image`/`draw_rect`/`insert_text`) เป็น PRIOR_ART พิสูจน์ใน `/export-pdf-overlay` แล้ว → spike ไม่ต้องพิสูจน์ซ้ำ. Spike จึง prototype **layout engine ของ approach E** บน `<canvas>` (จำลองหน้า landscape A4 842×595pt) — ตรวจว่า geometry/clamp logic ทำงานก่อนยกไป PyMuPDF.

**Sandbox:** `proto/sandbox/invent-lite-pdf-report-split.html` (เปิดตรงในเบราว์เซอร์ ไม่ต้อง server). มี: 3 หน้าตัวอย่าง (ชั้น1/ชั้น2/site), slider stress-rows 3–40, toggle overlay, รายงานผล criteria สดบนหน้า.

**Approach attempted:** E (font-scale to fit). **Outcome: PASS (6/6 criteria + 1 refinement noted).**

ผลทดสอบ layout math (PT_H 595, header 58, footer 26 → bodyH 511, availH 505):

| case | dataLines | ROW_H | font | trunc | used(pt) | fit? |
|---|---|---|---|---|---|---|
| page1 (5 obj,3 grp) | 13 | 14 | 9.1 | F | 200 | ✅ |
| page2 (8 obj,3 grp) | 16 | 14 | 9.1 | F | 242 | ✅ |
| page3 site (7 obj,4 grp) | 17 | 14 | 9.1 | F | 259 | ✅ |
| **stress 15 (เกณฑ์ข้อ 4)** | 23 | 14 | **9.1** | F | 340 | ✅ |
| stress 25,3grp | 33 | 14 | 9.1 | F | 480 | ✅ |
| stress 40,3grp | 48 | 10.5 | 6.84 | F | 519 | ⚠️ overflow |
| stress 60,3grp | 68 | 7.4 | 5 | F | 515 | overflow → fallback D |
| extreme 100,4grp | 110 | 4.6 | 5 | T | — | fallback D |

**ผล vs success criteria:**
1. ภาพ aspect-fit ไม่บิด/ไม่ล้น — **PASS** (letterbox fit `dw≤leftW, dh≤bodyH`)
2. overlay polygon+label map เข้าในภาพ — **PASS** (normalized pts ∈ [0,1] → map เข้ากรอบ fitted image เสมอ)
3. ตาราง group ตาม semanticTag + subtotal + รวมสุทธิ (deduction ติดลบ) — **PASS** (รวมสุทธิตรงสูตร XLSX summary)
4. ครบหน้าเดียว ≥15 แถว font อ่านออก (≥5pt) — **PASS** ที่ 15 แถว font 9.1pt; ครอบคลุมถึง ~25 แถวสบาย
5. หลายหน้า → หลาย report page — **PASS** (วน PAGES, แต่ละหน้าเป็น report page เดี่ยว)

**Refinement สำหรับ implementation จริง (พบจาก spike):**
- `availH` ที่ใช้ clamp ต้อง**หัก spacing overhead** (group-gap×0.1 + subtotal×0.1 ต่อกลุ่ม + title×0.4 + grand×0.3) ก่อน ไม่งั้นตาราง overflow ตั้งแต่ ~38 แถว ทั้งที่ font ยัง 6.8pt. แก้ 1 บรรทัด: `availH_eff = availH - overhead*ROW_H` แล้ว recompute (หรือ pad dataLines += ceil(overhead)).
- Threshold fallback D ที่แท้จริง: font < 5pt เกิดที่ ~60 แถว/หน้า, truncate ที่ ~100 แถว — ไม่สมจริงสำหรับ floor plan เดียว ⇒ E ครอบคลุม use-case จริงทั้งหมด, D เป็น safety net เท่านั้น.

---

## Diverge (v2)

5 approaches (editable web report, แยกหน้า, print):

- **A — sessionStorage + new-window contenteditable** (axis: edit-model). `window.open("lite-report.html")` + payload ผ่าน sessionStorage; ซ้าย `<img>` (read-only), ขวา `<table>` ที่ชื่อแถว/note/หัวกระดาษเป็น `contenteditable`, ตัวเลขพื้นที่ read-only; `window.print()` + `@media print @page landscape`. forbidden: NO, dep: none.
- **B — postMessage bridge + new window** (axis: data-handoff). เหมือน A แต่ handoff ผ่าน postMessage handshake → ส่ง Blob URL ภาพ original resolution (ไม่มัว, ไม่ติด sessionStorage 5MB). forbidden: NO. ข้อเสีย: async handshake + popup-blocker.
- **C — serialize-to-URL (base64) + self-load** (axis: editor-location+handoff). payload เล็กใส่ `?d=<b64>`, ดึงภาพจาก `GET /page/{n}` (server ต้องรัน). ขัด standalone (criterion 5) ถ้า server ปิด; URL จำกัด ~10 obj/หน้า. forbidden: NO.
- **D — form-field inputs + localStorage draft** (axis: edit-model+persistence). `<input>/<textarea>` แทน contenteditable; draft persist ใน localStorage ข้าม session. print CSS ซ่อน border. ไม่ WYSIWYG 100%. forbidden: NO.
- **E — structured template slots + sidebar form** (axis: interaction-model). named slots (project/floor/prepared-by/date/note) bind จาก sidebar form; ชื่อแถว read-only. ไม่ WYSIWYG (ต้องเดินไป-มา form↔preview). forbidden: NO.

(หมายเหตุ: inventor เสนอ "hidden print iframe" ตอนแรกแต่ตัดเองเพราะขัด constraint editability + no-bloat — แทนด้วย template-slots)

## Score (v2)

| approach | novelty | accuracy | UX | model-fit | boundary | cost | total |
|---|---|---|---|---|---|---|---|
| **A sessionStorage+contenteditable** | 3 | 4 | 5 | 5 | 5 | 5 | **27** |
| B postMessage bridge | 3 | 5 | 5 | 5 | 5 | 3 | 26 |
| C serialize-to-URL | 4 | 3 | 4 | 4 | 5 | 4 | 24 |
| D form-field+localStorage draft | 3 | 4 | 4 | 4 | 5 | 4 | 24 |
| E template slots+sidebar | 4 | 4 | 3 | 4 | 5 | 4 | 24 |

Key: A UX=5 (contenteditable = Word/Docs model), accuracy=4 (dataURL RS=1.5 ≈144DPI มัวกว่า vector เล็กน้อย), cost=5 (native ทั้งหมด ~150 บรรทัด). B accuracy=5 (Blob URL original res) แต่ cost=3 (async handshake + popup-blocker). C ขัด standalone (criterion 5).

## Recommendation (v2)

**Spike A ก่อน** — สูงสุด 27, cost ต่ำสุด, ไม่มี lib, standalone ครบ (โหลด sample เมื่อไม่มี payload), WYSIWYG สูงสุด.
**Fallback: B (postMessage + Blob URL)** ถ้า A พบ sessionStorage 5MB quota ตัน (PDF render RS=1.5 หลายหน้า dataURL ~400-600KB/หน้า → ~8 หน้าเกิน quota) — B เปลี่ยนแค่ handoff layer ไม่ต้องเขียนใหม่.
**Phase 5 boundary check:** top (A) `forbidden_surface_touch: NO`, boundary=5, ไม่ข้าม Phase 1. ไม่ต้อง re-rank.

## Spike (v2)

**Scope:** ความเสี่ยงจริงของ v2 = **editable-then-print web page ที่แยกหน้า ไม่บวม + WYSIWYG print**. Spike เป็น `lite-report.html` standalone จริง (criterion 5): โหลด sample data เอง, contenteditable header/row-name/note, area read-only (lock), `@media print @page landscape` + page-break ต่อหน้า.

**Sandbox:** `proto/sandbox/invent-lite-pdf-report-split-v2.html`

**Approach attempted:** A (sessionStorage + new-window contenteditable). **Outcome: PASS.**

- JS syntax: `JS_SYNTAX_OK` (node vm.Script).
- ผล vs success criteria v2:
  1. **PASS** — `lite-report.html` เป็นไฟล์แยก; รับ payload จาก `sessionStorage["bmaReportPayload"]` ถ้ามี (handoff), ไม่มี → โหลด SAMPLE เอง. ไม่ผูก DOM canvas.
  2. **PASS** — ต่อหน้า: ซ้าย `<img>` (แปลน, ที่นี่ใช้ synthetic SVG แทน render หน้า PDF), ขวา `<table>` group ตาม semanticTag + subtotal + รวมสุทธิ, หัวกระดาษ project/หน้า/สเกล/วันที่.
  3. **PASS** — `contenteditable` บน title/page-title/date/preparedBy/ชื่อแถว/note/footer; `td.area` **read-only** (ไม่มี contenteditable + lock style + tooltip "ค่าจากการวัด แก้ไม่ได้") → รักษาสัญญา raw-geometry.
  4. **PASS** — `@page{size:A4 landscape}` + `@media print{.sheet{page-break-after:always}}` + ซ่อน toolbar/affordance ตอนพิมพ์ → WYSIWYG, 1 แปลน = 1 หน้า. (ผล print จริงให้ user ยืนยันด้วยการเปิด+Ctrl+P)
  5. **PASS** — standalone: เปิดไฟล์ตรงในเบราว์เซอร์ทำงานได้ด้วย SAMPLE โดยไม่ต้องมี canvas/engine/server → พิสูจน์ "คนละโมเดล ไม่บวม".
- logic check: หน้า1 รวมสุทธิ = 87.60 ม² (หัก deduction 6.10), หน้า2 site = 672.60 ม² — ตรงสูตร group-by-semanticTag (deduction sign −1).

**Residual risk (ต้องจัดการตอน implement จริง):**
- **sessionStorage 5MB quota** เมื่อ image เป็น real dataURL จาก `get_pixmap` RS=1.5 (~400-600KB/หน้า → ~8 หน้าตัน). ⇒ ถ้าเจอจริง switch handoff layer ไป **fallback B (postMessage + Blob URL / `/page/{n}` fetch)** โดยไม่ต้องเขียนหน้าใหม่.
- ฟอนต์ไทยตอน print ขึ้นกับ font ที่เครื่องผู้ใช้มี — implementation จริงควร embed/bundle Sarabun หรือใช้ font ระบบที่การันตี.
- หน้าที่ object เยอะมาก: ตาราง HTML จะ flow ข้ามหน้าเอง (browser pagination) — ต้องตัดสินใจว่ายอมให้ table ต่อหน้า หรือ scale (ต่างจาก v1 ที่ต้อง font-scale เอง; ฝั่ง HTML ถูกกว่าเพราะ browser จัด pagination ให้).

## Decision

**GO** — 2026-05-21, human checkpoint (รอบ v2). user เห็น Chromium screenshots แล้วอนุมัติ.

- **Chosen:** Approach A-v2 — `lite/lite-report.html` แยกไฟล์, รับ payload ผ่าน `sessionStorage`, `contenteditable` (header/row-name/note) + area read-only, browser print → PDF (`@page A4 landscape` + page-break).
- **Promoted to:** `INV-2026-05-21-002` / **LITE-REPORT** ใน `docs/status/PHASE_INDEX.md` Discovered backlog (status `queued`, ready for `/bma-dev-loop`).
- **Fallback ถ้า sessionStorage 5MB ตัน:** Approach B (postMessage + Blob URL) — เปลี่ยนแค่ handoff layer.
- **History:** v1 (backend PyMuPDF, approach E) spike PASS แต่ user RESHAPE ที่ checkpoint เพราะต้องการ editability + แยกหน้า → v2. v1 sections เก็บไว้ใต้ `## v1 attempt (superseded)`.
- **Status flips:** IDEAS.md → `invent-done-go (→ INV-2026-05-21-002)`.

## Decision
_(stub — phase 7, human GO/NOGO/RESHAPE)_
