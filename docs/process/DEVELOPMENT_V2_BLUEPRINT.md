# DEVELOPMENT_V2_BLUEPRINT.md — วิธีการพัฒนารุ่นถัดไป (ดีกว่าที่ทำอยู่)

Date: 2026-07-02
Status: proposed blueprint — ต่อยอดจาก `DEVELOPMENT_PILLARS.md` (6 เสายังคงเป็นฐาน ไม่ยกเลิก)
วิธีออกแบบ: วิจารณ์ระบบปัจจุบันด้วยหลักฐานจริง → แก้ทีละจุดอ่อนเชิงโครงสร้าง ไม่ใช่เพิ่มกติกา

---

## Part 1 — จุดอ่อนจริงของระบบปัจจุบัน (พร้อมหลักฐาน)

| # | จุดอ่อน | หลักฐานจากงานจริง |
|---|---|---|
| W1 | **ตั้งรับ ไม่ป้องกัน** — จับบั๊กหลังมันเกิด (audit/hunt) ไม่กันตั้งแต่ออกแบบ | บั๊ก arc/CFSS อยู่ในระบบมาหลายสัปดาห์ รอด 60 เทสต์ เพราะ invariant "ยอดรวม = Σ ป้าย" **ไม่เคยถูกประกาศตอนสร้าง rollup** — ถ้ามีตั้งแต่แรก บั๊กทั้งสองเกิดไม่ได้เลย |
| W2 | **เทสต์แพงขึ้นเชิงเส้น** — ทุกไฟล์ boot uvicorn+Chromium ของตัวเอง | 67 ไฟล์ ≈ 9-10 นาที/รอบเต็ม; full run ถูก kill กลางคัน 2 ครั้งวันนี้จนต้องใช้ subset แทน; เทสต์คณิตล้วนอย่าง parity ก็แบก browser boot ไปด้วย |
| W3 | **เอกสารซ้ำซ้อน 7 ไฟล์/sprint** | sprint-writer ใช้ ~180-240K tokens ต่อ finalize × 3-4 รอบ/วัน; log/PATCH_SUMMARY/TEST_RESULT/FINAL_REPORT เนื้อหาทับกัน ~70%; ความจริงทั้งหมดมีอยู่แล้วใน commit message |
| W4 | **Roadmap เป็น append-only swamp** | PHASE_INDEX 178KB+; แถว lpm-1..9 ค้าง `queued` ทั้งที่ fixed ไปแล้ว (drift กับ bug-archive/git); ยิ่งโต ยิ่งอ่านแพง ยิ่ง drift ง่าย |
| W5 | **ความรู้ในเอกสาร/คอมเมนต์เน่าเงียบ** | CLAUDE.md บอก 21 markers ของจริง ~110; คอมเมนต์ `page-rotate.js` อ้าง "server ?rot=N" ซึ่งไม่จริงแล้ว และ**เกือบพา patch plan ของ pageRot หลงทาง** |
| W6 | **ไม่มี feedback จากผู้ใช้จริง + ไม่มี release discipline** | เทสต์ทั้งหมด self-generated; ไม่มี version/tag/CHANGELOG; commit ตรง main ไม่มี CI gate (runner เพิ่งมีแต่ยังไม่บังคับ) |

## Part 2 — การออกแบบรุ่นใหม่ (6 upgrades แก้ตรงจุดอ่อน)

### U1. Invariant-first development (แก้ W1) — เปลี่ยนจากไล่จับเป็นกันเกิด
- สร้าง **`lite/tests/INVARIANTS.md` — ทะเบียน invariant กลาง** เริ่มจากที่พิสูจน์แล้วว่าจับบั๊กได้: "ทุก rollup == Σ ค่าป้าย object", "area ไม่แปรตาม rotation/translation/vertex-order", "save→load→save = byte-stable", "export == สิ่งที่เห็นบนจอ", "ทุก consumer ของ object ต้องรองรับทุก kind (poly/instance/…)"
- **กติกาใหม่ตอน SCOPE:** ทุกฟีเจอร์ต้องตอบ 2 ข้อก่อนเขียนโค้ด — (a) แตะ invariant ตัวไหน → เพิ่มตัวเองเข้าเทสต์ invariant นั้น (b) สร้าง "ชนิดข้อมูล/consumer ใหม่" ไหม → ถ้าใช่ ต้องไล่ตาราง consumer ให้ครบตั้งแต่วันแรก (บทเรียน CFSS: instance เกิดใหม่แต่ 6 consumers ไม่มีใครรู้จัก)
- ฟีเจอร์ประเภท "ค่าที่ผู้ใช้เห็น" default ต้องมี property-based หรือ metamorphic test ไม่ใช่แค่ example-based

