# Plan: Phase G — Menu Wiring + Measure/Layer Power-up

## Context

**Why:** Mockup V3 Alignment Phases A–F (branch `feature/mockup-v3-alignment`) จบลงด้วย menu-bar 13 items แบบ **visual-only** (ไม่มี dropdown ทำงาน). ตอนนี้:
1. **Implement** dropdown ใช้งานได้จริง สำหรับ 6 เมนูสำคัญ: Project / Scale / Page / Measure / Object / Layer
2. **ตัด disabled items ออกหมด** — เมนูสะอาด มีแต่ของกดได้จริง
3. **Surface ฟังก์ชั่นพลังที่ซ่อน** ใน `#hidden-controls` (Ortho/Loupe/Perp/Setback Distance ฯลฯ)
4. **แก้ bug** per-page layer memory ที่ overwrite ซ้ำๆ ทำให้ user รำคาญ

**Source of truth:** `docs/design/bma-plan-mockup-v3.html` — CSS lines 113–145, 6 menu defs lines 848–968

**Phase 1 hard constraints (ห้ามแตะ):**
- legal / OCR / AI / Rule Engine / FAR/OSR / K.1 / draggable workspace / save-load migration
- `proto/server.py`, `.bmaplan` schema, `polyMetrics`, `polyAreaM2`, `pdfToC`, `cToPdf`, coord math, snap algorithm

**Out of scope for this sprint (designed-but-deferred to Phase H):**
- Polygon curves / Circle / Ellipse / Quick Rectangle / Arc Edge tools
- Annotate menu (comment / highlight / frame / cloud / arrow) — จะเป็น **item ที่ 14** ใน menu bar (ไม่ rename Workspace)
- File / Edit / View / Review / Export / Workspace / Help dropdowns

**Branch:** ทำงานบน branch ใหม่ `feature/menu-power-up` (สาขาจาก `main` หลังจาก Mockup V3 alignment merge)

---

## Final menu specs (56 items total — no disabled rows)

### 1. Project (4 items)
```
📋 Project Info               → openSetup()
📊 Project Summary            → showSummaryWidget() + switchSWTab('area')
─────────
💾 Save Project       Ctrl+S  → saveProject()
📁 Open Project       Ctrl+O  → openProjectBtnClick()
```

### 2. Scale (7 items)
```
📏 Set Scale Current Page  S  → setMode('calib')
📊 Scale Manager              → openScaleManager()
✓ Verify Scale                → verifyScale()                                [helper]
🔄 Reset Page Scale           → resetPageScale(curPage)                      [helper]
─────────
Scale Status by Page          → openScaleManager()
Show Scale Line               → toggleScaleLine()                            [helper]
⚠ Scale Warning               → showSummaryWidget() + switchSWTab('warn')
```

### 3. Page (8 items)
```
📄 Page Manager                  → openPageManager()
🏷 Set Page Type / Floor / Label → openSetup()
Auto Name Pages                  → triggerSetupAutoTag()                     [helper]
─────────
◀ Previous Page         PgUp  → loadPage(getPrevPage(curPage))
▶ Next Page             PgDn  → loadPage(getNextPage(curPage))
↺ Rotate 90° CCW              → rotatePage(-90)
↻ Rotate 90° CW               → rotatePage(90)
─────────
📊 Page Summary               → showSummaryWidget() + switchSWTab('floor')
```

### 4. Measure (19 items)
```
↖ Select                      V       → setMode('sel')
✋ Pan                       H       → setMode('pan')
─────────
⬡ Area (Polygon)              A       → activateAreaTool('room')
Opening / Deduction           O       → toggleOpening()
Land / Site Boundary          L       → activateAreaTool('land')
Building Footprint            B       → activateAreaTool('building')
─────────
Dimension                     D       → setMode('dist')
Path / Continuous Distance    Shift+D → setMode('path')
Reference Line                R       → setMode('ref')
─────────
↑ North Arrow                 N       → setMode('north')
Parking                       P       → setMode('parking')
─────────
Snap Modes ▶
  ├─ Endpoint                 E       → toggleSnap('ep')
  ├─ Midpoint                 M       → toggleSnap('mp')
  ├─ Center                   C       → toggleSnap('ct')
  ├─ Nearest Line                     → toggleSnap('nl')
  ├─ Intersection                     → toggleSnap('ix')
  ├─ Perpendicular            ⌘P      → togglePerp()
  └─ Disable All Snaps                → toggleSnap('off')
Ortho Mode (0°/90°)         Shift+O → toggleOrtho()
Loupe Magnifier              Shift+L → toggleLoupe()
─────────
Show Reference Distances              → toggleRefDistance()
Show Setback Distances                → toggleSetbackDistance()
Validate Polygons                     → validateAllPolygons()                [helper]
Clear Current Page                    → clearMeasures()
─────────
Finish Drawing                Enter   → finishCurrentArea()
Cancel Drawing                Esc     → cancelDrawing()
Undo Point                    ⌘Z      → undo()
```

