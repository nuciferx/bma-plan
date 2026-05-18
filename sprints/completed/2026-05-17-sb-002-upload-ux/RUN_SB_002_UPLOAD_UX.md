# RUN_SB_002_UPLOAD_UX — SB-2026-05-15-002: Upload-cap UX modal + cold-start hint

Date: 2026-05-17
Branch: main
Status: PASS — completed 2026-05-17
Commit hash: `33577b7`

## Goal

Surface the upload file-size limit clearly to the user: pre-flight modal before upload when file
exceeds cap, cold-start Setup screen shows the current limit, and the 413 error modal provides
actionable suggestions. Uses `max_upload_mb` field echoed by `/upload` (shipped in SB-001) so the
displayed value always matches the server constant without hard-coding.

Source: PHASE_INDEX.md row `SB-2026-05-15-002` (FRICTION, discovered by `bma-sandbox-test`
2026-05-15 on `251121_CHH_Submission_REV2 - Copy.pdf`).

## Scope — IN

- Pre-flight file-size check in `uploadPdfFile()`: fetch `max_upload_mb` from last `/upload` echo
  (cached in `currentUploadCapMB`); if `file.size > cap`, show modal before sending.
- `currentUploadCapMB` updated from `/upload` response echo (server-driven, not hard-coded).
- Cold-start Setup screen: adds hint text showing current limit (e.g. "รองรับไฟล์ถึง 256 MB").
- Clear 413 modal with actionable suggestions (compress PDF, reduce page count, check scan DPI).
- New E2E marker `SB002_UPLOAD_UX_OK` with 8 sub-checks.

## Scope — OUT

- No server changes (`proto/server.py` untouched — cap already raised in SB-001).
- No `.bmaplan` schema change.
- No forbidden-surface edits.

## Implementation summary

### Functions added / changed (`proto/ui.html`)

- `currentUploadCapMB` state variable — updated on every `/upload` response; starts `null`.
- `uploadPdfFile()` — added pre-flight branch: reads `file.size`, compares against `currentUploadCapMB`;
  if exceeded → show pre-flight modal, abort upload, do NOT send bytes to server.
- `showUploadCapModal(fileSizeMB, capMB)` — new helper; renders modal with file size / cap /
  3 actionable suggestions (compress, reduce pages, lower scan DPI).
- Cold-start setup screen: limit badge updated via `updateCapBadge()` when `currentUploadCapMB` known.

### E2E (`proto/e2e_ui_test.py`)

NEW `_test_sb002_upload_ux(page)` 8 sub-checks:
- A. `capVarExists` — `currentUploadCapMB` declared
- B. `updateFnExists` — `updateCapBadge` or equivalent fn present
- C. `preflight_fn_exists` — `showUploadCapModal` function present
- D. `coldStartHintPresent` — setup screen DOM has cap hint element
- E. `modalHasFileSize` — modal template references file-size token
- F. `modalHasCap` — modal template references cap token
- G. `modalHasSuggestions` — modal has at least 3 suggestion items
- H. `capReadFromEcho` — `currentUploadCapMB` update path wired to `/upload` response field

Marker `SB002_UPLOAD_UX_OK` wired after `UPLOAD_CAP_OK` in `main()`. Count: smoke +1.

## Files changed

| File | Change |
|---|---|
| `proto/ui.html` | `currentUploadCapMB` state; pre-flight check in `uploadPdfFile`; `showUploadCapModal`; `updateCapBadge`; cold-start hint update |
| `proto/e2e_ui_test.py` | NEW `_test_sb002_upload_ux` 8 sub-checks + marker `SB002_UPLOAD_UX_OK` |

## Tests run

```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PYCOMPILE_OK
python proto/e2e_ui_test.py smoke                          → PASS (with SB002_UPLOAD_UX_OK)
python proto/e2e_ui_test.py full                           → PASS GREEN
```

SB002_UPLOAD_UX_OK: `{capVarExists:T, updateFnExists:T, preflight_fn_exists:T, coldStartHintPresent:T, modalHasFileSize:T, modalHasCap:T, modalHasSuggestions:T, capReadFromEcho:T, all:T}`.

## Phase 1 + forbidden-surface check

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNTOUCHED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNTOUCHED
- `buildSnapIndex`, `snap` engine — UNTOUCHED
- `proto/server.py` — UNTOUCHED (client-only feature; cap already raised in SB-001)
- `.bmaplan` schema — UNTOUCHED (no save/load fields changed)
- Phase 1 boundary — kept (no legal verdict, no OCR, no AI, no FAR/OSR)

## References

- PHASE_INDEX.md row `SB-2026-05-15-002`
- SB-001 sprint card `sprints/completed/...` (cap raised; `/upload` echo added there)
