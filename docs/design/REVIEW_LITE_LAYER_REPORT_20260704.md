# รีวิวระบบ Layer + Report ของ lite — เทียบกับคอนเซป "lite = เรียบง่าย"

Date: 2026-07-04
วิธีทำ: 4 review agents ขนาน — (1) โค้ด layer system, (2) โค้ด report system, (3) UX complexity inventory, (4) ประวัติการตัดสินใจใน docs/invent + lite/sandbox
สถานะ: read-only review — ยังไม่แก้โค้ดใด ๆ ข้อเสนอทั้งหมดรอ user ตัดสิน

---

## 0. บทสรุปผู้บริหาร

**แกนกลางดี ผิวใช้ยาก.** หลัง redesign B0-B5 (2026-07-03) แกนคำนวณของ lite อยู่ในสภาพดีที่สุดตั้งแต่เริ่มโปรเจกต์ — engine รวมตัวเดียว (`object-agg.js` tuple stream) + oracle คุม parity + orphan heal + undo ครบ แต่ **ความรู้สึก "ใช้ยาก" ของผู้ใช้เป็นเรื่องจริงและวัดได้**:

- ผู้ใช้ต้องรู้ **~18 concepts** (layer, role, folder, PF auto-folder, page tag, floorKind, floorKey, Σ/▸ refs, grid vs classic, CFSS master/instance, ...) ทั้งที่ use-case หลักคือ *"วาดให้ตกหมวด 6 หมวดต่อชั้น"*
- ยอดพื้นที่เดียวกันโชว์ **7 ที่** · ประตูส่งออก **5 ทาง** · ตั้ง tag หน้าได้ **3 ประตู** · ชั้นซ้อน **4 ระดับ** (role → layer → user folder → PF folder) + แกนชั้น **2 แหล่งความจริง** (page tag vs layer.floorKey)
- ประวัติ invent ชี้ pattern ชัด: **ทุก GO เพิ่ม concept 1-3 ตัว, ไม่เคยมีการตัดสินใจไหน "ถอด" concept ออกเลย** และจุดเบี่ยงหลักคือ human checkpoint เลือกทาง rich ทับทางเรียบง่ายซ้ำ ๆ (เช่น editable report เลือก Approach D คะแนน 21 ทับ A คะแนน 27)
- แถมพบ **bug ตัวเลขจริง 2 ตัว (HIGH)** ที่กระทบเอกสารส่งลูกค้า — ต้องแก้ก่อนพูดเรื่อง UX

**ทิศทางที่เสนอ:** แก้ bug ตัวเลข → ยุบผิว UI ให้เหลือ "1 ทางต่อ 1 งาน" → ตั้ง counter-force เชิง concept ใน invent loop (แบบเดียวกับ 5,000-line trigger ของ proto แต่เป็นระดับ concept)

---

## 1. Bug ตัวเลขที่ต้องแก้ก่อน (กระทบความถูกต้องของเอกสาร)