### 5. Object (7 items)
```
Object Properties             → focusPropertiesTab()                         [helper]
Rename Object         F2      → openNamePanel() for selected
─────────
Change Category               → focusPropertiesTab() + scrollToField('useCategory')
Change Semantic Tag           → focusPropertiesTab() + scrollToField('semanticTag')
─────────
Link Opening to Area          → focusPropertiesTab() + scrollToField('parentLink')
Unlink Opening                → rpSetOpeningParent(null) for selected
─────────
Delete Object         Del     → deleteSelectedObject()    ← class="dd-item danger"
```

### 6. Layer (11 items)
```
Set Active Layer ▶
  ├─ พื้นที่ย่อย (sub_area)
  ├─ พื้นที่หลัก (base_area)
  ├─ ช่องเปิด (deduction)
  └─ อ้างอิง (reference_geometry)
─────────
Show Active Layer             → toggleLayer(activeLayer, true)
Hide Active Layer             → toggleLayer(activeLayer, false)
Lock Active Layer             → toggleLayerLock(activeLayer, true)
Unlock Active Layer           → toggleLayerLock(activeLayer, false)
─────────
Solo Active Layer             → soloLayer(activeLayer)                       [helper]
Show All Layers               → setAllLayersVisible(true)                    [helper]
Hide Other Layers             → hideOtherLayers(activeLayer)                 [helper]
Lock All Other Layers         → lockOtherLayers(activeLayer)                 [helper]
Unlock All Layers             → setAllLayersLocked(false)                    [helper]
─────────
Select All in Active Layer    → selectAllInLayer(activeLayer)                [helper]
```

**Total active items:** 4 + 7 + 8 + 19 + 7 + 11 = **56 items**

---

## Critical files

| File | Change scope |
|---|---|
| `proto/ui.html` | 6 dropdown markup + `toggleMenu` + close-handler + 14 helpers + keyboard shortcuts (11 ใหม่) + bug fix `_syncPageLayersToGlobals` |
| `proto/static/css/app.css` | `.dropdown`, `.dd-item`, `.dd-item:hover`, `.dd-item.danger`, `.dd-sep`, `.shortcut`, `.dd-submenu`, `.menu-item.active .dropdown` (~35 บรรทัด) |
| `proto/e2e_ui_test.py` | ~15 assertions ใหม่: menu structure, click dropdown, action triggers, keyboard, layer per-page memory fix |
| Root docs | `PATCH_SUMMARY.md`, `TEST_RESULT.md`, `UI_MANUAL_TEST.md`, `FINAL_REPORT_FOR_CHATGPT.md`, `CURRENT_STATUS.md`, `log.md` |

**ห้ามแตะ:** `proto/server.py`

**Estimated change:** ~650 lines (proto: ~540, css: ~35, e2e: ~75)

---

## Helper functions ที่ต้องเพิ่ม (14 ตัว ใน `proto/ui.html`)

