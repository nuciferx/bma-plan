# INVENT — page-manager-redesign

Date: 2026-08-10 · Pipeline: `/lite-invent` (7 เฟสเต็ม) · Status: **awaiting human CHECKPOINT (GO / NOGO / RESHAPE)**

## 1. PICK

User field report: เปิด Page Manager (⇧F12) แล้วเผลอคลิกนอก panel → ปิดทันที หลุดไปหน้า PDF → state เลเยอร์ (ที่ตามหน้า) เปลี่ยนกลางคัน งานเลือก/ติดแท็กเสีย context · ขอวิจัยใหม่ทั้งตัว: การเลือก/แท็กต้องมี "วินัย" และแก้ง่าย
โค้ดยืนยันบั๊กจริง: `page-manager-ui.js:126-128` (backdrop=ปิดทันที ไม่เช็ค pending), `:226-231` (คลิก tile=กระโดดหน้า+ปิด), `:279` (confirm ลบเปล่าๆ), `:492` (ไม่มี PDF → return เงียบ)

## 2. RESEARCH (bma-researcher) — verdict `PRIOR_ART_PARTIAL`

- **Incumbent ทั้ง 5 ราย (Acrobat Organize Pages / Bluebeam / Foxit / Preview / PDF Expert) ไม่มีใครใช้ dismissable modal กับงานจัดการหน้า** — ใช้ full-screen mode ที่ออกด้วยเจตนา หรือ docked panel ถาวร ทั้งหมด
- NN/g: click-outside-close ห้ามใช้กับจอที่ถือ unsaved/destructive state · Raskin: mode ต้องมองเห็นได้ — pending journal ของ lite วันนี้คือ "โหมดล่องหน"
- คำตัดสินเก่าที่ล็อกไว้ (ต้องเคารพ): pending journal + Apply ceremony (approach D, INV-2026-05-29-LPM), ปิดโดยไม่ Apply = PDF เดิมไม่ถูกแตะ, undo stack มีแล้ว, bulk-tag bar + shift-select ship แล้วใน wizard grid, JIT per-page gate แทน hard gate แล้ว (INV-2026-07-04-002)

## 3. FRAME — Eval 3 เคส (รันได้จริง)

1. happy: multi-select → bulk tag → reorder → Apply → ลำดับ+tag ถูก + canvas sync
2. edge (อุบัติเหตุที่รายงาน): มี pending → คลิก backdrop → **ไม่ปิด ไม่ navigate, pending คงอยู่, active layer ไม่เปลี่ยน**
3. adversarial: Esc+pending → เตือน · ลบหน้ามีงานวัด → confirm บอกจำนวนชิ้น · เปิดตอนไม่มี PDF → hint มองเห็นได้

## 4-5. DIVERGE + SCORE (bma-inventor) — 5 แนวทาง

| # | แนวทาง | คะแนน |
|---|---|---|
| A | เสริมเกราะ modal เดิม (guard backdrop/Esc + confirm มีข้อมูล) ~45 บรรทัด | 24 |
| B | sidebar ถาวรแบบ Bluebeam (Browse/Organize toggle) | 22 |
| C | **= mockup ศูนย์หน้า**: full-screen รวม F12+⇧F12 | 20 (blast radius ใหญ่: รวม 2 จอที่มี test 4+ ไฟล์ บน headroom 11 บรรทัด) |
| **D** | **ปลด wizard auto-open+hard-lock → JIT banner บน canvas + เสริมเกราะ PM เดี่ยว (กลไกเดียวกับ A)** | **25 ← ชนะ** |
| E | session-chip: pending แยกจากการเปิด/ปิด overlay (ติด status bar) | 24 (novel สุด แต่ตีความ eval เคส 3 ใหม่ — ไม่ผ่านตามตัวอักษร) |