| # | ปัญหา | หลักฐาน | ระดับ |
|---|---|---|---|
| B-1 | **sign ของ deduction อ่านจาก `layer.id` ไม่ใช่ `role`** — `var sign=(c.id==="ded")?-1:1` → เลเยอร์หักที่ user สร้างเอง (id `L5`, role `ded`) ถูก **บวก** เข้า net ทั้ง classic report และ payload ที่ไหลไป grid ผิดหมด (invariant "คำนวณจาก role เท่านั้น" โดนละเมิดในรูปอ่าน id — สายพันธุ์เดียวกับอ่าน name) | `export-annotate.js:78` | **HIGH** |
| B-2 | **Grid (view default) แสดงเฉพาะหน้าแรก** — `gridRows()` flatten แค่ `payload.pages[0]` โปรเจกต์หลายหน้าข้อมูลหายเงียบ ไม่มีคำเตือน | `lite-report.html:264-277` | **HIGH** |
| B-3 | **Grid ไม่รู้เครื่องหมายลบ** — แถวหักถูกบวกเมื่อ user ทำ subtotal (known gap จาก ship `16698bb` ยืนยันแล้วว่ายังเปิด) | `lite-report.html:272-274`, `report-edit.js:181` | HIGH (known) |
| B-4 | **แตะ editor ตัวแปรครั้งเดียว → หลุด `useLive`** — closure ทุกตัวที่ re-render (operand/lit/op/+ขั้น/−/✕/+ตัวแปร) เรียก `renderReportVarsEditor(h, ag)` โดยไม่ส่ง opts ต่อ → ค่า role สลับจาก tuple semantics (ตัด excluded) เป็น legacy (รวม excluded) ต่อหน้า user | `report-vars.js:411,424,495,507,517,544,557` | **HIGH** |
| B-5 | **`activeCat` ค้างชี้ layer ที่ตายแล้ว → ผลิต orphan catId ใหม่** — undo restore LAYERS (`ui-lite.html:867-871`) และ `_pflPrunePF` (`page-folder-layers.js:313-330`) ไม่ validate `activeCat`; `mkObj` เขียน catId ผี; `aggTuples` ทิ้ง tuple role=null เงียบ ๆ (`object-agg.js:180-189`) → พื้นที่หายจากยอดรวมจนกว่าจะ reload | `ui-lite.html:533-534,867` | MED-HIGH |
| B-6 | **excluded-page มี 2 มาตรฐานใน modal เดียว + export** — ตารางหมวดใน Σ สรุป (computeSummary) *รวม* หน้า excluded แต่ per-floor/ตัวแปร (tuples) *ตัด*; XLSX (`buildExportData`) รวม แต่ report payload กรอง → ยอด XLSX ≠ ยอดรายงาน | `ui-lite.html:1063-1091`, `export-annotate.js:11 vs :55`, decision note `object-agg.js:35-45` | MED |
| B-7 | `_rvSeq` ไม่ restore หลัง load → id ตัวแปรชนกัน (`v_1` ซ้ำ) | `report-vars.js:267-273` | MED |
| B-8 | ย้าย object ข้าม layer ไม่กรอง counting-compatibility (poly ย้ายไป layer นับจำนวนได้ → หายจากตาราง) | `layer-move.js:17-21` | MED |
| B-9 | `buildPageStore` จำแนก opening/land ด้วย id default layer เท่านั้น — custom ded layer ถูกบันทึกเป็น room | `ui-lite.html:951-953` | MED |
| B-10 | localStorage grid edits: hash = `name\|area` join → collision ข้ามโปรเจกต์ / วัดเพิ่ม 1 object edits เก่าหายเงียบ / orphan keys ไม่มี GC | `report-edit.js:162-175` | MED |
| B-11 | jspreadsheet context-menu insert/delete row ไม่ผ่าน mapper → `rowIds`/baseline desync | `report-edit.js:197` | MED |
| B-12 | DnD ซ้อน PF folder ใน PF folder ได้ + ลาก layer ข้ามชั้นแล้ว floorKey ไม่ตาม → Σ tree ไม่ตรง Summary เงียบ ๆ (`detectDivergence` จับไม่ได้) | `layer-dnd.js:441-448`, `object-agg.js:323-345` | MED |

LOW (เก็บเป็น batch): แถว "+ เพิ่ม layer ใน PF" ไม่มี pushUndo + fix role=gfa + ไม่ปัก floorKey (`page-folder-layers.js:680-695`) · load ไฟล์เก่าไม่ล้าง LAYERS (`ui-lite.html:999`) · dead code `togglePageFolderMode` (`page-folder-layers.js:705-757`) · Σ count ใต้ useLive = 0 · double-escape ชื่อ var (`lite-report.html:217`) · MutationObserver ไม่ disconnect (`report-edit.js:312-314`) · classic contenteditable edits ไม่ persist · `_lpFirstPageOfLayer` ไม่ผ่าน `rollupCatId` (`layer-panel.js:161`)

---

## 2. ทำไมถึงรู้สึกใช้ยาก — หลักฐานเชิง UX

