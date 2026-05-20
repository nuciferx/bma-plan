# Phase 1 Scope-Creep Audit — 2026-05-20

Read-only review of `proto/` against the Phase 1 boundary. Source: /idea 2026-05-20 (scope-creep audit). **Report-only — no code changed.**

Phase 1 = **Raster PDF Measurement Assistant** ("CAD core + Foxit measurement behavior + Excel-style summary"). Hard-forbidden: legal checker, OCR, AI, rule engine, FAR/OSR/setback **pass-fail**, K.1 generator, auto boundary detection, multi-user/SaaS.

## Verdict: 🟢 No Phase-1 VIOLATION — 🟡 1 watch-item + UX-chrome breadth

`proto/ui.html` = 3,887 lines (trigger at 5,000).

## 1. Hard-forbidden surfaces — CLEAN (zero hits)

Grep across `server.py` + `ui.html` for `tesseract/pytesseract`, `openai/anthropic/tensorflow/torch/onnx`, `cv2/findContours/detectBoundary`, `login/auth/jwt/bcrypt` → **0 matches**. No OCR, no AI/ML, no auto-boundary detection, no auth/multi-user. ✅

## 2. Closest-to-the-line (intentional, bounded — NOT a violation)

**Site-plan ratios — BCR / OSR / FAR / setback / building-distance** (Phase I-C/D/E, ~83 refs across ui.html + server.py).
- Computes legal-style ratios AND echoes user-defined limits beside them — but **rigorously facts-only**: code comments throughout say "no verdict / no pass/fail", summary widget header says "อัตราส่วน (ไม่มี verdict)", XLSX footer says "ไม่มีการพิจารณาผ่าน/ไม่ผ่านตามกฎหมาย".
- **Risk:** this is **one cell away** from a forbidden "FAR/OSR validation / rule engine" — a single future "✓/✗ ผ่าน" column or red/green compare would cross the line. Decided facts-only by user 2026-05-13 (Q1=A).
- **Recommendation:** keep; add a regression assertion that **no verdict/pass-fail cell ever renders** (lock the line so a future sprint can't drift across it). `lawBasis`/`countingRule` metadata fields are neutral tags — fine.

## 3. Over-engineered / breadth beyond the core goal (not forbidden, but heavy)

These are tested + user-requested, so **not cut candidates** — but they expand the surface well past "mini-CAD area measurement," consistent with the bloat trend:

| Subsystem | ~refs | Note |
|---|---|---|
| Zen / Overview / Focus (F11/F12 + minimap + edge-peek + onboarding) | ~150 | Largest non-measurement layer; 6 invent sprints (INV-001a/b/c, 002a/b/c) |
| Annotation suite (comment/highlight/rect/circle/arrow/cloud/sticky/text) | ~89 | Broad markup vs core measurement |
| Settings v1+v2 (4 tabs, loupe/export prefs) | ~72 | |
| ⌘K command palette | ~43 | Page-jump nav |
| Multi-export (XLSX + 1-page XLSX + JSON + CSV + annotated PDF ×2 + PNG ZIP + print-canvas) | — | Many overlapping output paths |
| dev-website static docs site | — | `proto/static/docs/` |
| Widget-placement system | ~2 | Mostly dormant now |

## 4. Recommendations (priority order)

1. **Lock the site-plan line** — add a marker/test asserting no pass/fail verdict UI ever appears (the only real boundary risk). Small sprint.
2. **Freeze new UX-chrome** unless it directly serves measurement — Zen/palette/settings/annotation breadth is the main "over-engineered" driver, not any forbidden feature.
3. **Don't cut shipped features** — all are tested + user-requested; removing them costs more than it saves and risks regressions.
4. **Leaner build path already queued** — the "BMA-Plan Lite — standalone `/lite/` folder" backlog idea is the right home for a stripped-down core if desired.

## 5. Queued cards (PHASE_INDEX) — quick check
No `queued`/`invent-queued` card proposes a forbidden capability. Closest watch-items remain site-plan follow-ons (all facts-only). No OCR/AI/auto-boundary/legal-verdict card present.