| Helper | Purpose | Implementation hint |
|---|---|---|
| `toggleMenu(el)` | open/close dropdown + ปิด siblings | toggle `.active` class |
| `closeAllMenus()` | document click handler | remove `.active` from all `.menu-item` |
| `verifyScale()` | เปิด Scale Manager + ไฮไลต์ row หน้าปัจจุบัน | `openScaleManager()` + scroll/highlight |
| `resetPageScale(pg)` | ล้าง scale ของหน้า | `delete pageStore[pg].scaleSeg` + `pushUndo()` + `updateWorkspaceState()` |
| `toggleScaleLine()` | toggle flag per-page | `pageStore[pg].showScaleLine = !` + `redraw()` |
| `focusPropertiesTab()` | เปลี่ยน left panel เป็น Properties | `setSidebarMode('properties')` |
| `triggerSetupAutoTag()` | reuse setup auto button | `openSetup()` then click `#setup-auto-btn` |
| `validateAllPolygons()` | scan + report | loop polys ใน curPage, run `polySelfIntersects()`, push warnings ไป Summary Widget |
| `soloLayer(slug)` | active visible, others hidden | loop layers, set visible |
| `setAllLayersVisible(b)` | bulk visibility | loop `LAYER_ORDER`, set + redraw + buildRightPanel |
| `hideOtherLayers(slug)` | hide except active | loop, hide if slug !== active |
| `lockOtherLayers(slug)` | lock except active | loop, lock if slug !== active |
| `setAllLayersLocked(b)` | bulk lock | loop, set locked |
| `selectAllInLayer(slug)` | batch select | iterate page objects, push to selection set |

---

## Keyboard shortcuts ใหม่ (11 ตัว)

ของเดิม: V (sel), A (area), O (opening), L (land), D (dist), R (ref), N (north), Enter, Esc, Cmd+Z, Cmd+S

**เพิ่ม:**
| Shortcut | Action |
|---|---|
| H | pan |
| B | building footprint |
| Shift+D | path |
| P | parking |
| F2 | rename selected object |
| PgUp / PgDn | prev / next page |
| Cmd+P | perp snap toggle |
| Shift+O | ortho mode toggle |
| Shift+L | loupe toggle |
| E / M / C | snap toggles ตอนวาด |

**Guard:** ไม่ trigger ถ้า `event.target` เป็น `<input>`, `<select>`, `<textarea>`, หรือ modal เปิด

---

## CSS additions (`proto/static/css/app.css`)

```css
.menu-item { position:relative; }
.dropdown { display:none; position:absolute; top:100%; left:0;
  background:var(--surface2); border:1px solid var(--border);
  border-radius:6px; min-width:220px; padding:4px 0;
  box-shadow:0 8px 32px rgba(0,0,0,.5); z-index:200 }
.menu-item.active .dropdown { display:block }
.dd-item { padding:5px 16px; font-size:12px; color:var(--text2);
  cursor:pointer; display:flex; align-items:center; gap:8px;
  transition:background .08s, color .08s }
.dd-item:hover { background:var(--accent); color:#fff }
.dd-item.danger { color:var(--red) }
.dd-item.danger:hover { background:rgba(255,69,58,.18); color:var(--red) }
.dd-sep { height:1px; background:var(--border); margin:4px 0 }
.dd-item .shortcut { margin-left:auto; font-size:10px; color:var(--text3) }
.dd-item:hover .shortcut { color:rgba(255,255,255,.6) }
.dd-submenu-trigger::after { content:"▶"; margin-left:auto; font-size:9px; color:var(--text3) }
.dd-submenu { display:none; position:absolute; left:100%; top:0;
  background:var(--surface2); border:1px solid var(--border);
  border-radius:6px; min-width:200px; padding:4px 0;
  box-shadow:0 8px 32px rgba(0,0,0,.5) }
.dd-item:hover > .dd-submenu { display:block }
```

---

## Bug fix: per-page layer memory

**ปัญหา:** `_syncPageLayersToGlobals()` (`proto/ui.html` ~line 374) ทำงานทุกครั้งที่โหลดหน้า มัน overwrite global `layerVis`/`layerLock` จาก `pageStore[pg].layers[]` ซึ่งสร้างใหม่จาก preset → user ที่ซ่อน layer แล้วเปลี่ยนหน้ากลับ → layer กลับมา visible

**Fix:** เปลี่ยน logic เป็น "merge preset เฉพาะ slug ที่ pageStore ไม่มี" — เก็บ user changes:
```js
function _syncPageLayersToGlobals() {
  const pg = curPage;
  if (!pageStore[pg]?.layers) return;
  pageStore[pg].layers.forEach(l => {
    // อย่า overwrite ถ้า user มีการเปลี่ยนใน session นี้
    if (l._userModified) return;
    layerVis[l.slug] = l.visible;
    layerLock[l.slug] = l.locked;
  });
}
```
หรือ track ผ่าน flag separate. รายละเอียดเลือกใน implementation

**Test:** `perPageLayerMemoryFixed` — hide base_area page 1 → switch page 2 → back to page 1 → still hidden ✓