### 2.1 ตัวเลขภาระผู้ใช้

| มิติ | ค่าที่วัดได้ | ควรเป็น (คอนเซป lite) |
|---|---|---|
| Concepts ที่ leak ถึง UI | ~18 | ≤ 8 |
| จุดแสดงยอดพื้นที่ | 7 | 2-3 (canvas label + สรุปเดียว + รายงาน) |
| ประตูสู่ report/export | 5 (บางปุ่มป้ายผิด — "📄 ส่งออก PDF" ใน wizard เปิด HTML) | 1-2 |
| ประตูตั้ง tag/ชั้นของหน้า | 3 (Page Setup / wizard / หัว Σ สรุป) | 1 |
| ทางเพิ่ม layer | 2 — พฤติกรรม**ไม่เท่ากัน** (modal เลือก role ครบ vs prompt fix role=gfa) | 1 |
| ชั้นซ้อนใน panel | 4 ระดับ (role → layer → user folder → PF folder) | 2 |
| แหล่งความจริงของ "ชั้น" | 2 (page tag vs layer.floorKey) + banner ให้ user reconcile เอง | 1 |

### 2.2 กับดักใหญ่ 5 อัน (เรียงตามความเจ็บ)

1. **รายงาน 2 โหมดที่แก้แล้วพิมพ์ไม่ตรงกัน** — grid เป็น default แก้ได้ทุกอย่าง แต่ `@media print` บังคับ classic เสมอ (`lite-report.html:70-73`) → **สิ่งที่แก้ใน grid ไม่ออกไปกับ PDF** ส่วน classic เลขล็อกแก้ไม่ได้ + การแก้ grid หายเงียบเมื่อวัดเพิ่ม (hash key เปลี่ยน) — งานเดียว "แก้แล้วพิมพ์" ถูกผ่าเป็นสองโลกที่ไม่ sync
2. **floorKey ที่ user ไม่เคยตั้ง แต่ถูกบังคับตัดสินใจ** — ระบบ seed floorKey เอง (`page-folder-layers.js:241`) แล้ววันหนึ่ง banner เด้ง "เลเยอร์ปักไว้ชั้น A แต่หน้านี้แท็กชั้น B [ตามเลเยอร์][ตามหน้า]" — ผู้ใช้ถูกถามเรื่องกลไกที่ตัวเองไม่เคยสั่ง
3. **Jargon ภายในหลุดถึงเอกสารลูกค้า** — PDF overlay ใช้ semanticTag ดิบเป็น label: ลูกค้าได้ PDF เขียน `gross_floor_area 58.40 m2` (`export-annotate.js:36`); UI มี "polyAreaM2 (vendored)" (`ui-lite.html:1089`), `PF_floor_2` ดิบในตาราง Review (`overview-setup.js:844`), role id monospace `gfa · counting` ใน modal (`layer-panel.js:77`)
4. **คลิกเลือก layer แล้วโดนวาร์ปหน้า** — side-effect เชิง navigation ที่ไม่ได้ขอ ใน action พื้นฐานที่สุดของระบบ (`layer-tree.js:487-492`)
5. **Wizard hard-lock ทั้งจอ** — ทุก event นอก panel โดน `stopImmediatePropagation` (`wiz-auto.js:54-79`) ต้องผ่าน 3 step + floorKind + เลขชั้นทุกหน้าก่อนจับเครื่องมือใด ๆ แม้อยากวัดหน้าเดียว (นโยบาย hard gating ถูกต้องตามที่ user เคยยืนยัน — แต่ scope ที่ lock กว้างเกินงาน)

### 2.3 ฟีเจอร์ที่ค้นพบไม่ได้

