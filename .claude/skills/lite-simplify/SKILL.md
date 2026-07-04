---
name: lite-simplify
description: |
  Execution loop for the "ดึง lite กลับสู่ความเรียบง่าย" campaign. Source of truth = `docs/design/REVIEW_LITE_LAYER_REPORT_20260704.md` (the 4-agent review: bug ตัวเลข + UX complexity 18 concepts + ประวัติ invent). One invocation = one ledger item shipped: pick the topmost `queued` row from §7 Ledger → spec → delegate to `lite-builder` per /bma-lite-dev discipline → verify → update ledger → ask GO to commit. Phase B rows are `needs-GO` and MUST NOT be picked until the user GOs that specific row.

  Trigger phrases (Thai): "/lite-simplify", "ทำต่อตามรีวิว", "simplify lite", "ลดความซับซ้อน lite", "แก้ตาม ledger", "ทำ A-1", "GO S-3"
  Trigger phrases (English): "/lite-simplify", "continue the simplify plan", "next simplify item", "work the review ledger"

  Do NOT use for: new lite features outside the review ledger (use /bma-lite-dev), proto work (bma-dev-loop), capturing ideas (/idea), or re-running the review itself (the review is done — this skill EXECUTES it).
---

# lite-simplify — executes the 2026-07-04 layer/report simplification review

Purpose: work through `docs/design/REVIEW_LITE_LAYER_REPORT_20260704.md` §7 Ledger, one item per invocation, until the ledger is exhausted. The review found: core engine (object-agg tuple stream) is sound; the pain is number-correctness bugs at the edges (Phase A) + user-facing concept bloat (Phase B, 18 → target ~8 concepts) + missing concept counter-force in the invent loop (Phase C).

**You (Opus) orchestrate; `lite-builder` (sonnet) writes code.** Full division-of-labor, spec format, review gate, size caps, and stale-memory guards are defined in `/bma-lite-dev` — this skill inherits ALL of them and adds the ledger discipline below. Do not restate them; go read `.claude/skills/bma-lite-dev/SKILL.md` if not already in context.

## Steps

### 0. LOAD
Read `docs/design/REVIEW_LITE_LAYER_REPORT_20260704.md` — at minimum §1 (bug table), §4 (proposals), §7 (ledger). Run `git log --oneline -5` + `git status --short` to catch work landed by other sessions; if a ledger row's fix already appears in git history, mark it shipped in the ledger (with commit) instead of redoing it.

### 1. PICK
- Take the **topmost `queued`** row. Never pick `needs-GO` unless the user explicitly GO'd that row id in this conversation (then flip it to `queued` in the ledger first, recording "GO <date>").
- If the user named a row ("ทำ A-3", "GO S-6"), that row wins.
- If NO row is `queued` and user gave no GO: report remaining `needs-GO` rows with a one-line pitch each, ask which to GO. **Halt.** (Phase B = UX-changing decisions; the review deliberately leaves them to the human.)
- `in-progress` row found (crashed prior session): resume it, don't pick a new one.
- Mark the picked row `in-progress` in the ledger before building.

### 1.5 ANNOUNCE + WAIT FOR CONFIRM (Opus) — ประกาศก่อนลงมือ ทุกครั้ง

**Hard gate. Never skip.** Before writing any spec or spawning the builder, tell the user in **plain Thai** (no jargon):
- แถวนี้คือข้ออะไร (row id) และปัญหาคืออะไรแบบภาษาคน
- จะแก้อะไร ไฟล์ไหน (สั้น ๆ 1-3 บรรทัด)
- แก้แล้วผู้ใช้จะเห็นอะไรต่างไป
- ความเสี่ยง / สิ่งที่อาจกระทบ (ถ้ามี)

Then **STOP and wait for the user to confirm ("โอเค" / "ทำเลย" / "GO")**. Do not proceed to build on your own initiative. If the user says change scope, adjust and re-announce. This gate applies to EVERY row including small ones — the user wants to approve each piece before it happens.

