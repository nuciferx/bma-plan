# PROGRESSIVE_PREVIEW_AND_BACKGROUND_FULL_RENDER — Sprint Result

**Date:** 2026-05-11
**Sprint:** RUN_PROGRESSIVE_PREVIEW_AND_BACKGROUND_FULL_RENDER
**Status:** BLOCKED — Reverted after smoke test memory exhaustion

---

## Goal

Implement progressive PDF page rendering:
1. Show preview (JPEG quality 50) quickly
2. Swap to full quality (75) when ready
3. Background warmup for adjacent pages

---

## Changes Attempted

### `proto/server.py`
- Added `preview: bool = False` parameter to `/page/{n}`
- Preview: JPEG quality 50, separate cache key
- Full: JPEG quality 75, separate cache key

### `proto/ui.html`
- `loadPage()` โหลด preview ก่อน → แสดง → โหลด full ใน background → swap

---

## Failure: Memory Exhaustion

**Smoke test failed immediately with:**
```
pymupdf.mupdf.FzErrorSystem: code=2: malloc (27098928 bytes) failed
```

**Root cause:**
- `loadPage(1)` → request preview (`/page/1?preview=1`, quality 50) → server render
- พอ preview โชว์ → `loadPage(1)` ทันที request full (`/page/1`, quality 75) → server render อีกรอบ
- พร้อมกันนั้น `buildSidebar()` → request thumbnails หลายสิบรอบ
- Server ต้อง render หลายครั้งพร้อมกัน → memory ไม่พร้อม

**Key insight from logs:**
```
[BMA_PAGE_RENDER_PERF] page=1 scale=1.5 preview=True total=574.8ms MISS
```
Preview quality=50 ลด encode time เหลือ ~545ms (จาก ~672ms ที่ quality=88) แต่ก็ยังต้อง render ทั้ง preview + full + thumbnails พร้อมกัน

**Progressive rendering ทำให้ server ทำงานหนักขึ้น (render 2 ครั้งแทน 1 ครั้ง)** ในขณะที่ memory มีจำกัด — ผลตรงกันข้ามกับเป้าหมาย

---

## Reverts Applied

- `proto/server.py`: เอา `preview` parameter ออก, กลับไป quality 88, cache key เดิม
- `proto/ui.html`: `loadPage()` กลับไป single-step image load

---

## Test Results (After Revert)

```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py smoke                          → PASS
python proto/e2e_ui_test.py full                           → PASS
```

All 17 E2E sections green.

---

## Lessons Learned

1. **Progressive rendering requires architecture support.** ไม่ใช่แค่ frontend trick — ต้องมี server queue / memory management ด้วย
2. **Rendering twice = worse, not better.** ถ้า server ไม่มี resource พอ
3. **Real bottleneck is concurrent render contention, not encode quality.** ต้องแก้ที่ server concurrency ก่อน

---

## Alternative Paths (Future)

1. **Server-side render queue:** Limit concurrent PyMuPDF renders to 1-2 threads
2. **Lower default quality:** ลด quality เป็น 70-75 โดยไม่ต้อง preview/full split
3. **Client-side image caching:** Cache browser-side ไม่ต้อง re-render ซ้ำ
4. **Server process pool:** Separate worker processes สำหรับ render