Shift+↑↓/→/← จัด tree (ไม่อยู่ใน cheatsheet — cheatsheet ไม่มีหมวด layer เลย) · คลิกชื่อ layer = rename, คลิก swatch = เปลี่ยนสี (ไม่มี affordance) · checkbox "จับกลุ่มเมื่อชนกัน" ไม่มีคำอธิบาย · Ctrl+E ทำงานทั้งที่รายการเมนู XLSX ถูกซ่อน (`menu-flyout.js:237-238`) · กติกา var อ้างได้เฉพาะตัวก่อนหน้า รู้ได้จาก dropdown ที่หายไปเท่านั้น

### 2.4 ศัพท์ไม่ตรงกันระหว่างหน้าจอ

floorKind: Page Setup มี `custom` ไม่มี `mezzanine` (`ui-lite.html:245`) / wizard มี `mezzanine` ไม่มี `custom` (`overview-setup.js:356-360`) → ชั้นลอยที่ตั้งจาก wizard แก้ต่อใน Page Setup ไม่ได้ · page tag: wizard เป็นอังกฤษล้วน / Page Setup เป็นไทย

---

## 3. ประวัติ: ความซับซ้อนสะสมมาอย่างไร (จาก sandbox + docs/invent)

### 3.1 เส้นทาง 6 สัปดาห์ของ layer panel

```
flat 6-role (05-22) → tree+folder+Σ (LST, hybrid F ที่ไม่ได้ score)
→ DnD+auto-group (LDND — inventor สั่ง defer D, user เอาเลย)
→ PF page-folder + auto-seed (LPFL)
→ floor kinds + composite ID (LFOC — เกิดเพื่ออุด data-loss bug ของ LPFL+LFLOOR ชนกันเอง)
→ CFSS master/instance
→ floorKey pin + chip + tint + banner (07-03 — doc เรียก page-folder tree ว่า "already a fragile system" แล้ววางระบบใหม่ทับ)
```

### 3.2 ทางเรียบง่ายกว่าที่แพ้ (คัดเฉพาะตัวสำคัญ)

| รอบ | ตัวชนะ (ที่เลือก) | ตัวที่เรียบง่ายกว่าที่แพ้ | ใครตัดสิน |
|---|---|---|---|
| LST sublayer-tree | hybrid F (A+B, ไม่ได้ score) | **B group-1-ระดับ (26 — คะแนนสูงสุด, inventor แนะ)** | user RESHAPE |
| LDND | A+D (auto-group เป็น first-class) | C context-menu-only (cost 5/5) และ defer-D ตามที่ inventor เสนอ | user GO |
| Editable report | **D jspreadsheet (คะแนน 21 — เกือบต่ำสุด)** + RESHAPE 3 รอบ + vendor 444 KB | A contenteditable (27) / B override-overlay (26, eval-gate เลือก) | user RESHAPE "อยากได้เหมือน Excel" |
| CFSS | A metric-master (object kind ใหม่ → ตามมาด้วย summary bug, undo gap, special-case ใน B4/floorKey) | C eager-copy (25 เสมอกัน — "zero changes ต่อ draw/area/snap/export") | tie-break |
| layer-linkage 07-03 | B one-engine (25/30) — *อันนี้ trade ถูกทาง: ลดความซับซ้อนภายใน* | fallback D floorKey-on-object | GO (สมเหตุผล) |

### 3.3 Pattern ที่สรุปได้

1. **ไม่มีการตัดสินใจครั้งไหนถอด concept ออก** — การลบเกิดแค่ระดับ widget (ปุ่มลูกศร, skin v1) ไม่เคยระดับ concept
2. **จุดเบี่ยงหลักคือ human checkpoint ไม่ใช่ scoring** — ระบบ score 6 มิติทำงานดี แต่ RESHAPE ของมนุษย์เลือก rich ทับ simple เกือบทุกครั้ง
3. **ชั้นหลังเกิดเพื่ออุดรอยชั้นก่อน** — LFOC-ORDER ทั้งซีรีส์มีเหตุจาก bug ที่ PF folder + floor kind ชนกันเอง
4. **NOGO เกิดครั้งเดียว** (progressive-disclosure 05-24) — เหตุผลตอนนั้น ("maintenance surface จริง ต่อ benefit แคบ") เป็น template ที่ถูกต้อง แต่ไม่เคยถูกใช้ย้อนกลับกับ concept ที่ ship แล้ว
5. **เอกสาร invent ซื่อสัตย์เรื่อง cost ขึ้นเรื่อย ๆ** — ปัญหาไม่ใช่มองไม่เห็น cost แต่คือ**ไม่มี counter-force เชิง concept ใน loop** (proto มี 5,000-line trigger เป็น counter-force เชิงบรรทัด — lite ไม่มีอะไรเทียบเท่าในเชิง concept)