### 2. SPEC → DELEGATE → REVIEW → TEST
Only after the user confirms. Follow `/bma-lite-dev` steps 1-4 exactly. Additions specific to this campaign:

- **Spec must cite the review:** copy the exact file:line findings from §1/§4 for the picked row into the spec — the builder must not re-derive the diagnosis.
- **Fixture rule (review §5, non-negotiable):** every new guard test for A-row bugs uses a fixture with **≥2 pages + a deduction + a custom layer (role=ded, id≠"ded") + ≥1 excluded page** — the review proved single-page/all-positive fixtures let 4 HIGH bugs stay green. A-7 creates the shared fixture; if A-7 hasn't shipped yet and the picked row needs it, build the fixture as part of the row.
- **RED-first where the bug is reproducible:** prove the guard fails on pre-fix code (git stash trick) before applying the fix — same standard as `test_save_clickpath.py`.
- **Phase B rows change UX:** spec must state the before/after user flow in 2-3 lines, and REMOVE the old path in the same slice (the review's core finding: nothing was ever removed). Removing beats hiding. `.bmaplan` schema stays additive-only even when a concept is retired (old saves must load — migrate/flatten on load, never break).
- **Phase C rows are docs/skill edits** — no lite-builder needed; edit directly, no E2E, no-test rationale in outputs.
- **Invariant reminders:** calculation never reads layer.name OR layer.id for semantics — role/semanticTag only (that's what A-1 fixes; don't reintroduce). measure-engine.js / RS / pdfToC / cToPdf untouchable. MEASURE_PARITY_OK must stay green on anything geometry-adjacent.

### 3. LEDGER UPDATE
On PASS: edit the row → `shipped` + commit hash + guard test name/marker. On STOP/BLOCKED: → `blocked` + one-line reason. The ledger is the campaign's memory — future sessions (or a different Opus) resume from it cold.

### 4. REPORT (Opus) — พองานเสร็จ บอกว่าแก้อะไรไป ทุกครั้ง

**Hard gate. Never skip.** After the build passes review+test, tell the user in **plain Thai** what actually happened:
- แก้อะไรไปจริง ๆ (เทียบกับที่ประกาศไว้ตอน 1.5 — ถ้าต่างจากแผน บอกด้วยว่าต่างตรงไหน เพราะอะไร)
- ไฟล์ที่แตะ + เทสต์ผ่าน/ไม่ผ่าน
- ผู้ใช้จะเห็นอะไรต่างไปตอนใช้จริง
- เหลืออะไรที่ยังไม่ได้ทำในข้อนี้ (ถ้ามี)

Per project memory (progression > perfection): lead with **"เทียบกับรอบก่อน: ปิดไปแล้ว X/Y แถว, แถวนี้ปิดอะไร, ช่องว่างที่เหลือ"**. Then ask GO before commit — **no auto-commit**. Commit message prefix: `simplify(lite): <row-id> <short>`.

**สรุปจังหวะทั้งหมด:** PICK → **ประกาศ+รอคอนเฟิร์ม (1.5)** → build → **รายงานว่าแก้อะไร (4)** → รอ GO commit. ผู้ใช้อนุมัติ 2 จุด: ก่อนเริ่ม และ ก่อน commit.

## Stop conditions
- Forbidden/parity surface in diff → STOP, surface to user (per /bma-lite-dev).
- Size cap breached and extraction doesn't fit the slice → STOP, propose extraction slice.
- A Phase B row turns out to need schema-breaking change → STOP, reshape the row with the user.
- Ledger exhausted (all shipped/dropped) → declare the campaign done: report final concept count vs the 18→~8 target, propose closing sprint (finalize + memory note).

## Guardrails
- One invocation = one ledger row. No bundling rows unless the ledger row itself is a batch (A-5, A-6).
- Never edit proto/. Never auto-GO a `needs-GO` row.
- This skill executes the review; it does not relitigate it. If new evidence contradicts a finding, mark the row `blocked` with the evidence and ask — don't silently deviate.
