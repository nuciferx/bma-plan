# TROUBLESHOOTING.md — BMA-Plan Known Failure Modes & Fixes

---

## 1. Static Assets Return 404 — UI Renders as Unstyled HTML

**Symptoms:**
- `GET /static/css/app.css → 404`
- `GET /static/js/semantic-meta.js → 404`
- `GET /static/js/opening-parent.js → 404`
- UI renders as raw/default unstyled HTML in browser
- E2E test passes but user's browser shows broken layout

**Root Causes (all three must be correct for static serving to work):**

| # | Cause | Check |
|---|-------|-------|
| 1 | `aiofiles` not installed | `python -c "import aiofiles"` — must not raise |
| 2 | Static mount guarded by a failing condition | Check server.py — mount must be unconditional |
| 3 | Relative `_STATIC_DIR` path breaks from wrong CWD | Must use `Path(__file__).resolve().parent / "static"` |
| 4 | Old server process still running on port 8001 | Kill old process before restarting |
| 5 | Browser caching 404 responses | Hard-refresh (Ctrl+Shift+R) or clear cache |
| 6 | UTF-8 BOM in app.css | `python -c "open('static/css/app.css','rb').read()[:3] == b'\xef\xbb\xbf'"` |

**Correct server.py pattern:**

```python
from pathlib import Path
from fastapi.staticfiles import StaticFiles

app = FastAPI()

_BASE_DIR = Path(__file__).resolve().parent
_STATIC_DIR = _BASE_DIR / "static"
print(f"[static] serving from: {_STATIC_DIR}")   # confirm on every startup
app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")
```

Do NOT guard the mount with `if _STATIC_DIR.exists():` — the guard hid a `RuntimeError`
from missing `aiofiles`, leaving the route unregistered with no error in the log.

**Fix checklist:**

```bash
# 1. Install aiofiles
pip install aiofiles

# 2. Verify requirements.txt includes aiofiles
grep aiofiles proto/requirements.txt

# 3. Kill old server
# Windows: find PID with `netstat -ano | findstr :8001` then `taskkill /PID <pid> /F`

# 4. Restart server from proto/ directory
cd proto
python server.py
# Should print: [static] serving from: .../proto/static

# 5. Verify 200 responses
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001/static/css/app.css
# Must return: 200

# 6. E2E verification (automated)
python e2e_ui_test.py smoke
# cssLinkPresent: True
# cssVarLoaded: True
# semanticMetaJsLoaded: True
# openingParentJsLoaded: True
```

**Post-fix sanity checklist:**
- [ ] Server startup log shows `[static] serving from: .../proto/static`
- [ ] `/static/css/app.css` → 200
- [ ] `/static/js/semantic-meta.js` → 200
- [ ] `/static/js/opening-parent.js` → 200
- [ ] UI has dark background and styled toolbar in browser
- [ ] E2E `cssVarLoaded: True`

**History:** Introduced by Frontend UI HTML Split sprint (2026-05-09). Fixed in Static 404 Fix sprint (proto `a2099ec`).

---

## 2. WinError 10054 on Uvicorn Shutdown

**Symptoms:** `ConnectionResetError: [WinError 10054]` in E2E test output after test suite ends.

**Root cause:** Windows TCP RST on uvicorn shutdown. Non-fatal.

**Action:** None required. Does not affect test results.

---

## 3. `? proto` in Root `git status --short`

**Symptoms:** Root git shows `? proto` or `M proto` depending on whether proto has staged changes.

**Root cause:** `proto/` is a nested git repo tracked as a submodule pointer in root.

**Action:** Commit proto/ normally inside `proto/`. Root `git add proto && git commit` updates the submodule pointer. Non-blocking.

---

## 4. AUTO_MERGE.lock Error on Root Commit

**Symptoms:** `error: cannot lock ref 'AUTO_MERGE': Unable to create '.../.git/AUTO_MERGE.lock': File exists.`

**Root cause:** Pre-existing stale lock from a prior interrupted git operation. Non-blocking — commits succeed.

**Action:** If commit fails (not just warns), delete the lock file manually:
```bash
rm "F:/drives/My Drive/01 project/ai/bma-plan/.git/AUTO_MERGE.lock"
```