### 3.4 ซากที่ควรเคลียร์ (housekeeping sprint เดียว)

- `lite/sandbox/invent-lite-editable-report{,-d,-d2,-compare}.html` + eval คู่ — superseded (เก็บเฉพาะ `-d3` = behavior contract ของโค้ดที่ ship)
- `lt-v2` residue — toggle ถูกลบแล้ว (LSKIN-DROP) แต่ CSS ยัง scope `body.lt-v2` 16 จุด + `ui-lite.html:1175` ต้อง classList.add ถาวร → จบ S4 ที่ค้างครึ่งทาง (flag→base)
- `lite/sandbox/invent-lite-pdf-render-quality/` — invent สถานะ paused + artifacts untracked ค้าง (jpg/png 5 ไฟล์ + `v3-results/`) — ตัดสินใจ commit/ลบ
- `lite/tests/demo_cfss_rightclick_screenshot.py` — untracked demo ค้าง
- dead code: `togglePageFolderMode`/`_pflInjectToggleButton`, `layersOfPage` (API ไม่มี caller + latent bug)

---

## 4. ข้อเสนอ: ดึงกลับสู่คอนเซป lite

### Phase A — แก้ตัวเลขให้ถูก (ทำก่อน ไม่ต้องรอตัดสินใจเชิง UX)

1. `export-annotate.js:78` → `c.role==="ded"` + test custom-ded-layer (ปิด B-1) — sprint เล็ก 1 บรรทัด + guard
2. ส่ง `opts` เข้า closure ทุกจุดใน `report-vars.js` (ปิด B-4) — ~7 บรรทัด + test
3. Heal `activeCat`: validate ใน `_afterHistory` + หลังทุก `removeLayer` path, เรียก `sweepOrphanCatIds()` หลัง undo/redo (idempotent อยู่แล้ว) (ปิด B-5)
4. **ตัดสิน semantics เดียวของ excluded pages** แล้ว reroute `computeSummary` (ตารางหมวด) + `buildExportData` (XLSX) มาอ่าน tuple stream (ปิด B-6 + จบ B2-leftover) — ทุกยอดในแอปมาจาก engine เดียวจริง ๆ
5. เก็บ MED ที่เหลือ: `_rvSeq` restore (B-7), กรอง counting ใน move menu (B-8), `buildPageStore` role-based (B-9), ปิด context menu jspreadsheet (B-11), DnD guard PF (B-12)

### Phase B — ยุบผิว UI: "1 งาน = 1 ทาง" (ต้องการ user ตัดสินทีละข้อ)

