# RUN_MAIN_PAGE_RENDER_PRIORITY_FIX

**Goal:** แก้ปัญหา PDF โหลดช้าโดย prioritizing การ render หน้าหลัก และป้องกัน thumbnail sidebar แย่ง server/render resource

**Problem:**
- Browser timing แสดง delay อยู่ที่ `img request+onload` สำหรับ `/page/{n}`
- UI post-first-visible ทำงานเร็ว (~20ms)
- แต่ sidebar thumbnails อาจ load พร้อมกันกับหน้าหลัก ทำให้เกิด contention

**Hard Rules:**
- Keep FastAPI + PyMuPDF
- Keep RS=1.5
- Do not change coordinate math
- Do not change save/load, export, measurement

**Tasks:**
1. Audit open/load flow — หาว่า `/page/{n}` และ `/thumb/{n}` เรียกเมื่อไร
2. Add instrumentation — log main page vs thumbnail timing
3. Fix thumbnail priority — lazy load, delay after main page visible, limit concurrency to 2
4. JPEG/cache tuning — ลอง quality 75 ถ้าปลอดภัย

**Stop conditions:**
- ถ้า smoke/full test fail → stop and report
- ถ้า coordinate math drift → stop and report

**Tests:**
- `python -m py_compile proto/server.py proto/e2e_ui_test.py`
- `python proto/e2e_ui_test.py smoke`
- `python proto/e2e_ui_test.py full`
