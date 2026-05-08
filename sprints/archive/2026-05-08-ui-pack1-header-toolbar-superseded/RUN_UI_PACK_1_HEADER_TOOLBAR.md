# RUN_UI_PACK_1_HEADER_TOOLBAR.md — UI Overhaul Pack 1: Header + Toolbar

## Goal

Improve the visual quality and usability of the top header and measurement toolbar.

This sprint is **visual and organizational only**. No new geometry/drawing logic.

New drawing tools (arc, rectangle, circle, dimension arrow heads, callout box) are **out of scope** — they belong to a separate Tool Sprint.

---

## Scope Split Context

```
UI-1 (this sprint)  = header cleanup + toolbar visual + promote existing tools
Tool Sprint (later) = arc, rectangle, circle, dimension arrowhead, callout/leader box
```

---

## Required Reading

1. `AGENTS.md`
2. latest entry in `log.md`
3. `CURRENT_STATUS.md`
4. `FINAL_REPORT_FOR_CHATGPT.md`
5. `TEST_RESULT.md`
6. `UI_MANUAL_TEST.md`
7. `proto/ui.html`
8. `proto/server.py`
9. `proto/e2e_ui_test.py`

---

## Part 1 — Top Header Cleanup

### Current state

```
[brand] [file status] [Open PDF] [Open Project] [ตัวอย่าง] [page nav] [zoom] [scale badge] [summary] [Export]
```

Too many items at the same visual weight. No clear grouping.

### Requirements

Regroup header into **3 zones** with visible separation:

```
Zone A (left)   : brand/logo + file status (project name, current page)
Zone B (center) : page nav + zoom controls
Zone C (right)  : scale badge + Export button (prominent, green)
```

Rules:
- Remove or collapse items that are rarely used — move to a secondary action or dropdown
- `Open PDF` and `Open Project` → collapse into a single `เปิด ▾` dropdown button (Zone A)
- `ตัวอย่าง` → move to `เปิด ▾` dropdown or remove from header entirely
- `summary` numbers → show only if available, hide if zero/empty
- `Export` button → right-aligned, always visible, green, icon + label
- Font: use Inter / Noto Sans Thai stack, weight 500 for labels, 600 for actions
- Spacing: consistent 8px unit grid, header height max 48px
- No horizontal overflow at 1440px viewport

### Do not touch
- Header JS logic for Open PDF / page navigation / zoom behavior
- Export function / endpoint

---

## Part 2 — Measurement Toolbar

### Current primary tools

```
Pan | เลือก | พื้นที่ | ช่องเปิด | เส้นอ้างอิง | ตั้ง Scale | ระยะ | active-layer ▼ | Undo | เพิ่มเติม ▾
```

### Requirements

#### 2A — Promote from More menu to Primary toolbar

Move these tools from `เพิ่มเติม ▾` into the primary visible row:

| Tool | Thai label | Icon suggestion |
|---|---|---|
| กรอบที่ดิน / Parcel boundary | กรอบที่ดิน | ▭ with dashed border |
| ตั้งทิศเหนือ / North arrow | ทิศเหนือ | ↑N |
| Redo | Redo | ↷ |
| Delete selected | ลบ | 🗑 |

Keep these in More menu (secondary):
- เส้นต่อเนื่อง
- ถึง Ref
- ตั้งฉาก/perp
- ortho toggle
- loupe/size controls
- land-edge/setback helper (hidden by default, Phase 1)
- parking/room type controls

#### 2B — Visual improvements

- **Icon clarity**: use crisp SVG icons or Unicode symbols — no blurry emoji where SVG exists
- **Label**: show short Thai label below or beside icon for primary tools
- **Active state**: selected tool has clear highlight — filled background `#0a84ff`, white icon/text — not just a subtle border
- **Tool grouping**: add subtle visual dividers between logical groups:
  - Group 1: Pan, เลือก
  - Group 2: พื้นที่, ช่องเปิด, กรอบที่ดิน
  - Group 3: เส้นอ้างอิง, ระยะ, ตั้ง Scale
  - Group 4: ทิศเหนือ
  - Group 5: active-layer ▼
  - Group 6: Undo, Redo, ลบ
  - Group 7: เพิ่มเติม ▾
- **Responsive**: toolbar must not overflow at MacBook-like viewport (1440×900, 1512×982)
- **Height**: toolbar pill/row max 44px
- **Font**: same stack as header, size 11–12px for tool labels

#### 2C — More menu cleanup

Items remaining in More menu must still work. Do not break any existing tool logic.

Keep More menu as a proper dropdown (not a modal), positioned below the button, closes on outside click.

---

## Part 3 — Typography System (both header + toolbar)

Apply consistently:

```css
font-family: "Inter", "Noto Sans Thai", "Sarabun", system-ui, sans-serif;

/* weights */
--font-label:   500;  /* toolbar labels, header items */
--font-action:  600;  /* buttons with action (Export, เริ่มวัด) */
--font-data:    400;  /* numbers, status text, page info */

/* sizes */
--text-xs:   11px;  /* toolbar labels */
--text-sm:   12px;  /* header secondary items */
--text-base: 14px;  /* main body / properties */
--text-lg:   16px;  /* section headers */
```