### U2. Test pyramid + impact map (แก้ W2) — เร็วขึ้น 10 เท่าโดย coverage เท่าเดิม
- แบ่ง 4 tier: **T0** คณิตล้วนรันใน Node (parity/pbt/invariant-math — เป้า <5 วิทั้งชุด, วันนี้แบก browser อยู่ฟรีๆ) / **T1** server endpoint ผ่าน requests ไม่มี browser / **T2** Playwright UI / **T3** journey+sandbox ไฟล์จริง
- **Shared-harness สำหรับ T2:** boot uvicorn+Chromium ครั้งเดียว รันหลาย test module ต่อ (ตัด ~10 วิ/ไฟล์ × 50 ไฟล์)
- **Impact map ใน runner:** ตารางไฟล์→เทสต์ (`measure-engine.js` → T0 ทั้งหมด+arc; `page-renderer.js` → render suite; `server_lite.py` → T1+journey) → `run_all_tests.py --changed` รันเฉพาะที่กระทบ + T0 เสมอ; full 4-tier เหลือไว้ pre-release
- เป้าเวลา: dev loop ปกติ <1 นาที, pre-release ~10 นาที

### U3. Ledger-first docs (แก้ W3) — เขียนครั้งเดียว generate ที่เหลือ
- **`SHIPS.jsonl`** เป็น single source of truth ต่อ ship: `{id, date, commits[], problem, fix, evidence{red,green,numbers}, guard_test, regression, files}` — เติมตอน SHIP ในไม่กี่บรรทัด (ข้อมูลเดียวกับ commit message)
- เอกสารมนุษย์ลดเหลือ **2 ไฟล์เขียนมือ**: `log.md` (บริบท/เหตุผล/บทเรียน — สิ่งที่ ledger เก็บไม่ได้) + `CURRENT_STATUS.md` (one-liner) — ส่วน PATCH_SUMMARY/TEST_RESULT/FINAL_REPORT/LATEST_STATUS **generate จาก ledger** ด้วยสคริปต์ ไม่ใช่ agent 200K tokens
- ประหยัดจริง: ~150-200K tokens/finalize × ทุก sprint

### U4. Roadmap ที่ reconcile ตัวเอง (แก้ W4)
- แยก `PHASE_INDEX.md` → **`ROADMAP_ACTIVE.md`** (เฉพาะ queued/in-progress, เป้า <15KB) + `ROADMAP_DONE.md` (append-only archive)
- สคริปต์ `reconcile_roadmap.py` ใน preflight ของ runner: เทียบสถานะแถว vs git log + bug-archive → รายงานแถวโกหก (แบบ lpm-1..9) อัตโนมัติ

### U5. Executable truth (แก้ W5) — เอกสารที่โกหกไม่ได้
- ข้อเท็จจริงที่อ้างในเอกสาร ต้องมี assertion ตรวจ: จำนวน marker, line caps, "ไฟล์นี้ vendored byte-identical", สถานะ card — เข้า `run_all_tests.py` preflight (ต่อยอด doc-drift ที่มี `bma-doc-auditor` อยู่แล้วให้เป็นอัตโนมัติแทน quarterly)
- คอมเมนต์เชิงสถาปัตยกรรมที่สำคัญ (แบบ ?rot=N ที่เน่า) → ย้ายข้อเท็จจริงไปอยู่ในเทสต์ที่ fail เมื่อไม่จริง แทนที่จะอยู่ในคอมเมนต์

### U6. Release + real-user loop (แก้ W6)
- **Release ritual:** tag `lite-vX.Y` + CHANGELOG (generate จาก SHIPS.jsonl) + full 4-tier + `/lite-sandbox-test` ไฟล์จริงทุกตัว ก่อน build แจกทุกครั้ง
- **Golden real-project acceptance:** เลือกโปรเจกต์ลูกค้าจริง 1-2 ไฟล์ วัดครบ flow เก็บเป็น `.bmaplan` + ค่า m² ที่ถูกต้อง → เทสต์ T3 เปิด/คำนวณ/export เทียบ golden ทุก release (จับ regression แบบที่ synthetic ไม่มีวันเจอ)
- **Dogfood ritual รายสัปดาห์:** ใช้แอปวัดงานจริง 30 นาที → finding เข้า `/bma-bug-report` — แทน telemetry ที่ Phase 1 ไม่มี

## Part 3 — ลำดับ migration (ทำเป็น sprint ปกติ ไม่หยุดงาน feature)

1. **U2-T0 แยกเทสต์คณิตเป็น Node tier** — ผลตอบแทนเร็วสุด (parity/pbt วิ่ง <5 วิ) [sprint เดียว]
2. **U1 INVARIANTS.md + กติกา SCOPE ใหม่** [ครึ่ง sprint — เอกสาร + เพิ่มเข้า checklist]
3. **U4 แยก ROADMAP_ACTIVE + reconcile script** [sprint เดียว — แก้ swamp ทันที]
4. **U3 SHIPS.jsonl + generator** [sprint เดียว ประหยัด token ทุก sprint หลังจากนั้น]
5. **U2 shared-harness + impact map** [1-2 sprint]
6. **U5 + U6** [ทยอย — release ritual เริ่มได้ตั้งแต่ build แจกครั้งหน้า]

หลักตัดสินว่ารุ่นใหม่ "ดีกว่า" จริง (วัดได้): บั๊กคลาสซ้ำ (consumer ลืม kind ใหม่) ต้องเกิดไม่ได้อีก / dev-loop test <1 นาที / token ต่อ finalize ลด >70% / แถว roadmap โกหก = 0 / ทุก release มี golden real-project ผ่าน
