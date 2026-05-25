# Invent — Pages Overview UI (lite)

- **Started**: 2026-05-23
- **Idea**: Pages Overview UI for lite — bulk tag/floor + report preview in one view (replaces single-page `setupModal` friction)
- **Sandbox (3 spikes)**:
  - `lite/sandbox/invent-pages-overview-H-wizard.html`  (373 lines)
  - `lite/sandbox/invent-pages-overview-C-splitpane.html` (328 lines)
  - `lite/sandbox/invent-pages-overview-E-palette.html`  (325 lines)
- **Trigger**: ผู้ใช้ขอเข้า `/lite-invent` หลังจาก prior spike `lite/sandbox/invent-45page-permit-spike.html` (กรณี 45-page permit, 9/45 หน้าวัด) — สั่งเฉพาะ: 10 approaches + spike top 3
- **Status**: CHECKPOINT — รอผู้ใช้ตัดสิน GO / NOGO / RESHAPE

## Phase 2 — RESEARCH (verdict `PRIOR_ART_PARTIAL`)

Delegated to `bma-researcher` (haiku). Key findings:

- **Proto มี pattern แล้ว** — `proto/ui.html:3071-3081` `pgmgr` + `pgmgrSel/SelectAll/ClearAll` (multi-select bulk-op) + "Pages" tab + "Sheets/Disciplines" tab. lite สามารถ port idiom ได้ แต่ต้อง reimplement ในรูปสลิมกว่า
- **ไม่มี lib ที่ fit** — Tabulator (220KB) viable แต่หนัก, Handsontable license blocker, AG Grid 700KB เกิน cap. SortableJS (40KB) OK แต่ lite มี pointer-events DnD ของตัวเองใน `layer-dnd.js` แล้ว. pdf.js render thumbnail 45 หน้า → ติด proto malloc anti-pattern (CLAUDE.md #9)
- **Incumbents อ่อนทั้งหมด** — Bluebeam/Foxit/AutoCAD SSM ไม่มี bulk page classification ที่ดี, PlanGrid ใช้ OCR auto-tag → lite มีโอกาส innovate
- **5 UX axes viable**: modal-form / multi-card / tabular / kanban / wizard
- **Verdict**: PARTIAL → diverge

## Phase 3 — FRAME

**Problem**: tag 45 PDF pages ใน lite วันนี้ต้องเปิด `setupModal` (Ctrl+,) ทีละหน้า. ใน permit 9/45 หน้าวัด อีก 36 หน้าต้อง tag เพื่อ report exclusion → friction หนัก

**Success criteria**:
- tag 45 หน้า ≤ 2 นาที (≤ 2.7s/page)
- bulk select + bulk floor sequential (p11..16 → 1,2,3,4,5,roof)
- report preview เห็นในจอเดียวกัน (อย่างน้อย: measured/excluded counts + GFA sum mock)
- proto cross-open parity คงเดิม (`pageTags`/`pageFloorKind`/`pageFloorNum`/`pageNames` ไม่เปลี่ยน format)

**Forbidden**: `measure-engine.js`, `RS`, `pdfToC`/`cToPdf`, area math, `semanticTag` resolution, `.bmaplan` field rename
**Size cap**: `ui-lite.html` 1139/1200 (เหลือ 61) → bulk logic ลง `static/js/pages-overview.js` ใหม่
**Out-of-scope**: OCR auto-classifier (LSP-3), GFA-by-floor aggregator ใน LRV (LRR-1), report traceability section (LRP-1)

## Phase 4 — DIVERGE (10 approaches)

Delegated to `bma-inventor` (sonnet). 10 approaches across 6 axes:

| # | Name | Axis | Sketch (1 line) |
|---|------|------|-----------------|
| A | Inline table replace `#ov-grid` | UX | table 8 col + checkbox + top bulk bar |
| B | Kanban board grouped by tag | representation | column per tag, drag card → set tag |
| C | Split-pane gallery + form | data-model | left thumb grid + right batch form (Lightroom-style) |
| D | Accordion timeline by discipline | integration | `<details>` per discipline + horizontal scroll within band |
| E | Palette over existing `#ov` | UX modal-less | extend `openOv()` ด้วย multi-select toggle + bottom action bar |
| F | Three-panel workspace | UX workspace | thumbs / form / report 3 columns 25/50/25 |
| G | Virtual-scroll spreadsheet | algorithm | 44px row × all cols + virtual DOM (สำหรับ 200+ pages) |
| H | Two-pass wizard | UX flow | Step 1 classify → Step 2 number floors → Step 3 review |
| I | Persistent side-drawer | integration | non-modal 320px drawer slides from right (canvas ยังเห็น) |
| J | Radial quick-tagger | algorithm | long-press / right-click → 8-sector radial picker |

## Phase 5 — SCORE (6-dim, scale 1-5)

| approach | novelty | accuracy | UX | model-fit | boundary | cost | **total** |
|----------|---------|----------|----|-----------|----------|------|-----------|
| A inline table             | 2 | 5 | 4 | 5 | 5 | 4 | **25** |
| B kanban board             | 4 | 5 | 4 | 4 | 5 | 2 | **24** |
| C split-pane gallery+form  | 3 | 5 | 5 | 5 | 5 | 3 | **26** |
| D accordion timeline       | 3 | 5 | 3 | 4 | 5 | 3 | **23** |
| E palette over existing ov | 3 | 5 | 3 | 5 | 5 | 5 | **26** |
| F three-panel workspace    | 3 | 5 | 5 | 4 | 5 | 2 | **24** |
| G virtual-scroll spreadsht | 2 | 5 | 3 | 5 | 5 | 3 | **23** |
| **H two-pass wizard**      | 4 | 5 | 5 | 5 | 5 | 3 | **27** |
| I persistent side-drawer   | 4 | 5 | 5 | 4 | 5 | 2 | **25** |
| J radial quick-tagger      | 5 | 5 | 3 | 5 | 5 | 3 | **26** |

**Top 3 (ตามคำสั่งผู้ใช้)**: **H (27) · C (26) · E (26)** — เลือก E แทน J เพราะ cost ต่ำสุด (5) และ J มี discoverability risk (radial 2-level)

## Phase 6 — SPIKE (top 3 ทั้งหมด)

### Spike H — Two-pass wizard (`invent-pages-overview-H-wizard.html`)

3 steps แบบ force-order:
1. **Classify** — 45 card grid, คลิก = cycle tag, กด `1-9` = set tag ที่ focus, `→/←` เลื่อน focus, progress bar `N/45 tagged`
2. **Number Floors** — แสดงเฉพาะ `tag=floor`, drag-reorder, ปุ่ม "Sequential 1→N (ปลายสุด=roof)"
3. **Review** — รายงาน A4: site coverage / GFA breakdown / FAR/OSR/Coverage / traceability list

จุดเด่น: force order = ไม่มีโอกาสลืม step. self-documenting (first-time users ไม่ต้องเดาว่าทำอะไรต่อ)
จุดอ่อน: rigid sequencing — back/forward เยอะถ้าผู้ใช้อยากแก้ฟรี

### Spike C — Split-pane gallery + form (`invent-pages-overview-C-splitpane.html`)

Layout 60/40:
- **ซ้าย** (gallery) — 45 thumb grid + search box + select-all/by-tag/clear, multi-select via click/Shift/Cmd
- **ขวา** (form) — adaptive ตามจำนวนเลือก:
  - 0 = facts panel (ที่ดิน 1919.20, อาคารปกคลุม 839.10, FAR allowed 10, OSR 3%)
  - 1 = single-page form (tag + floor kind + floor num + name + exclude)
  - N = bulk form (dropdown มี `⟨ คงเดิม ⟩`, sequential checkbox, 3-state exclude)
- **ล่างขวา** — pill summary 4 ตัว (measured/excluded/floors/GFA mock)

จุดเด่น: pattern Lightroom/macOS Preview ที่ผู้ใช้คุ้น. แก้ free-form (ไม่ใช่ wizard). 3-state checkbox มี option "คงเดิม" สำหรับ bulk → ป้องกัน accident
จุดอ่อน: split-pane 40% ของจอ อาจแคบ บน laptop เล็ก

### Spike E — Palette over existing `#ov` (`invent-pages-overview-E-palette.html`)

ขยาย `#ov` เดิม ไม่ทดแทน:
- ปุ่ม `✓ Multi-select` บน header → เข้าโหมด multi
- โหมด multi เปิด: bottom action bar slide-up (`Set tag ▼ Apply` · `Floor seq 1→N` · `Toggle excluded` · `Auto-classify`)
- โหมด single (default): single-click = เปิดหน้า (เหมือนเดิม)
- toast notification ตอบทุก action
- Σ summary bar ด้านล่างไม่เปลี่ยน — แสดง measured/excluded/floors/GFA mock เหมือนใน lite วันนี้

จุดเด่น: cost ต่ำสุด (3 step delta จากของเดิม), ไม่ฉีก DOM/UX ที่ผู้ใช้คุ้น. มี Auto-classify ใน palette (Thai-keyword heuristic ≈ 12 บรรทัด — เผื่อ tease feature LSP-3)
จุดอ่อน: ไม่มี report preview inline แยก (อยู่ใน Σ overlay เดิม) — partially fails frame criterion "report preview เห็นในจอเดียวกัน"

## Phase 7 — CHECKPOINT

หยุดรอผู้ใช้ตัดสิน. ตัวเลือก:

1. **GO H** (wizard) — เริ่ม sprint card `LITE-LPO-H` ผ่าน `/bma-lite-dev`; build `static/js/pages-overview.js` + glue ≤30 lines ใน `ui-lite.html`. risk: ต้องเขียน wizard state machine + UI ใหม่ทั้งหมด (~220 lines)
2. **GO C** (split-pane) — sprint card `LITE-LPO-C`; ใช้ pattern Lightroom. risk: split layout + 3-state form (~200 lines)
3. **GO E** (palette) — sprint card `LITE-LPO-E`; แค่ขยาย `openOv()` ที่มีอยู่. risk ต่ำสุด (~120 lines)
4. **HYBRID** — เริ่ม E (palette) ก่อน เพื่อ ship bulk-tag ใน 1 slice เล็ก ๆ → ถ้ายังต้องการ flow แบบ wizard ค่อยทำ H เป็น slice 2 ทับ
5. **NOGO** — ปัจจุบัน `setupModal` ทีละหน้าก็พอ
6. **RESHAPE** — เปลี่ยน frame (เช่น ลด/เพิ่ม success criterion) แล้ววน Phase 4 ใหม่

แนะนำ (Opus): **#4 HYBRID** — ship E ก่อน เพราะ:
- cost ต่ำสุด (5/5) — slice เดียวจบ
- ไม่ขัดของเดิม (ขยาย ไม่ทดแทน) — proto cross-open parity เห็นชัดว่าคงเดิม
- ผู้ใช้ได้ลอง bulk-tag กับ permit จริงแล้ว ค่อยตัดสินว่าต้องการ wizard (H) เพิ่มไหม
- H ทำทับได้ภายหลัง เพราะ data layer เดียวกัน

ถ้าผู้ใช้ตัดสิน GO ตัวใด — สร้าง sprint card ใน `PHASE_INDEX.md` status `invent-done-go` พร้อม note ว่า build ผ่าน `/bma-lite-dev`. ถ้า NOGO/RESHAPE — เก็บ doc นี้ไว้, ไม่แก้ PHASE_INDEX

## Notes (จากการสร้าง spike)

- ทั้ง 3 spike ใช้ dataset 45-page เดียวกัน (manual classification จาก spike แรก) — เปิดเทียบได้
- ไม่มี spike ใดแตะ measure-engine.js / RS / pdfToC / area math (forbidden surface 0)
- size estimate ที่ inventor ให้ (H~220, C~200, E~120 lines) สอดคล้องกับ spike (H 373, C 328, E 325 รวม CSS+demo data) — ใน production จะลด ~30% เพราะไม่ต้องฝัง 45-page data + CSS เยอะ ใช้ lite chrome แทน
- spike H มี `quickAuto` keyboard binding (`1-9`) เป็น preview ของ LSP-3 (auto-classifier) — ถ้า GO HYBRID อาจรวมเข้าใน palette ทันที
