# SAVE_SYSTEM_AUDIT.md — Current Save/Load Behavior

Date: 2026-05-10

## Current Save Behavior

`saveProject()` (proto/ui.html line 1284):
- Always downloads a new `.bmaplan` file via `dlBlob()` (anchor click)
- Filename: `{pdfName without .pdf}.bmaplan`
- Status bar says "Saved manually" after save
- No File System Access API (`showSaveFilePicker` not used)
- No overwrite / save-in-place
- No dirty state tracking
- No stored file handle or path after download

## Current Load Behavior

Two `<input type="file" accept=".bmaplan">` elements:
- `#proj-input`: topbar "เปิด Project" label
- `#proj-input2`: inside Export panel

Both call `applyLoadedProject(proj)` which restores state from JSON.

Validation on load (proj-input):
- `proj.version !== 1` → throws
- `proj.pdfName !== currentFileName` → throws (if PDF is loaded)
- `proj.totalPages !== totalPages` → throws

`proj-input2` skips validation (no checks).

No recent file list. No path stored after load.

## Save Format (version: 1)

```json
{
  "version": 1,
  "pdfName": "filename.pdf",
  "totalPages": N,
  "pageStore": { ... },
  "pageRotations": { ... },
  "pageTags": { ... },
  "pageNames": { ... },
  "projectInfo": { ... },
  "siteOrientation": { ... },
  "excludedPages": [...]
}
```

## File System Access API Availability

`window.showSaveFilePicker` is available in Chromium-based browsers (Chrome 86+, Edge 86+).
The app runs in a browser context. FSAPI can be used for overwrite.

Limitations:
- FSAPI requires user gesture (button click)
- File handle cannot be serialized across page reloads
- Recent files: only file names can be stored in localStorage (not handles)
- In some embeddings (iframe, electron without allowfileaccess), FSAPI may be unavailable

## Dirty State

`lbl-save-state` shows:
- "Manual save required" → after PDF load
- "Saved manually" → after saveProject() call

No `isDirty` flag. No tracking of what changed. No per-page dirty tracking.
The label is purely cosmetic and not used by any logic.

## Gaps

| Gap | Current | Required |
|-----|---------|----------|
| G1 | Always download new file | Save overwrites if handle/path known |
| G2 | No file handle stored | Store FSAPI handle after Save As |
| G3 | No dirty state | isDirty flag set on any data change |
| G4 | No recent files list | localStorage list of recent .bmaplan names |
| G5 | proj-input2 skips validation | Consistent validation on all load paths |
| G6 | No "save before close" guard | Prompt if isDirty on PDF load |

## Risk Table

| Feature | Risk | Notes |
|---------|------|-------|
| FSAPI Save overwrite | Low-Medium | Needs try/catch for unavailable FSAPI; fallback to download |
| isDirty tracking | Low | Set flag on pushUndo(), clearMeasures(), saveProject() |
| Recent files list | Low | localStorage only; file names not handles |
| Validation consolidation | Low | Shared helper for both load paths |
