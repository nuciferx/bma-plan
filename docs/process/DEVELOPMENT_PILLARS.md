# DEVELOPMENT_PILLARS.md — เสาหลักวิธีการพัฒนา BMA-Plan

Date: 2026-07-02
Status: canonical — กลั่นจากวิธีทำงานที่พิสูจน์ผลจริงในวัน 2026-07-02
(13 commits: 4 accuracy-bug fixes + 2 infra + 4 perf ships + docs, suite 60→67 ไฟล์, 0 regression, `MEASURE_PARITY_OK` ไม่หลุดแม้ครั้งเดียว)

ทุก sprint/บั๊ก/ฟีเจอร์ ต้องผ่านครบทั้ง 6 เสา — เสาไหนข้ามไม่ได้ ระบุ halt ไว้ท้ายเสา

---

## เสา 1 — วัดก่อนแก้ (Evidence before action)

**หลักการ:** ห้ามแก้/ออกแบบจากสมมุติฐาน ทุกการตัดสินใจต้องมีตัวเลขหรือ file:line รองรับ

**หลักฐานว่าทำไมต้องมี:**
- แผน "placeholder JPEG" ที่ดูสมเหตุสมผล ถูก**ฆ่าด้วยข้อมูล** (โพรบชี้ว่า upload คือตัวถ่วง ไม่ใช่ /raw — placeholder ต้องรอ upload เหมือนกัน)
- ข้อสงสัย "pan กระพริบ" จาก code review ถูก**หักล้างด้วยโพรบ** (0/10 blank, 3 ไฟล์ × 2 รอบ) — ประหยัดไป 1 sprint เต็มๆ
- ทิศทาง `Matrix.prerotate` ถูกทดสอบเชิงประจักษ์ 4 มุม**ก่อน** wiring ลงโค้ด

**กลไก:** perf → เขียนโพรบวัดจริง (`artifacts/perf/`); bug → specialist read-only ตรวจ code จริงทุก claim ก่อนได้ patch plan; ambiguity → spike ใน sandbox
**Halt:** ถ้า claim ไหนยังยืนยันด้วยโค้ด/ตัวเลขไม่ได้ → ไม่เข้าขั้น FIX

## เสา 2 — ลงทะเบียนก่อนลงมือ (File-first tracking)

**หลักการ:** ทุก finding/bug/idea เข้า `PHASE_INDEX.md` (และ `bug-archive.jsonl` เมื่อ fix) **ก่อน**เริ่มงานแก้ — stop-condition กลางทางต้องไม่ทำให้งานหาย

**กลไก:** แถว PHASE_INDEX เขียนตอน triage เสร็จ (สถานะ queued) → อัปเดตเป็น done พร้อม commit hash + ตัวเลขจริง; bug-archive ต้องมี repro + guard_test + fixed_commit ครบ
**Halt:** ไม่มีแถวใน roadmap = ยังไม่เริ่มแก้

## เสา 3 — Guard test ต้องพิสูจน์ RED→GREEN (Tests that provably catch the bug)

**หลักการ:** เทสต์ที่ไม่เคยแดง = ยังไม่รู้ว่าจับบั๊กได้จริง ทุก fix ต้อง `git stash` พิสูจน์ว่าเทสต์**แดงบนโค้ดเก่า**ก่อนนับว่าเสร็จ

**หลักฐาน:** ทุก fix วันนี้มี RED proof (arc: 12000 vs 15926.99 / CFSS: throw จริง / pageRot: (15,15) vs (585,15) / local-open: paint รอ upload)
**กติกาคู่กัน:**
- **Assert invariant ไม่ใช่ implementation** — เทสต์ "ยอดรวม == Σ ป้าย object" ตัวเดียวจับบั๊กได้ทั้งคลาส (arc + CFSS + อนาคต)
- **Hard-fail เท่านั้น** — สะสม failures แล้ว `sys.exit(1)`; ห้ามพิมพ์ `*_OK` ถ้าเช็คข้างในเป็น False (บทเรียน soft-pass ของ proto ที่ทำให้ regression ผ่านเขียวทั้งกระดาน)
- **Ground truth อิสระ** — เทียบ closed-form (`10000+1250π`) ไม่เทียบฟังก์ชันที่กำลังทดสอบ (กัน tautology)
**Halt:** เทสต์ไม่แดงบนโค้ดเก่า = เทสต์ยังใช้ไม่ได้ ห้าม commit

## เสา 4 — สัญญาแตะไม่ได้ + ทางเลี่ยงมาตรฐาน (Contract protection)