---

## Implementation steps

### Step 1 — CSS scaffolding
- เพิ่ม CSS block ลง `app.css`
- run smoke → PASS (ยังไม่มี visual change)

### Step 2 — Markup + toggleMenu + click-outside (proto)
- 6 dropdown markup ใต้ menu-item Project/Scale/Page/Measure/Object/Layer (placeholder items)
- `toggleMenu()` + global click handler + Esc to close
- run smoke → PASS (dropdown เปิด/ปิดได้)

### Step 3 — Wire Project / Scale / Page / Object (simple menus)
- ผูก dd-items ไปยังฟังก์ชั่นเดิม
- เพิ่ม helpers: verifyScale, resetPageScale, toggleScaleLine, focusPropertiesTab, triggerSetupAutoTag
- เพิ่ม keyboard: Ctrl+O, F2, PgUp/PgDn
- run smoke → PASS

### Step 4 — Measure power-up
- ผูก hidden capabilities: Ortho/Loupe/Perp/Ref Distances/Setback Distances/Clear/Path/Parking
- Snap submenu (6 items)
- `validateAllPolygons()` helper
- เพิ่ม keyboard: H, B, Shift+D, P, Cmd+P, Shift+O, Shift+L, E, M, C
- run smoke → PASS

### Step 5 — Layer power-up + bug fix
- New helpers: soloLayer, setAllLayersVisible, hideOtherLayers, lockOtherLayers, setAllLayersLocked, selectAllInLayer
- Layer submenu (4 items)
- Bug fix: `_syncPageLayersToGlobals` merge logic
- run smoke → PASS

### Step 6 — E2E assertions
เพิ่ม assertions ใน `proto/e2e_ui_test.py`:
- `menuStructureOk` — 6 dropdowns, item counts 4/7/8/19/7/11
- `noDisabledItems` — no `.dd-item.disabled` ใน 6 menus
- `menuClickOpens` — Project menu คลิก → `.active`
- `clickOutsideCloses` — คลิกข้างนอก → `.active` removed
- `dropdownActionTriggers` — spy on saveProject, setMode('calib'), etc.
- `keyboardB` — กด B → mode=area + atype=building
- `keyboardF2` — กด F2 หลังเลือก → name panel เปิด
- `keyboardPgUp` — กด PgUp → curPage−1
- `keyboardShiftO` — Shift+O → ortho mode active
- `snapSubmenuToggles` — E key toggles ep
- `soloLayerWorks` — solo sub_area → others hidden
- `lockOthersWorks` — lock others → ดูว่า lock state เปลี่ยน
- `selectAllInLayerWorks` — N objects ใน sub_area → selection set มี N items
- `perPageLayerMemoryFixed` — bug fix ทำงานจริง
- `validatePolygonsWarns` — self-intersecting poly → warning ปรากฏ
- run smoke + full → PASS

### Step 7 — Docs + commits
- update PATCH_SUMMARY.md, TEST_RESULT.md, UI_MANUAL_TEST.md, FINAL_REPORT_FOR_CHATGPT.md, CURRENT_STATUS.md, log.md
- proto commit: code changes
- root commit: submodule pointer + docs

---

## Verification

```
python3 -m py_compile proto/server.py proto/e2e_ui_test.py    → PASS
python3 proto/e2e_ui_test.py smoke                            → PASS
python3 proto/e2e_ui_test.py full                             → PASS (17 markers + new menu assertions)
```

**Measurement baseline (ต้องไม่เปลี่ยน):**
- VECTOR 305.56 / XLSX สุทธิ 0.82 / PERSIST page1 66646.05 + page2 11883.33 / REAL 45 pages, rotation 90°

**Manual verification:**
- คลิก Project → 4 items แสดง, คลิก Save → ไฟล์ download
- คลิก Scale → 7 items, Set Scale → calib mode
- คลิก Page → 8 items, ปุ่ม Prev/Next + Rotate ใช้ได้
- คลิก Measure → 19 items + submenu Snap แสดง 7 sub-items
- กด B → Building Footprint mode active
- กด PgUp → ไปหน้าก่อน
- คลิก Object → 7 items, Delete สีแดง
- คลิก Layer → 11 items + submenu Set Active Layer 4 sub-items
- ซ่อน base_area หน้า 1 → ไปหน้า 2 → กลับหน้า 1 → ยังซ่อน ✓
- คลิกข้างนอก → dropdown ปิด
- Esc → dropdown ปิด

