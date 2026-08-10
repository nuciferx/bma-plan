# INVENT — bluebeam-batch (4 candidates)

Date: 2026-08-10 (ดึก) · Pipeline: `/lite-invent` Phase 2 เสร็จ · Status: **awaiting human CHECKPOINT**
Source: Bluebeam feature review ในแชท 2026-08-10 → user สั่ง "วิจัยหัวข้อบูลบีมก่อน" (Track AI ถอยคิว)

## ผลวิจัยรายตัว (bma-researcher)

### (b) Viewports — หลาย scale ในหน้าเดียว → verdict `PRIOR_ART_MATURE` · size S · 🟢 อันดับ 1

- Pattern ของ Bluebeam ชัดเจน (ตีกรอบ region + ผูก scale เฉพาะกรอบ); point-in-rect ~5 LOC
- Data model additive ล้วน: `PS[page].viewports = [{rect, pts_per_m, label}]` + row เพิ่ม `viewportId` (optional)
- **ไม่แตะ forbidden เลย**: wrapper `getScaleForPage(pg, pt?)` อยู่นอก vendored core
- **ตามกฎ MATURE → ข้าม diverge/spike → sprint card ตรง** (scope: data model + wrapper + ปุ่มใน Page Setup + parity/export smoke — sprint เดียว)

### (c) Custom columns / สูตรราคา → core `MATURE` (ship แล้ว!) · grid UX `PARTIAL`

- แกนสูตร = LRV (report-vars) **ship ไปแล้วตั้งแต่ พ.ค.** — "cost formula" คือการเพิ่ม operand ราคา/หน่วย ไม่ใช่ของใหม่
- ส่วนที่ค้างคือ grid UX ซึ่งติดบั๊กที่รู้แล้ว **B-10/B-11** (localStorage hash + context-menu desync) — ต้องแก้ก่อนต่อยอด
- ข้อเสนอ: แตกเป็น 2 การ์ด — (c1) แก้ B-10/B-11 (bug sprint), (c2) คอลัมน์ราคา×พื้นที่ (S, ทำหลัง c1)

### (d) Vector-snap พอร์ตจาก proto → verdict `PRIOR_ART_MATURE` · size S · 🟡 คุ้มต่ำสำหรับตอนนี้

- โค้ดพร้อมยกจาก proto (`extract_snaps_pdfium`, proto/server.py:275 + `/analyse`) — งาน copy-port วันเดียว, forbidden ศูนย์
- **แต่**ไฟล์จริงของผู้ใช้ ~ทั้งหมดเป็นสแกน (ไม่มี vector) → ได้ประโยชน์เฉพาะไฟล์ digital-native ซึ่งยังน้อย
- ข้อเสนอ: file เป็น card `queued-low` รอวันที่แบบ digital ยื่นเยอะขึ้น

### (a) Compare/Overlay revisions → verdict `PRIOR_ART_PARTIAL` · size L · ตัวเดียวที่ต้องประดิษฐ์จริง

- Display ครึ่งหนึ่งง่าย (canvas blend modes เป็น native — Bluebeam/Drawboard ใช้ tint คนละสี + opacity slider)
- **ปมยากจริง 2 ปม**: (1) **สแกน 2 รอบไม่ตรงกัน** — ทางเลือก registration: manual 2-point click (UX ง่าย ไม่มี dependency) vs auto (opencv.js ~5-10MB WASM phase-correlation/ORB) (2) **lite ทั้งตัว assume เอกสารเดียว** — ต้องออกแบบ two-doc lifecycle (memory, page-sync nav, ความหมายต่อ layer/report: overlay = visualization-only?)
- **ต้อง DIVERGE (ยุทธศาสตร์ registration + architecture) + SPIKE (dual-doc proof)** ก่อนถึง GO ได้

## CHECKPOINT — คำถามถึง human

1. **(b) Viewports**: เขียน sprint card `needs-GO` แล้ว — GO เลยไหม? (S, เสี่ยงต่ำสุด คุ้มสุด)
2. **(a) Compare revisions**: จะให้**เดิน diverge+spike ต่อเลย** (ลงทุน invent เต็มตัว — ตัวนี้คือ candidate ที่มีคุณค่ากับงานตรวจแบบแก้ไขสูงสุด) หรือ**พักไว้** ให้ (b) ship ก่อน?
3. (c1) แก้บั๊กตาราง B-10/B-11 จะหยิบเมื่อไหร่ (เป็นทางผ่านของทั้งสูตรราคาและ report แก้ได้ที่เสถียร)
4. (d) เก็บ `queued-low` ตามข้อเสนอ — ok?