จุดขายของ D: **ปิด BUG-20260810 เชิงโครงสร้าง** (ไม่มี wizard เด้งล็อก = ไม่มีตัวกลืน ⇧F12) ไม่ใช่ patch ซ้อน patch · reuse ของที่ ship แล้วทั้งสองฝั่ง (bulk-bar ของ wizard grid คงอยู่เป็นเครื่องมือกดเรียกเอง, pending engine ของ pageMgr ไม่แตะ) · net impact ต่อเพดาน ui-lite.html ≈ 0 (โมดูล self-inject)
Fallback: A (ship เกราะอย่างเดียวได้ในวันเดียว ถ้า D ถูกตัดสินว่าแรงไป)

## 6. SPIKE — ผล: **ALL PASS 14/14**

Artifact: `lite/sandbox/invent-page-manager-redesign/spike.html` (self-verifying, รันแล้วผ่าน headless Chromium 2026-08-10)
- CASE 1 happy 4/4 · CASE 2 edge 5/5 (backdrop click ขณะ pending: overlay ไม่ปิด, pending อยู่, curPage/activeLayer ไม่ขยับ, มีแถบเตือน) · CASE 3 adversarial 5/5 (Esc เตือน / confirm บอก "งานวัด 3" / no-PDF hint / JIT banner แทน lock / jitTag ติดหน้าถูก)
- กลไกสำคัญที่พิสูจน์: backdrop + Esc + ✕ วิ่งเข้า `tryClose()` **ช่องเดียว** ที่ guard ด้วย `pending.length` — เคส 2 ผ่าน "โดยโครงสร้าง" ไม่ใช่ patch รายจุด

## 7. CHECKPOINT — คำถามถึง human

1. **คำถามนโยบาย (หัวใจของ D — spike ตอบแทนไม่ได้):** ยอมรับการ**ปลด wizard เด้งอัตโนมัติ + hard-lock ตอนเปิดไฟล์**หรือไม่? (แทนด้วย JIT banner: แตะวัดบนหน้าไม่มีป้าย → banner ติดป้ายตรงนั้น ไม่ล็อกทั้งแอป) — ผู้ใช้ที่ชิน "wizard บังคับ tag รวดเดียว 45 หน้า" ยังกด F12 เรียกจอ tag เดิมได้เอง แค่ไม่ถูกบังคับ
2. ถ้า GO D: sprint แตกเป็น 3 slice — (i) เกราะ PM (guard+confirm+hint ~45 บรรทัด, ยก confirm widget จาก mockup ศูนย์หน้า), (ii) JIT banner (`canvas-tag-banner.js` ~70 บรรทัด ตาม spec ใน lite-page-tagging-workflow), (iii) ปลด auto-open/lock ใน wiz-auto (−~110 บรรทัด) + อัปเดต test wizard-auto-open — ทุก slice ผ่าน `/bma-lite-dev` + guard test RED ก่อน
3. ถ้าไม่เอาการปลด wizard: **RESHAPE → A** (เกราะอย่างเดียว ~45 บรรทัด ปิดอาการที่รายงานครบ แต่ BUG-20260810 ต้อง fix แยกอีกดอก)
4. หมายเหตุ: mockup ศูนย์หน้า (แนวทาง C) ไม่ตาย — เก็บเป็นวิสัยทัศน์ระยะยาว ถ้าวันหน้าอยากรวมจอค่อยเปิด invent ใหม่เมื่อ headroom พร้อม

## Decision

**GO แนวทาง D** (user, 2026-08-10 — "go ทั้งสองตัว delegate เอเจนต์ให้เหมาะสม") — build 3 slices ผ่าน /bma-lite-dev
หมายเหตุ orchestrator: JIT gate มีอยู่แล้วในรูป `tag-jit.js` (ship แล้ว INV-2026-07-04-002) — slice 2 จึงเป็นการ**แก้บั๊กที่รู้แล้วของ tag-jit** (banner ปิด closure หน้าเก่า + `__jitWrapped` ตั้งก่อน wrap สำเร็จ) ไม่ใช่สร้าง `canvas-tag-banner.js` ใหม่ซ้ำซ้อนตามที่ inventor ร่างไว้