| # | ข้อเสนอ | ผลต่อ concept count |
|---|---|---|
| S-1 | **รายงานเหลือโหมดเดียว** — เลือกทางใดทางหนึ่ง: (ก) ทำ grid ให้พิมพ์ได้จริง (item 9 print CSS + sign-aware + ทุกหน้า) แล้ว**เลิก classic**, หรือ (ข) ยก classic กลับเป็น default + ทำเลขแก้ได้แบบ override-overlay (Approach B เดิมที่ eval-gate เคยเลือก) แล้ว**เลิก grid + vendor 444 KB** | −2 (grid/classic + hash-localStorage) |
| S-2 | **ยุบแกนชั้นเหลือแหล่งเดียว** — floorKey ไม่ควรเป็นสิ่งที่ user ต้อง reconcile: ให้ folder membership = floorKey โดยกลไก (ลาก layer เข้า folder ชั้นไหน = ปักชั้นนั้น อัตโนมัติ) แล้วตัด banner [ตามเลเยอร์][ตามหน้า] ทิ้ง | −2 (floorKey + divergence banner) |
| S-3 | **ซ่อน PF jargon ทั้งหมด** — `PF_floor_N` / warning "ไม่มี folder PF_site" / "page-folder mode" ห้ามโผล่ใน UI text; แสดงเป็นชื่อชั้นภาษาไทยเสมอ | −1 |
| S-4 | **ตัด user folder (📁+)** — ทับซ้อนกับ PF folder; งานจัดกลุ่มที่เหลือให้ PF อย่างเดียว (ต้อง migrate: folder ที่มีอยู่ flatten) | −1 (ชั้นซ้อน 4→3) |
| S-5 | **ยอดพื้นที่เหลือ 3 ที่**: canvas label + Σ สรุป (เดียว, กติกา excluded เดียว) + รายงาน; ตัด Σ ท้าย PF folder ใน tree, ตาราง LRV ซ้ำใน wizard Review | −? (7→3) |
| S-6 | **ประตู export เหลือ 2**: File▸Export (รายงาน/XLSX/PDF overlay ในที่เดียว) + Ctrl+E; แก้ป้าย "📄 ส่งออก PDF" ใน wizard ที่จริง ๆ เปิด HTML; unhide รายการเมนูที่ Ctrl+E ชี้ | — |
| S-7 | **ตั้งค่าหน้าเหลือประตูเดียว** (Page Setup) — ตัด floorctl ในหัว Σ สรุป; ศัพท์ floorKind ชุดเดียวทั้ง wizard/Page Setup (เพิ่ม mezzanine ให้ Page Setup) | −1 |
| S-8 | **ตัด warp-on-layer-click** — คลิก layer = เลือก layer เฉย ๆ; ถ้าจะ warp ให้เป็นปุ่มแยก (🔍) | — |
| S-9 | **ทางเพิ่ม layer เหลือแบบเดียว** — แถว "+ เพิ่ม layer ใน..." ใช้ modal เดียวกับปุ่ม + (role ครบ, pushUndo, ปัก floorKey ตาม folder) | — |
| S-10 | **Wizard lock เฉพาะ panel ไม่ lock ทั้งแอป** + ปุ่ม "ข้ามไปวัดเลย (tag ทีหลัง)" ที่ tag หน้าปัจจุบันหน้าเดียวแล้วปล่อย (ยังสอดคล้อง hard-gating: ไม่มี tag = ยังวัดไม่ได้) | — |
| S-11 | **ตัวแปรรายงาน: ยก seed 3 ตัว (FAR/OSR/สุทธิ) เป็น first-class แสดงเลย** — editor สร้างสูตรเองย้ายไปหลัง "ขั้นสูง ▸" (progressive disclosure เฉพาะจุด); เพิ่มช่องหน่วยให้ var ที่ user สร้าง | −1 (Σ/▸ ยังอยู่แต่ผู้ใช้ 90% ไม่ต้องเจอ) |
| S-12 | **label ใน PDF overlay ใช้ชื่อ layer ภาษาไทย** (display เท่านั้น — คำนวณยังใช้ role/semanticTag ตาม invariant) | — |
| S-13 | เพิ่มหมวด layer ใน cheatsheet (Shift+↑↓/→/←, rename, swatch, จับกลุ่ม) — ระหว่างรอ S-4/S-2 ตัดของจริง | — |

เป้ารวม: concept ที่ผู้ใช้ต้องรู้ **18 → ~8** (layer, หมวด 6 อย่าง, ชั้น, ซ่อน/ล็อก, scale+verify, tag หน้า, รายงาน, CFSS สำหรับ advanced)

### Phase C — กลไกป้องกันไม่ให้กลับมาบวม

