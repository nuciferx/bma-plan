---
name: bma-check-forbidden
description: |
  Use BEFORE editing any BMA-Plan source file to verify the target isn't in the forbidden-surfaces table. Returns OK / WARN / BLOCK with the exact rationale and a safer alternative if applicable.

  Trigger phrases (Thai): "แตะได้ไหม", "ตรงนี้ปลอดภัยไหม", "จะแก้ X", "forbidden", "เปลี่ยน Y ได้มั้ย", "RS ลดได้มั้ย"
  Trigger phrases (English): "is this safe to edit", "can I change X", "is X forbidden", "safe to modify"

  Always run before edits to: polyAreaM2/pdfToC/cToPdf/RS/buildSnapIndex/snap/.bmaplan schema/server.py endpoints.
---

# /bma-check-forbidden — Forbidden Surfaces Pre-Edit Check

Goal: prevent re-incidents from the anti-patterns catalog. Fast lookup against the canonical table — no need to re-read CLAUDE.md or ANTI_PATTERNS.md each time.

## Canonical Forbidden Table

| Surface | File | Rule | Verdict |
|---|---|---|---|
| `polyAreaM2`, `polyMetrics`, `polySelfIntersects` | `proto/ui.html` | Area math contract. Add NEW functions next to them; never edit. | 🔴 BLOCK |
| `pdfToC`, `cToPdf`, scale math | `proto/ui.html` | Coordinate conversion. Rotation + zoom + RS all depend. | 🔴 BLOCK |
| `RS` constant (= 1.5) | `proto/ui.html` + E2E `raw()` helper | Baked into setback math and tests. Prior reduce sprint BLOCKED. | 🔴 BLOCK |
| `buildSnapIndex`, `snap` | `proto/ui.html` | CAD snap engine. | 🔴 BLOCK |
| Core upload/render/analyse endpoints | `proto/server.py` | Case isolation + render cache contract. | 🟡 WARN |
| `.bmaplan` schema field RENAME/REMOVE | save/load in `proto/ui.html` | Breaks user saves. | 🔴 BLOCK |
| `.bmaplan` schema field ADD (additive) | save/load in `proto/ui.html` | OK — schema is additive only. | 🟢 OK |
| `app.mount("/static", ...)` guard with `if exists()` | `proto/server.py` | Anti-pattern #3 — swallows aiofiles RuntimeError. | 🔴 BLOCK |
| UTF-8 BOM in `proto/static/css/app.css` | static | Breaks CSS parse in some browsers. | 🔴 BLOCK |
| Progressive PDF rendering (preview + full) | server | Prior sprint BLOCKED — OOM on real PDFs. | 🔴 BLOCK |
| Calculate from `layer.name` / `layer.slug` | anywhere | Page-Scoped Layer Model — use `semanticTag` / `measurementProfile` / `reportTarget`. | 🔴 BLOCK |
| `layer.id` cross-page comparison | anywhere | Layers are page-scoped — same name on diff pages = diff ids. | 🔴 BLOCK |
| Adding legal pass/fail UI / verdict badges | UI | Phase 1 hard rule — capture facts, never judge. | 🔴 BLOCK |
| OCR / AI / Rule Engine / FAR-OSR auto | anywhere | Phase 1 explicitly excludes. | 🔴 BLOCK |
| Global `SESSION` (no case_id) | `proto/server.py` | Per-case isolation invariant. | 🔴 BLOCK |
| Cache `m` / `m²` values | anywhere | Raw geometry contract — always re-derive from current scale. | 🔴 BLOCK |
| Promote `auto-unverified` scale to confident metric | anywhere | Scale state contract. | 🔴 BLOCK |

## Steps

1. **Parse target**: user describes what they want to change (file, symbol, behavior).
2. **Match against table** above.
3. **Output verdict in this format:**

   ```
   ### Forbidden Check: <target>

   Verdict: 🟢 OK / 🟡 WARN / 🔴 BLOCK

   Reason: <one line from table or derived>

   <if BLOCK>Safer alternative: <e.g., "Add new function `xxxAreaM2` next to polyAreaM2 instead of editing it">

   <if WARN>Required before edit:
   - Run smoke + full E2E before AND after
   - Update UI_MANUAL_TEST.md
   - Verify no regression in: <relevant markers>
   ```

4. If the user's request is ambiguous (e.g., "change scale handling"), ask one clarifying question — never assume.

## Heuristics for ambiguous targets

- Mentions "scale" → check `RS`, `pdfToC`, scale math → likely BLOCK
- Mentions "save" / "load" / ".bmaplan" → check schema rename → likely WARN
- Mentions "static" / "CSS" → check mount pattern + BOM → likely WARN
- Mentions "measurement" / "area" → check `polyAreaM2` family → likely BLOCK if editing existing
- Mentions "layer" → check page-scoped model + name-based calculation → likely BLOCK
- Mentions "performance" / "render" → check progressive rendering + RS reduce → likely BLOCK
