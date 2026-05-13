# RUN_RENDER_SCALE_REDUCE_AND_CACHE

**Goal:** ลดเวลาโหลดหน้า PDF โดยลด default render scale 1.5→1.2 และปรับปรุง page image cache key ให้ครบถ้วน (รวม format+quality)

**Status:** PARTIAL — Task 1 FAILED (coordinate math regression), Task 3 DONE

**Context:**
- `BMA_PRE_FIRST_PAGE_LOAD` แสดง delay ~18.5s โดยส่วนใหญ่จาก GET `/page/{n}`
- PyMuPDF render audit พบว่า JPEG encode เป็นตัวการหลัก (~93% ของ render time)
- ลด scale 1.5→1.2 = ลด pixel count ~36% → encode เร็วขึ้นประมาณ 36%
- Cache มีอยู่แล้วแต่ key ยังไม่รวม image format และ jpeg quality

**Files edited:**
- `proto/ui.html` — `RS=1.5` (reverted from 1.2 after regression)
- `proto/server.py` — default scale 1.5 (reverted), cache key รวม format+quality (kept)
- `proto/STATUS.md` — doc table updated and reverted

**Regression found:**
- `RS=1.2` ทำให้ `_test_setback_helpers` fail: distances เปลี่ยน 2.0m → 2.5m
- Root cause: `RS` ใช้ใน `pdfToC()`/`cToPdf()`/`raw()` — ไม่ใช่แค่ render parameter
- ตัวคูณ 1.25 = 1.5/1.2 เป๊ะ

**Decision:** Reverted RS and server default scale back to 1.5. Cache key improvement kept.

**Tests (after revert):**
- `python -m py_compile proto/server.py proto/e2e_ui_test.py` → PASS
- `python proto/e2e_ui_test.py smoke` → PASS
- `python proto/e2e_ui_test.py full` → PASS

**Acceptance (achieved for cache task only):**
- BMA_PAGE_RENDER_PERF log แสดง HIT/MISS ชัดเจน ✅
- Cache key รวม format+quality ✅
- ทุก test PASS ✅
- BMA_PRE_FIRST_PAGE_LOAD ลดลง ~36% ❌ (blocked by coordinate math)