1. **เพิ่มมิติที่ 7 ในการ score ของ invent pipeline: "user-facing concepts added/removed"** — approach ที่เพิ่ม concept ต้องแสดงว่าคุ้มกว่า approach ที่ไม่เพิ่ม
2. **กติกา one-in-one-out** — invent ที่เพิ่ม concept ต้องระบุ concept ที่จะ retire (หรือแสดงเหตุผลยกเว้น) — เทียบเท่า consolidation trigger ของ proto แต่เชิง concept
3. **housekeeping sprint** เคลียร์ซากตาม §3.4

---

## 5. Test coverage gaps (จับคู่กับ bug ข้างบน)

มี guard ดีอยู่แล้ว: tuple engine + oracle, orphan heal (load-time), move-to-layer 13 checks, undo LAYERS/FOLDERS/MASTERS, floorKey precedence, report vars fold/chain/÷0, grid picker/ลบแถว/NaN, export endpoints caps

**ไม่มี guard (ตรงกับ findings)**: sign custom-ded ใน payload (B-1) · grid หลายหน้า / grid-vs-classic เมื่อมี ded (B-2/B-3 — fixture ปัจจุบันหลบทั้งคู่: หน้าเดียว + all-positive) · editor re-render คง useLive (B-4) · activeCat dangling → mint orphan (B-5) · excluded ใน XLSX (B-6 — ไม่มี test pin ฝั่งไหนเลย) · `_rvSeq` (B-7) · move ข้าม counting role (B-8) · context-menu desync (B-11) · DnD PF nesting / floorKey ไม่ตาม folder (B-12)

หลักที่ควรจำ (ซ้ำรอย save-wipe): **fixture ที่ "หลบ" เงื่อนไขจริง (หน้าเดียว, ไม่มี ded) ทำให้ test เขียวโดยไม่คุ้มครองอะไร** — fixture มาตรฐานควรมี ≥2 หน้า + มี deduction + มี custom layer + มีหน้า excluded

---

## 6. ลำดับที่แนะนำ

1. **Sprint แก้เลขผิด** (Phase A ข้อ 1-2): B-1 sign + B-4 useLive — เล็ก, ปิด bug เอกสารลูกค้า
2. **Sprint excluded-unify** (Phase A ข้อ 4): semantics เดียว + reroute computeSummary/XLSX เข้า tuple stream
3. **Sprint activeCat heal + MED batch** (Phase A ข้อ 3, 5)
4. **user ตัดสิน Phase B ทีละข้อ** — ข้อใหญ่สุดที่ต้องเลือกคือ S-1 (รายงานโหมดเดียว — ทาง ก หรือ ข) และ S-2 (ยุบแกนชั้น) → แต่ละข้อเป็น sprint แยกผ่าน `/bma-lite-dev`
5. **Housekeeping** ซาก sandbox + `lt-v2` residue (Phase C ข้อ 3)
6. **แก้ invent loop** เพิ่มมิติ concept-count (Phase C ข้อ 1-2) — docs-only

---

## 7. Ledger การดำเนินการ (source of truth ของ `/lite-simplify`)

> กติกา: `/lite-simplify` หยิบรายการ `queued` บนสุดตามลำดับ; รายการ `needs-GO` ห้ามหยิบจนกว่า user จะสั่ง GO เป็นรายข้อ (แล้วเปลี่ยนเป็น `queued`); เมื่อ ship ให้บันทึก commit hash + guard test ในคอลัมน์หมายเหตุ

