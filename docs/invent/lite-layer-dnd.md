# Invent — lite layer drag-and-drop (reorder + group)

- **idea id**: `2026-05-23-00-59`
- **status**: **invent-done-go** — GO (A + D) at checkpoint 2026-05-23; build via `/bma-lite-dev`
- **pipeline**: `/lite-invent` (lite-framed)
- **spike**: `lite/sandbox/invent-layer-dnd.html`
- **frame date**: 2026-05-23

## Idea (verbatim)
> layer ทำระบบ แดรกแอนดรอป แทนลูกศร และการรวมกลุ่มก้เกิดจากการ แครกแอนดรอปเช่นกัน ui ใน layer จะได้เท่าเดิม จากที่เคยเป็น

Replace the layer tree's `▲▼` (reorder) + `→←` (indent/outdent) buttons with drag-and-drop; grouping also via drag; return the per-row UI to its cleaner pre-LST footprint.

## RESEARCH — verdict `PRIOR_ART_PARTIAL`
- Reorder/nest **gesture** is commoditized. **HTML5 native DnD is a trap** (no touch, no scroll-during-drag, dragImage pitfalls) → must use SortableJS or vanilla pointer-events.
- **SortableJS** (MIT, ~30 KB, CDN, touch) is the standard lib, but its DOM-position→model mapping fights lite's flat-`div`+`marginLeft` tree (visual nesting is CSS, not DOM nesting).
- **Auto-group-on-collision** (drag two loose layers together → auto-create folder) is **genuinely novel** — unmatched in AutoCAD / QGIS / Figma / Photoshop / Bluebeam. All incumbents use drag-between=reorder, drop-onto-folder=nest, with a line/triangle indicator.
- Incumbent friction: pixel-precision ambiguity between "nest" vs "insert below" → a **two-zone drop model** + clear indicator fixes it.
- Current `▲▼→←` buttons are keyboard-accessible; DnD-only would regress that → keep a fallback.

## FRAME
- **Forbidden-surface profile: CLEAN** — DnD only mutates `.order` + `.parentId`, both already in the model and already persisted additively in `.bmaplan`. Never touches `measure-engine.js` / RS / `pdfToC`-`cToPdf` / area math / `semanticTag`.
- **Size caps**: `ui-lite.html` 1135/1200 (65 headroom — keep logic OUT of the HTML); `layer-tree.js` 681/1000. New DnD code → new `lite/static/js/layer-dnd.js`.
- **Success**: `▲▼→←` removed; drag reorders + nests; grouping by drag; touch + keyboard fallback kept; `test_measure_parity.py` + tree tests stay GREEN; no cap breach.
- **Out of scope**: multi-select drag, cross-page moves, any law/calc coupling.

## DIVERGE + SCORE (6-dim, /5)
| approach | axis | nov | acc | UX | fit | bound | cost | total |
|---|---|---|---|---|---|---|---|---|
| **A** vanilla pointer-events, two-zone drop, kbd fallback | interaction-model | 3 | 5 | 5 | 5 | 5 | 3 | **26** |
| C right-click context-menu only (no drag) | accessibility | 2 | 5 | 3 | 5 | 5 | 5 | **25** |
| D vanilla DnD + auto-group-on-collision | novelty | 5 | 4 | 4 | 5 | 5 | 2 | **25** |
| E DnD reorder-only, `→←` kept | scope | 2 | 5 | 3 | 5 | 5 | 4 | **24** |
| B SortableJS vendored | library-use | 2 | 5 | 4 | 3 | 4 | 2 | **20** |

- **#1 = A.** Highest overall; no vendor file; fits the existing flat-div DOM without restructuring `buildPicker()`; two-zone drop kills the pixel-precision ambiguity. A's middle-40%-over-folder zone already satisfies "grouping via drag".
- **Fallback = C** if 30px rows make two-zone hit-testing too finicky (middle zone ≈ 12px). C also complements A as the keyboard/touch path.
- **D deferred** — the novel reading of the user's "grouping via drag". High value but undo-path risk + a 3rd visual zone on 30px rows; build it on A's skeleton in a Phase-2 slice.
- **B rejected for #1** — model-fit 3: SortableJS expects DOM-nested containers; lite nests via CSS margin. 30 KB against lite's lean ethos.

## SPIKE — what it proves
`lite/sandbox/invent-layer-dnd.html` implements A end-to-end on a mock tree + an **experimental D toggle** + a **keyboard-mode toggle**, at lite's real 30px row height. Question: does ghost + line-indicator + 2-zone hit-test feel unambiguous? Open it in a browser and try drag-reorder, drag-into-folder, toggle auto-group, toggle keyboard mode.

## Sprint slices (GO A+D — built via `/bma-lite-dev`)
- **LDND-S1** — `lite/static/js/layer-dnd.js`: pointer-events drag engine (ghost, two-zone hit-test, auto-scroll, line/highlight indicators) + commit ops reusing `childrenOf`/`reorderLayers`/`.parentId`. Wire to `buildPicker()` rows via a `⠿` grip. No model change.
- **LDND-S2** — remove `▲▼→←` button blocks from `layer-tree.js` row render (clears ~80 lines, restores pre-LST footprint); keep keyboard fallback (Shift+↑/↓ reorder, →/← nest/outdent).
- **LDND-S3** — auto-group-on-collision (Approach D): drop root layer onto middle of another root layer → `addFolder()` wrapping both, green double-ring indicator, clean undo, behind a setting. Builds on S1's skeleton.
- **LDND-S4** — tests: reorder/nest/outdent/auto-group parity via DnD + keyboard ops; `test_measure_parity.py` GREEN; `/bma-check-forbidden`; cap check on both files.

## Checkpoint decision — **GO (A + D), 2026-05-23**
User accepted Approach A as the baseline AND Approach D (auto-group-on-collision) as a first-class slice (LDND-S3), not deferred. Sprint card written to `PHASE_INDEX.md` as `invent-done-go`. Fallback C remains on record if S1's 30px two-zone hit-test proves finicky during the lite dev loop.