---

## Risk + mitigation

| Risk | Mitigation |
|---|---|
| Keyboard E/M/C ทำงานตอนพิมพ์ใน input | guard `event.target.tagName !== 'INPUT'/'TEXTAREA'/'SELECT'` |
| Solo Layer ทำให้ select / hit-test ทำงานผิด | reuse existing `layerVis` check — ทำงานอยู่แล้ว |
| Per-page bug fix break โหลดโปรเจกต์เก่า | กรณี pageStore ไม่มี layer state → ใช้ preset (fallback) |
| Validate Polygons สแกน loop เยอะ → ช้า | sync run on click — page poly count ≤ 50 |
| Loupe / Ortho session-only — ไม่ persist | OK สำหรับ Phase G; persist เป็น Phase 2 |
| Lock Active Layer ทำให้วาดไม่ได้ | current code: drawing into locked layer ไม่ถูก block — ยังคงสถานะเดิม (เป็น known issue) |
| Menu-bar overflow ที่ 13 items | OK สำหรับ Phase G (ไม่เพิ่ม slot); G.4 (Annotate item 14) จะกระทบ — risk ทราบไว้ก่อน |

---

## Out of scope (deferred to Phase H)

ออกแบบใน plan นี้แล้ว — แค่ defer การ implement ไป sprint ถัดไป:

### Phase H.1 — Polygon curves + Circle + Ellipse (Measure additions)
- ⭕ Circle tool (radius from center, area = πr²)
- ⬭ Ellipse tool (a, b semi-axes, area = πab)
- ⌒ Arc Edge (toggle next polygon segment to be arc)
- □ Quick Rectangle (drag 2 corners → 4-vertex polygon)
- **Area math:** สร้าง `circleAreaM2`, `ellipseAreaM2`, `arcSegmentArea`, `polygonAreaWithArcs` — ไม่แตะ `polyAreaM2` (backward compat)
- **Schema:** polygon vertex เพิ่ม `edgeType?, arcRadius?, arcSweep?` (optional fields, backward compat)
- **Risk:** medium — area math + render + hit-test ใหม่

### Phase H.2 — Annotate menu (item 14)
- เพิ่มเป็น menu item 14 (ระหว่าง Layer และ Review) — **ไม่ rename Workspace**
- Menu items: Comment / Highlight / Rectangle Frame / Circle Frame / Cloud Frame / Arrow Pointer / Free Text Label / Clear Annotations
- **Schema:** `pageStore[pg].annotations = []` (additive — backward compat)
- **Render:** `drawAnnotations()` ใหม่ใน `redraw()` z-order บนสุด
- **Export:** XLSX sheet ใหม่ "Annotations"; annotated PDF include annotations
- **Risk:** medium — menu-bar 14 items อาจล้น viewport ที่เล็กกว่า 1280px; revision cloud SVG path complex

### Phase H.3 — File / Edit / View / Review / Export / Workspace / Help dropdowns
- เปิดทำงานอีก 7 dropdowns ที่เหลือ
- File: New Project, Open Recent, Export Recent, Quit
- Edit: Undo/Redo + Select All/None + Cut/Copy/Paste (ถ้าทำ)
- View: Show/Hide panels, theme, language
- Review: Open Check Panel, Show Warnings, Export Report
- Export: XLSX, PDF Annotated, JSON, CSV
- Workspace: Recent Workspaces, Reset Layout
- Help: About, Keyboard Shortcuts Cheatsheet, Documentation Link

---

## Stop conditions (ห้าม PASS ถ้าเจอ)

- Area / Opening / Land drawing เสีย
- Save / Load .bmaplan ไม่ทำงาน
- Export XLSX / PDF เสีย
- ปุ่ม ribbon เดิมไม่ทำงาน
- Keyboard shortcut เดิม (V/A/O/L/D/R/N/Enter/Esc/Cmd+Z/Cmd+S) เปลี่ยน behavior
- Measurement values เปลี่ยน
- Right panel layers list หาย / lock/visibility toggle เสีย
- modal เปิดอยู่แต่ keyboard shortcut ใหม่ trigger (must guard)
- Per-page bug fix break round-trip save/load