| id | รายการ | phase | สถานะ | หมายเหตุ |
|---|---|---|---|---|
| A-1 | B-1 sign หักจาก role ไม่ใช่ id (`export-annotate.js:78`) + guard custom-ded-layer | A | shipped `0bf8eb2` | 2026-07-04. `id`→`role` 1 บรรทัด. guard `test_report_sign_role.py` `LITE_REPORT_SIGN_ROLE_OK` 13/13, RED-proof เอง (pre-fix net=125 → post-fix 75). regression test_report 17/17. fixture มาตรฐาน A-7 สร้างพร้อมกัน (custom_layer_report.bmaplan: 2+ หน้า, custom ded L5, excluded หน้า 1) |
| A-2 | B-4 ส่ง opts เข้า closure ทุกจุด `report-vars.js` + guard re-render คง useLive | A | queued | ~7 จุด |
| A-3 | B-5 heal `activeCat` (_afterHistory + removeLayer paths + sweep หลัง undo/redo) + guard | A | queued | |
| A-4 | B-6 excluded semantics เดียว — reroute computeSummary + buildExportData เข้า tuple stream + pin test | A | queued | ปิด B2-leftover |
| A-5 | MED batch: B-7 `_rvSeq` / B-8 กรอง counting ใน move menu / B-9 buildPageStore role-based / B-11 ปิด jss context menu / B-12 DnD guard PF+floorKey | A | queued | แตกได้ถ้า diff ใหญ่ |
| A-6 | LOW batch (§1 ท้ายตาราง): PF "+ เพิ่ม layer" pushUndo+role+floorKey, ล้าง LAYERS ตอน load ไฟล์เก่า, dead code, double-esc, observer disconnect, ฯลฯ | A | queued | |
| A-7 | fixture มาตรฐานใหม่ (≥2 หน้า + ded + custom layer + excluded) ใช้กับ guard ของ A-1..A-5 | A | queued | ทำพร้อม A-1 ได้ |
| S-1 | รายงานโหมดเดียว (เลือกทาง ก: grid พิมพ์ได้จริง+เลิก classic / ทาง ข: classic+override-overlay เลิก grid+vendor) | B | needs-GO | ข้อใหญ่สุด — user ต้องเลือกทาง |
| S-2 | ยุบแกนชั้น: folder membership = floorKey อัตโนมัติ, ตัด divergence banner | B | needs-GO | |
| S-3 | ซ่อน PF jargon ทั้งหมดจาก UI text | B | needs-GO | เล็ก เสี่ยงต่ำ |
| S-4 | ตัด user folder (📁+) + flatten migrate | B | needs-GO | |
| S-5 | ยอดพื้นที่ 7→3 ที่ | B | needs-GO | |
| S-6 | ประตู export เหลือ 2 + แก้ป้ายผิด | B | needs-GO | เล็ก |
| S-7 | ตั้งค่าหน้าประตูเดียว + ศัพท์ floorKind ชุดเดียว | B | needs-GO | |
| S-8 | ตัด warp-on-layer-click | B | needs-GO | เล็ก |
| S-9 | ทางเพิ่ม layer แบบเดียว | B | needs-GO | |
| S-10 | wizard lock เฉพาะ panel + ปุ่มข้ามไปวัดเลย | B | absorbed → INV-2026-07-04-002 (shipped 2026-07-04) | per-page JIT gate แทน SET gate — วัดหน้าไหนต้องแท็กหน้านั้น (hard) แต่ไม่บล็อกทั้งชุดอีกต่อไป; wizard เป็น optional tool |
| S-11 | seed vars first-class + editor หลัง "ขั้นสูง" + ช่องหน่วย | B | needs-GO | |
| S-12 | label PDF overlay เป็นชื่อ layer ไทย (display เท่านั้น) | B | needs-GO | เล็ก |
| S-13 | cheatsheet หมวด layer | B | needs-GO | เล็ก |
| C-1 | เพิ่มมิติ 7 "concepts added/removed" ใน invent scoring (แก้ .claude/skills + agents ที่เกี่ยว) | C | queued | docs-only |
| C-2 | กติกา one-in-one-out ใน invent pipeline | C | queued | docs-only, รวมกับ C-1 ได้ |
| C-3 | housekeeping ซาก §3.4 (editable-report B/D/D2/compare, lt-v2 residue, render-quality untracked, demo script, dead code) | C | queued | propose-first ก่อนลบ |

---

*ที่มา: รายงานเต็มของ 4 agents (layer code / report code / UX inventory / decision history) — สรุปคัดเฉพาะ finding ที่ยืนยันด้วย file:line แล้ว; รายละเอียด LOW ครบชุดอยู่ในรายงาน agent ซึ่งเก็บใน session transcript*
