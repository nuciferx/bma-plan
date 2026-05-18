# ANTI_PATTERNS.md — BMA-Plan Patterns to Avoid

Patterns confirmed to have caused real incidents in this project.
Each entry: what the pattern is, why it failed, and what to do instead.

---

## 1. Guarding a Required Mount Behind a Soft Condition

**Anti-pattern:**
```python
_STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(_STATIC_DIR):
    app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")
```

**Why it fails:**
- If `StaticFiles(...)` raises `RuntimeError` (e.g., `aiofiles` not installed),
  the mount is skipped silently — no error in the server log, no 404 at startup,
  just every `/static/*` request returning 404 at runtime.
- The `if os.path.exists` guard passes (the directory exists) but does not protect
  against the `RuntimeError` from the missing dependency.

**Result:** UI renders as unstyled HTML. E2E may pass (headless browser sometimes
uses cached CSS) while the real browser shows broken layout.

**Do instead:**
```python
from pathlib import Path
_BASE_DIR = Path(__file__).resolve().parent
_STATIC_DIR = _BASE_DIR / "static"
print(f"[static] serving from: {_STATIC_DIR}")
app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")
```
Mount unconditionally. If the directory is missing, let it fail loudly at startup.
Add `aiofiles` to `requirements.txt`.

---

## 2. CWD-Relative Static Paths

**Anti-pattern:**
```python
_STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
# or
_STATIC_DIR = "static"
```

**Why it fails:**
- `os.path.dirname("server.py")` = `""` (empty string when `__file__` is bare).
- `os.path.join("", "static")` = `"static"` — relative to CWD.
- Running `python server.py` from root rather than from `proto/` gives
  `static/` relative to root, which does not exist there → 404 or guard failure.

**Do instead:**
```python
from pathlib import Path
_BASE_DIR = Path(__file__).resolve().parent   # always absolute
_STATIC_DIR = _BASE_DIR / "static"
```

---

## 3. Listing `aiofiles` as Optional or Omitting from requirements.txt

**Anti-pattern:** Not listing `aiofiles` in `proto/requirements.txt`.

**Why it fails:**
- `fastapi.staticfiles.StaticFiles` (via starlette) requires `aiofiles` for async
  file streaming on Python 3.x.
- Without it, any `StaticFiles(directory=...)` call raises `RuntimeError: The "aiofiles"
  package must be installed to use StaticFiles`.
- A new developer (or CI environment) running only `pip install -r requirements.txt`
  will not get `aiofiles` and static serving will silently fail.

**Do instead:** Always list `aiofiles` explicitly in `proto/requirements.txt`.
After adding it, verify: `python -c "import aiofiles; print(aiofiles.__version__)"`.

---

## 4. UTF-8 BOM in Extracted CSS Files

**Anti-pattern:** Extracting CSS from an HTML `<style>` block using an editor or tool that
adds a UTF-8 BOM (`\xef\xbb\xbf`) to the output file.

**Why it fails:**
- Some browsers (notably older Edge, some WebKit builds) reject a CSS file that starts
  with a BOM, or fail to parse the first rule (`*{box-sizing:border-box...}` becomes
  `\xef\xbb\xbf*{...}` which is invalid syntax for the `*` selector).
- The result is the stylesheet loads (HTTP 200) but applies no styles.

**Check:**
```python
with open("static/css/app.css", "rb") as f:
    print(f.read(3) == b"\xef\xbb\xbf")   # True = BOM present, must fix
```

**Fix:**
```python
with open("static/css/app.css", "rb") as f:
    data = f.read()
if data[:3] == b"\xef\xbb\xbf":
    data = data[3:]
with open("static/css/app.css", "wb") as f:
    f.write(data)
```

---

## 5. Assuming E2E Pass = Browser Renders Correctly

**Anti-pattern:** Reporting "UI is correct" based solely on E2E test pass.

**Why it fails:**
- E2E tests (Playwright/headless Chromium) may use a cached stylesheet version or
  evaluate CSS variables against a stale cached asset.
- `cssVarLoaded: True` in E2E does not guarantee the user's browser (Chrome, Edge,
  Safari) sees the styled page — especially after a cold server restart or cache bust.

**Do instead:**
- After any static asset change, verify the styled page in a real browser manually.
- Add HTTP-level verification (curl or requests) to confirm 200 + non-empty body.
- Mark all static-touching sprints as requiring `UI_MANUAL_TEST.md`.

---

## 6. Not Killing the Old Server Before Restarting

**Anti-pattern:** Starting a new `python server.py` without killing the prior process.

**Why it fails:**
- If port 8001 is already bound, uvicorn raises `[Errno 10048] Only one usage of each
  socket address` and exits immediately.
- If port 8001 is not bound (prior process died) but the browser has a cached 404
  from the broken server, the user sees a stale broken page even after the fix.

**Do instead:**
```bash
# Kill prior server
netstat -ano | findstr :8001     # find PID
taskkill /PID <pid> /F           # kill it

# Then restart
cd proto && python server.py

# Then hard-refresh browser: Ctrl+Shift+R
```
