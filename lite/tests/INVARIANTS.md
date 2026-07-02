# INVARIANTS.md — ทะเบียน invariant กลางของ lite (V2-U1, DEVELOPMENT_V2_BLUEPRINT)

Date: 2026-07-03 · Status: canonical

**กติกา (บังคับตอน SCOPE ของทุกฟีเจอร์):** ก่อนเขียนโค้ด ต้องตอบ 2 ข้อ —
(a) ฟีเจอร์นี้แตะ invariant ตัวไหน → เพิ่ม fixture ของตัวเองเข้าเทสต์ invariant นั้น
(b) สร้าง "object kind / consumer ใหม่" ไหม → ถ้าใช่ ต้องไล่ตาราง consumer (I2) ให้ครบวันแรก
บทเรียนต้นกำเนิด: บั๊ก arc + CFSS อยู่ในระบบหลายสัปดาห์เพราะ I2 ไม่เคยถูกประกาศตอนสร้าง rollup

| ID | Invariant | Guard test (marker) | Tier |
|---|---|---|---|
| I1 | คณิตวัด lite ≡ proto byte-identical + ผลตัวเลขเท่ากันทุก fixture | `test_measure_parity.py` (MEASURE_PARITY_OK) | t0 |
| I2 | **ทุก rollup consumer == Σ ค่าป้าย object** (arc-inclusive, ทุก kind: poly / instance / อนาคต) — consumers ปัจจุบัน: computeSummary, buildExportData, exportPdfOverlay, buildReportPayload, _ltOwnArea, _lovsLayerArea | `test_summary_arc_parity.py` (LITE_SUMMARY_ARC_OK), `test_summary_cfss_parity.py` (LITE_SUMMARY_CFSS_OK) | t2 |
| I3 | พื้นที่ไม่แปรตาม rotation / translation / vertex-order / scale-linearity ÷k² / degenerate→null-not-NaN | `test_pbt_measure.py` (LITE_PBT_MEASURE_OK, 6 คุณสมบัติ × ~500 เคส) | t0 |
| I4 | save → load → เรขาคณิต+พื้นที่+identity ทุกหน้าเท่าเดิม (`.bmaplan` additive-only) | `test_metamorphic_pages.py` MR-save-roundtrip + `test_*_persist.py` ทั้งชุด | t2 |
| I5 | **สิ่งที่ export == สิ่งที่เห็นบนจอ** (ค่า, ตำแหน่ง, orientation รวม pageRot) | `test_pagerot_registration.py` (LITE_PAGEROT_REG_OK), `test_export_endpoints.py` | t2/t1 |
| I6 | raster ↔ overlay ตรงกันระดับ sub-pixel ทุก zoom/rotation | `test_overlay_registration.py` (LITE_OVERLAY_REG_OK, วัดจริง ≤0.5px) | t2 |
| I7 | พิกัด screen↔pt เป็น inverse เป๊ะ (1e-9) และวิ่งผ่าน kernel ที่ parity-tested (`pdfToC`/`cToPdf`) — ห้าม reimplement | `test_pagerot_registration.py` (mapping 4 มุม + inverse) | t2 |
| I8 | หน้าไม่มี scale → area = null (ไม่ใช่ 0, ไม่ใช่ pt ปนหน่วย) และถูก drop จาก rollup อย่างเงียบแต่สม่ำเสมอ | `test_live_overlay.py` + polyMetrics guard ใน I1 fixtures | t2/t0 |
| I9 | การจัดการหน้า (reorder/dup/delete/merge) ไม่ย้ายข้อมูลวัดไปผิดหน้า (identity-keyed) + dirty flag เสมอ | `test_metamorphic_pages.py` MR-reorder/MR-dirty/MR-render-source, `test_page_manager.py` E1-E16 | t2 |
| I10 | server ปลอดภัยต่อ payload ประสงค์ร้าย (caps ปฏิเสธ 400 ไม่ silent-truncate) และต่อ concurrency (fitz ถูก serialize ต่อ case) | `test_export_endpoints.py` (LITE_EXPORT_ENDPOINTS_OK), `test_case_lock.py` (LITE_CASE_LOCK_OK) | t1 |

**การเพิ่ม invariant ใหม่:** เพิ่มแถว + guard test ที่พิสูจน์ RED บนโค้ดที่ละเมิด (เสา 3) ก่อนนับว่า registered
**การเพิ่ม object kind ใหม่ (แบบ CFSS instance):** ต้องเพิ่ม fixture ของ kind นั้นเข้า I2, I4, I5 เป็นอย่างน้อย ภายใน sprint เดียวกัน — ไม่มีข้อยกเว้น