**หลักการ:** คณิตวัด (`measure-engine.js` vendored, drift-locked byte-identical กับ proto), schema `.bmaplan` (additive-only), forbidden surfaces — **ไม่แก้ ให้เพิ่มฟังก์ชันใหม่ข้างๆ หรือ route ผ่านของที่ tested แล้ว**

**หลักฐานว่าวิธีนี้ชนะ:** บั๊ก pageRot แก้โดย**ต่อสาย**เข้า `pdfToC`/`cToPdf` ที่ vendor+parity-tested อยู่แล้ว (net 0 บรรทัด, ปิดช่องโหว่ drift-lock เป็นผลพลอยได้) แทนที่จะเขียน rotation ใหม่; helper `rollupAreaM2` วางข้าง `instanceAreaM2` แทนการแตกแขนง 6 จุด (postmortem ชี้ว่า per-site duplication คือสาเหตุที่ 6 จุด drift แต่แรก)
**กลไก:** `MEASURE_PARITY_OK` ต้องเขียวทุก commit; line caps (`ui-lite` 1200 / โมดูล 1000) บังคับแตกโมดูล; แตะ forbidden-adjacent = regression หนาแน่นขึ้นตามสัดส่วน
**Halt:** ทางแก้เดียวที่มีต้อง edit forbidden surface → STOP แล้ว file เป็น BLOCKED ให้มนุษย์ตัดสิน

## เสา 5 — หนึ่งปัญหา หนึ่ง sprint หนึ่ง commit (Small verified ships)

**หลักการ:** commit เดียวจบในตัว: fix + guard test + regression result + archive entry — ไม่รวมหลายปัญหา, ไม่ commit ครึ่งทาง

**กลไก:** ลำดับตายตัว INTAKE → TRIAGE → FILE → SCOPE → DIAGNOSE (specialist read-only) → FIX (main agent เท่านั้น) → TEST (guard RED→GREEN) → REGRESS (subset ตามความเสี่ยง หรือ full ผ่าน `run_all_tests.py`) → SHIP (commit + archive + roadmap + 7 เอกสาร)
**ข้อยกเว้นเดียว:** จุดบกพร่อง**เดียวกัน**ที่ replicate หลายที่ = แก้ทุกจุด atomic ใน sprint เดียว (arc 6 จุด) — เพราะ partial fix เงียบคืออันตรายกว่า
**Halt:** regression แดงเกิน 1 retry → STOP ไม่ commit

## เสา 6 — มอบหมายแบบตรวจทานได้ + บันทึกตามจริง (Verified delegation, honest ledger)

**หลักการ:** specialist/agent เป็น **read-only** เสมอ — เสนอแผน main agent เป็นคนแก้; ทุก claim จาก agent ต้อง verify ก่อนใช้; ตัวเลขรายงานตามจริงแม้ไม่สวย

**หลักฐาน:**
- Triage หา 4 จุด → specialist ตรวจจริงเจอ **6 จุด** → ขยาย scope ตามหลักฐาน ไม่ยึดติด plan แรก
- LRU ลด heap แค่ **-18%** → บันทึกตามจริงพร้อมสาเหตุ (~600MB เหลืออยู่ระดับ doc) และ**โอนความรับผิดชอบ**ไป card ที่ถูกต้อง แทนการเคลมว่า "แก้แล้ว"
- โพรบเจอ "0/0 thumbs" → ไล่จนพบว่าเป็น artifact ของโพรบเอง ไม่ใช่บั๊กแอป → ปิดเป็น no-bug ไม่ file งานผี
**กลไก:** งานยาก/เสี่ยงใช้ model แรงขึ้น (Opus) เฉพาะขั้น DIAGNOSE/verify; เอกสาร 7 ไฟล์ update ทุก ship (demote-don't-delete → archive); สถานะ roadmap ต้องตรง git log เสมอ
**Halt:** ถ้า agent claim อะไรที่ verify แล้วไม่ตรง → ทิ้ง claim นั้น re-verify ทั้งชุด

---

## ผังรวม (ทุก sprint วิ่งตามนี้)

```
เสา1 วัด/ตรวจ ──> เสา2 file ──> เสา4 เช็ค contract ──> เสา6 specialist plan (verify!)
     ──> เสา5 fix (main agent) ──> เสา3 guard RED→GREEN + regression ──> เสา5 ship
     ──> เสา6 บันทึกตามจริง (archive + roadmap + 7 docs)
```

การจัดคิว: BROKEN (ตัวเลขผู้ใช้ผิด/ข้อมูลหาย) > CRASH-risk (memory/เสถียรภาพ) > perf ที่ผู้ใช้รู้สึก > FRICTION > invent (ต้องผ่าน RESEARCH→SPIKE→CHECKPOINT ห้ามเข้า dev loop ตรง)
