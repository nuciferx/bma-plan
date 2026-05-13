# RUN_PROGRESSIVE_PREVIEW_AND_BACKGROUND_FULL_RENDER

**Status:** BLOCKED — Reverted after smoke test memory exhaustion

**Goal:** ลดเวลาเปิดหน้า PDF โดยใช้ progressive rendering (preview quality 50 ก่อน แล้วค่อย swap เป็น full quality 75)

**Problem:**
- เปิด PDF หน้าใหญ่ → JPEG encode ใช้เวลานาน → user เห็นหน้าขาวนาน
- Solution attempted: โหลด preview quality ต่ำก่อน (เร็ว) → show → แล้วค่อยโหลด full ใน background → swap

**Hard Rules:**
- Keep FastAPI + PyMuPDF
- Keep RS=1.5 (coordinate math unchanged)
- Do not change pdfToC(), cToPdf(), measurement, calibration, drawing
- Do not change save/load, export

**What was attempted:**
1. `proto/server.py`: เพิ่ม preview mode `/page/{n}?preview=1` (JPEG quality 50) และ full mode quality 75
2. `proto/server.py`: cache key แยก preview vs full
3. `proto/ui.html`: `loadPage()` → request preview → show → request full → swap

**Why it failed:**
- Smoke test memory exhaustion: `malloc (27MB) failed`
- Progressive rendering ทำให้ server render 2 ครั้ง (preview + full) + thumbnails พร้อมกัน
- Memory ไม่พอสำหรับ concurrent renders

**Reverts applied:**
- `proto/server.py`: เอา preview parameter ออก, กลับไป quality 88
- `proto/ui.html`: `loadPage()` กลับไป single-step

**Test after revert:** py_compile PASS · smoke PASS · full PASS

**Output:** `docs/status/PROGRESSIVE_PREVIEW_AND_BACKGROUND_FULL_RENDER.md`