Do not change font stack in canvas rendering (canvas uses system font, leave as-is).

---

## Scope — Allowed vs Forbidden

### Allowed

- CSS/HTML changes to `#top-header` and `#float-toolbar` / toolbar container
- Changing icon content (SVG/Unicode) for existing tools
- Moving buttons between primary and More menu
- Adding CSS variables for the typography system
- Updating `MAIN_UI_OK` e2e checks for new layout contracts
- Adding visual group dividers (CSS only, no JS)
- Updating font stack

### Forbidden

- **Arc / curve drawing tool** → Tool Sprint
- **Rectangle drawing tool** → Tool Sprint
- **Circle drawing tool** → Tool Sprint
- **Dimension line with arrow heads** → Tool Sprint
- **Callout / annotation box with leader line** → Tool Sprint
- Any change to measurement geometry, hit test, snap, or canvas drawing logic
- Any change to layer model, semanticTag, useCategory, save/load
- Any change to right panel, left panel, or properties panel
- Any change to Project Setup screen
- OCR, AI, legal rules, Rule Engine, Project PDF Save/Load
- Redesign of canvas area

---

## Acceptance Criteria

1. Header has 3 clear zones with visual separation.
2. `Open PDF` and `Open Project` collapsed into `เปิด ▾` dropdown.
3. Export button right-aligned, always visible, green.
4. No horizontal overflow at 1440px.
5. Toolbar primary row shows: Pan, เลือก, พื้นที่, ช่องเปิด, กรอบที่ดิน, เส้นอ้างอิง, ระยะ, ตั้ง Scale, ทิศเหนือ, active-layer ▼, Undo, Redo, ลบ, เพิ่มเติม ▾.
6. Active tool has filled `#0a84ff` highlight.
7. Tool groups have subtle dividers.
8. More menu still works and closes on outside click.
9. All promoted tools still trigger correct tool mode (no behavior change).
10. Font stack applied to header and toolbar.
11. `py_compile`, smoke, full PASS.
12. `MAIN_UI_OK`, `SITE_UI_OK`, `XLSX_OK`, `PROJECT_OK`, `SELECT_OK`, all existing regression tests PASS.
13. Scope grep: no forbidden strings.
14. No new drawing tools added.

---

## Manual UI Check

1. Open app
2. Confirm header: 3 zones, `เปิด ▾` dropdown works, Export right-aligned
3. Confirm toolbar: all 13+ primary tools visible, no overflow at 1440px
4. Click each promoted tool (กรอบที่ดิน, ทิศเหนือ, Redo, ลบ) — confirm tool mode activates
5. Click `เพิ่มเติม ▾` — confirm More menu opens with secondary tools, closes on outside click
6. Set scale → draw area → draw opening → confirm measurement flow unaffected
7. Check active state: click each primary tool — confirm blue highlight
8. Check tool groups: confirm visual dividers between groups
9. Export XLSX — confirm unaffected
10. Save `.bmaplan` / reload — confirm unaffected
11. Screenshot at 1440×900 and 1512×982

Update `UI_MANUAL_TEST.md`. Save screenshots to:
```
manual_test_artifacts/ui_pack_1_header_toolbar_YYYYMMDD/header.png
manual_test_artifacts/ui_pack_1_header_toolbar_YYYYMMDD/toolbar.png
manual_test_artifacts/ui_pack_1_header_toolbar_YYYYMMDD/more_menu.png
```

---

## Tests

```bash
python3 -m py_compile proto/server.py proto/e2e_ui_test.py
python3 proto/e2e_ui_test.py smoke
python3 proto/e2e_ui_test.py full
rg -n "ZONE_RULES|runCheck|FAR|OSR|Rule Engine|OCR|AI checker|ผังเมือง|Project PDF Save/Load" proto/ui.html proto/server.py proto/e2e_ui_test.py
```

Update `MAIN_UI_OK` e2e test to verify:
- toolbar primary tool count ≥ 13
- active tool highlight color matches `#0a84ff` or equivalent
- More menu button exists and opens menu
- header Export button exists and is right-aligned
- no horizontal overflow at 1440px viewport

---

## Output Files

Update:
- `PATCH_SUMMARY.md`
- `TEST_RESULT.md`
- `UI_MANUAL_TEST.md`
- `FINAL_REPORT_FOR_CHATGPT.md`
- `CURRENT_STATUS.md`
- `log.md`

---

## Stop Conditions

- Any measurement geometry, hit test, or canvas drawing logic changes → STOP
- Any new drawing tool implementation starts → STOP (that is Tool Sprint)
- `MAIN_UI_OK` / `SELECT_OK` / `XLSX_OK` regress → STOP
- `.bmaplan` save/load breaks → STOP
- Toolbar overflows at 1440px after changes → STOP and fix before continuing
- Forbidden strings appear → STOP

---

## Run Command

```powershell
cd "G:\drive\01 project\ai\bma-plan"
codex exec --sandbox workspace-write "Read RUN_UI_PACK_1_HEADER_TOOLBAR.md and run the same 5-agent pipeline: plan, patch, review/test, docs/check, final report. Visual and organizational changes to header and toolbar only. Do not add any new drawing tools. Do not touch measurement geometry, layer model, or save/load. Preserve all existing tool behavior."
```
