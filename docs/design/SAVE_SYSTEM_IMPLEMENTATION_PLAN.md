# SAVE_SYSTEM_IMPLEMENTATION_PLAN.md — Save/Open Implementation Plan

Date: 2026-05-10

## Phase 4 — Save / Save As / Overwrite

Sprint: RUN_SAVE_SAVEAS_OVERWRITE.md
Commit: `save: support save as and overwrite current project`

### New State Variables

```js
let currentProjectHandle = null;  // FileSystemFileHandle (FSAPI) or null
let isDirty = false;               // true when unsaved changes exist
```

### Behavior

| Trigger | Handle exists | Action |
|---------|--------------|--------|
| Save button | Yes | Overwrite via FSAPI write |
| Save button | No | Run Save As flow |
| Save As button | Any | showSaveFilePicker → write → store handle |
| FSAPI unavailable | Any | Fall back to dlBlob() download |
| Save keyboard shortcut (Ctrl+S) | Any | Same as Save button |

### Save As Flow

```js
async function saveProjectAs() {
  if (!totalPages) { alert("เปิด PDF ก่อน"); return; }
  const safe = currentFileName.replace(/\.pdf$/i, "") || "project";
  if (window.showSaveFilePicker) {
    try {
      const handle = await window.showSaveFilePicker({
        suggestedName: safe + ".bmaplan",
        types: [{ description: "BMA-Plan Project", accept: { "application/json": [".bmaplan"] } }]
      });
      currentProjectHandle = handle;
      await _writeToHandle(handle);
      _markSaved();
    } catch (e) {
      if (e.name !== "AbortError") _fallbackDownload();
    }
  } else {
    _fallbackDownload();
  }
}
```

### Save (overwrite) Flow

```js
async function saveProject() {
  if (!totalPages) { alert("เปิด PDF ก่อน"); return; }
  if (currentProjectHandle) {
    try { await _writeToHandle(currentProjectHandle); _markSaved(); return; }
    catch (e) { currentProjectHandle = null; }
  }
  await saveProjectAs();
}
```

### Dirty State

Set `isDirty = true` in:
- `pushUndo()`
- `restoreSnapshot()` (undo/redo)
- `clearMeasures()`
- `applyLoadedProject()` → reset to false after load

Set `isDirty = false` in `_markSaved()`.

Update `lbl-save-state`:
- `isDirty` → "Unsaved changes"
- `!isDirty` → "Saved" (with handle) or "Downloaded"

### Hard Rules
- No save format change (version stays 1)
- No measurement/export code touched
- FSAPI failure → graceful fallback to download
- Save key (Ctrl+S) added via `keydown` listener (no conflicts with browser)

### E2E Additions
- `saveProjectNoCrash`: call saveProject() when no PDF → no exception
- `isDirtySetAfterEdit`: after pushUndo() + undo/redo, isDirty === true
- `isDirtyClearedAfterLoad`: after applyLoadedProject(), isDirty === false

---

## Phase 5 — Open / Recent Project

Sprint: RUN_OPEN_RECENT_PROJECT.md
Commit: `save: improve open and recent project workflow`

### Recent Files List

```js
const RECENT_KEY = "bmaPlan.recentProjects.v1";
function getRecentProjects() {
  try { return JSON.parse(localStorage.getItem(RECENT_KEY)) || []; }
  catch { return []; }
}
function addRecentProject(name) {
  const list = getRecentProjects().filter(x => x !== name);
  list.unshift(name);
  localStorage.setItem(RECENT_KEY, JSON.stringify(list.slice(0, 10)));
}
```

### "เปิด Project" Button Improvement

Current: single `<label>` wraps `<input type=file>`.

Target: button that:
1. Triggers `<input type=file>` (as before) for opening a file
2. After successful load: calls `addRecentProject(file.name)`
3. Shows a recent files dropdown (if list non-empty)

### Recent Files Dropdown

- Small popup below the button listing up to 5 recent file names
- Each row shows the filename; clicking opens `<input type=file>` pre-filtered
- "Broken" entries (file not found) cannot be detected from localStorage alone
  — show a warning on failed parse, not a crash

### Validation Consolidation

Extract a shared `_applyLoadedProjectFile(file)` async function used by:
- `proj-input change`
- `proj-input2 change`
- Future recent-file open

Both load paths get the same validation:
```js
if (proj.version !== 1) throw new Error("version ไม่รองรับ");
if (proj.pdfName && currentFileName && proj.pdfName !== currentFileName)
  console.warn("pdfName mismatch — continuing");  // warn, not block
```

Note: proj-input2 (export panel) currently skips validation. After this sprint, both use the same validator but with `pdfName` mismatch as a warning not an error (since the export panel "Load" is commonly used to merge projects).

### E2E Additions
- `recentProjectsStorageKey`: `localStorage.getItem("bmaPlan.recentProjects.v1")` accessible
- `addRecentProjectWorks`: after a load, filename appears in recent list
- `openBrokenRecentShownAsWarning`: non-parseable recent entry shows warning, doesn't crash UI

---

## What Does NOT Change

- `.bmaplan` save format (version: 1) stays identical
- Export (XLSX, PDF, JSON, CSV) unchanged
- Page-scoped layer model unchanged
- Measurement, calibration, area calculation unchanged
- Phase 1 forbidden items (legal checker, OCR, AI, Rule Engine, FAR/OSR) not touched
