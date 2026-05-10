# RENDER_SCALE_REDUCE_AND_CACHE — Sprint Result

**Date:** 2026-05-11
**Sprint:** RUN_RENDER_SCALE_REDUCE_AND_CACHE
**Status:** PARTIAL — Task 1 FAILED (coordinate math regression), Task 3 DONE

---

## Goal

ลดเวลาโหลดหน้า PDF โดย:
1. ลด default `/page/{n}` render scale จาก 1.5 → 1.2
2. ปรับปรุง bounded in-memory page image cache key ให้ครบถ้วน

---

## Task Results

### Task 1: Reduce default render scale 1.5 → 1.2 — FAILED ❌

**What changed:**
- `proto/ui.html`: `const RS=1.5;` → `const RS=1.2;`
- `proto/server.py`: `get_page` default `scale=1.5` → `scale=1.2`
- `proto/server.py`: `/analyse` `"render_scale":1.5` → `1.2`

**Regression found immediately in smoke test:**
```
AssertionError: setback distances should be 2.0m:
{'distances': [2.5, 2.5, 2.5, ...]}
```

**Root cause:**
- `RS` (Render Scale) ใช้เป็นตัวคูณ/หารใน `pdfToC()` และ `cToPdf()` ซึ่งเป็นฟังก์ชันหลักของ coordinate math
- E2E test (`_test_setback_helpers`) ใช้ `const raw = (v) => v / RS;` ในการสร้าง polygon
- เมื่อ `RS` ลดจาก 1.5 → 1.2: `raw(20)` เปลี่ยนจาก `13.33` → `16.67` pt
- ผล: polygon ที่วาดมีขนาดใหญ่ขึ้น 1.25× → distance คำนวณผิด 2.0m → 2.5m
- ตัวคูณ 1.25 = 1.5/1.2 เป๊ะ

**Decision:** Reverted immediately per stop condition:
> "If changing render scale breaks measurement coordinate mapping, stop and report instead of guessing."

**Reverts applied:**
- `proto/ui.html`: `RS=1.2` → `RS=1.5`
- `proto/server.py`: default scale `1.2` → `1.5`
- `proto/server.py`: `/analyse` `render_scale: 1.2` → `1.5`
- `proto/STATUS.md`: doc table updated back to 1.5

---

### Task 3: Improve page image cache key — DONE ✅

**What changed:**
- `proto/server.py` `get_page()`:
  - Cache key เปลี่ยนจับ `("page", n, render_scale, rot)` → `("page", n, render_scale, rot, "jpeg", _jpg_quality)`
  - รวบ image format และ jpeg quality เข้า cache key ตาม spec

**Why this is safe:**
- ไม่แตะ coordinate math, measurement, calibration, drawing
- เป็น cache key change อย่างเดียว — ไม่เปลี่ยน behavior ของ `/page/{n}` response
- py_compile PASS, smoke PASS, full PASS หลัง revert scale + คง cache key ใหม่

---

## Test Results

```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py smoke                          → PASS (after revert)
python proto/e2e_ui_test.py full                           → PASS (after revert)
```

**All assertions green:**
- CACHE_OK, SETUP_OK, MAIN_UI_OK, VECTOR_OK, RECAL_OK, SITE_UI_OK, XLSX_OK, PROJECT_OK, RASTER_OK, WHEEL_OK, SNAP_OK, SELECT_OK, SETBACK_OK, EXT_MEASURE_OK, ANNOT_OK, PERSIST_OK, REAL_OK

---

## Files Changed

| File | Change | Status |
|------|--------|--------|
| `proto/server.py` | Cache key includes `"jpeg"` and `jpg_quality` | ✅ Kept |
| `proto/ui.html` | `RS=1.5` (reverted from 1.2) | ✅ Reverted |
| `proto/server.py` | Default scale `1.5` (reverted from 1.2) | ✅ Reverted |
| `proto/STATUS.md` | Doc table scale `1.5` (reverted from 1.2) | ✅ Reverted |

---

## Lessons Learned

1. **RS is NOT just a render parameter.** It is deeply embedded in frontend coordinate math (`pdfToC`, `cToPdf`, `raw()` in tests, vertex placement, snap radius). Changing RS requires updating every coordinate-dependent function simultaneously.

2. **To reduce render time without touching RS:**
   - Reduce `jpg_quality` (e.g. 88 → 70) — cuts bytes without changing pixel dimensions
   - Increase `MAX_IMAGE_CACHE_ENTRIES` / `MAX_IMAGE_CACHE_BYTES` — more cache hits
   - Add `cache-control` headers or browser-side image caching
   - Investigate progressive JPEG or lower chroma subsampling in PyMuPDF

3. **Cache key completeness matters.** Adding format+quality to cache key prevents silent cache corruption if future code changes quality or format.

---

## Known Gaps / Next Action

- Render scale reduction is **blocked** until coordinate math is decoupled from RS, or until a full refactor of measurement engine is justified (out of Phase 1 scope).
- Cache key improvement is **done** and safe.
- Next performance win should target `jpg_quality` reduction or cache size tuning.
