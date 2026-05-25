# Invent — Per-page-setup folder layer tree (lite)

- **Date**: 2026-05-25
- **Status**: spike (`invent-in-progress`)
- **Sandbox**: `lite/sandbox/invent-page-folder-layers.html`
- **Combines**:
  - `lite/sandbox/invent-layer-dnd.html` (DnD Approach A, scored 26/30)
  - `lite/sandbox/invent-45page-permit-spike.html` (45-page permit dataset)
- **PHASE_INDEX**: `## Discovered backlog → ### ideas 2026-05-25`
- **Idea source**: user 2026-05-25 — "ในแต่ละแผ่น = ชั้นที่ setup จะมีโฟลเดอร์แต่ละชั้นของ pagesetup ในแต่ละโฟลเดอร์จะมี layer พื้นฐาน และสามารถเพิ่มเลเยอร์ในแต่ละโฟลเดอร์ได้"

## หลักการ

**Per-page-setup folder** แทน role-based folder
- 1 folder = 1 page setup (ผังบริเวณ / ชั้น 1 / ชั้น 2 / … / ดาดฟ้า)
- Site pages ที่ตั้งใจคู่กัน (p5,7,8 = "ผังบริเวณ" เดียวกัน) → รวมเป็น 1 folder ผ่าน `siteGroup`
- Floor pages → 1 folder per floor (p11→ชั้น 1, p12→ชั้น 2, …, p16→ดาดฟ้า)
- ไม่นับเข้าคำนวณ (cover/legend/section/detail/schedule) → 1 folder รวม "🚫 ไม่นับเข้าคำนวณ" (collapsed by default)

แต่ละ folder มี **base layer auto-preset ตาม tag**:

| Folder | Base layers |
|---|---|
| 📐 ผังบริเวณ (site) | ที่ดิน · พื้นที่อาคารปกคลุม · แนวร่น |
| 🏢 ชั้น N (floor) | GFA ชั้น N · หักช่องลิฟต์ · หักช่องบันได · ห้องพัก/lobby |
| 🏗️ ดาดฟ้า (roof) | GFA ดาดฟ้า · อุปกรณ์บนดาดฟ้า |

แต่ละ folder มีปุ่ม **+ เพิ่ม layer** เปิด dialog (ชื่อ / role / สี) สำหรับ layer custom (เช่น "พื้นที่ระเบียง" ที่มีเฉพาะชั้น 2)

## ทำไมดีกว่า role-based folder

| มุม | role-based (เดิม) | page-folder (ใหม่) |
|---|---|---|
| โมเดลความคิดผู้ใช้ | "GFA / Deduction / Use" | "ชั้น 1 / ชั้น 2 / ผังบริเวณ" — ตรงกับวิธีคิดสถาปนิก |
| ค้น layer ของชั้นใดชั้นหนึ่ง | ต้องเปิดทุก folder + ดู "↳ p11" tag | เปิด folder ชั้นนั้น เห็นทั้งหมดในนั้น |
| เพิ่ม layer เฉพาะชั้น | ไม่ตรงไหน — ต้อง global pool + manual page binding | กดปุ่ม + ใน folder ชั้นนั้นได้ทันที |
| Cross-floor consistency | ทำได้แต่ไม่เห็นชัด | DnD ย้าย "หักช่องลิฟต์" จากชั้น 2 → ชั้น 3 เห็นย้ายชัด |
| มี active page indicator | ยาก (layer ผูก ≥ 1 หน้า) | คลิก folder = highlight pages ในขวาทันที |

## DnD (ยืม UX จาก `invent-layer-dnd.html`)

- ลาก `⠿` grip → ghost ติดเมาส์
- 3 drop zone ต่อแถว:
  - top 30% → blue line = insert before
  - bottom 30% → blue line = insert after
  - middle 40% บน folder = nest เข้า folder (green inset)
- Layer ห้ามไป root (ต้องอยู่ใต้ folder) — log warning
- Folder ห้าม nest ใต้ folder (sandbox-only restriction; เปิดได้ภายหลัง)
- Keyboard mode: ↑↓ focus / ⇧↑↓ reorder / → nest / ← outdent

## Open questions (รอผู้ใช้ตัดสิน)

1. **Site grouping** — ตอน spike นี้รวม p5,7,8 เป็น 1 folder "ผังบริเวณ" ผ่าน `siteGroup:'site-main'`. ถ้า project มี site 2 ชุด (เช่น lot A + lot B) ผู้ใช้ตั้งกลุ่มยังไง?
   - (a) auto-detect จาก scale ใกล้กัน?
   - (b) ผู้ใช้กดเลือกเอง ใน page-setup wizard?
   - (c) default = 1 site = 1 folder, ผู้ใช้ลากรวมเองภายหลัง?
2. **Cross-floor shared layer** — "หักช่องลิฟต์" ทุกชั้นมี:
   - (a) **copy-per-floor** (ปัจจุบันใน spike) — แก้ทีละชั้น เห็นง่ายแต่หลุดได้
   - (b) **symlink instance** — 1 layer master + reference ในทุก folder, แก้ที่เดียวเปลี่ยนทั่ว
   - (c) **"shared" sub-folder ด้านบน** — folder กลางสำหรับ layer ข้ามชั้น (lift shaft / stair core)
3. **Folder DnD between folders** — ตอนนี้ปิดไว้. ถ้าเปิด:
   - ย้าย "ชั้น 2" ขึ้นก่อน "ชั้น 1"? ไม่ make sense (ลำดับชั้นถูก lock โดย floor number)
   - หรือยอมให้ย้ายแค่ folder "site" / "ไม่นับ" / custom?
4. **Schema impact ใน lite จริง** — ปัจจุบัน `LAYERS[]` เป็น global. ถ้า adopt model นี้:
   - เพิ่ม `layer.pageSetupId` (FK ไป folder)
   - หรือ refactor เป็น `pageSetup[].layers[]` (per-page-setup ownership)
   - หลังถูก compatible — แต่ต้อง migrate `.bmaplan` ที่บันทึกแบบเดิม

## Forbidden-surface profile (ถ้า promote เข้า lite จริง)

- `lite/static/js/measure-engine.js` — ไม่แตะ (layer ≠ measurement math)
- `RS`, `pdfToC`/`cToPdf` — ไม่แตะ (panel-only)
- `.bmaplan` schema — **กระทบ** (เพิ่ม `pageSetupId` ใน layer); ต้องเขียน migration (additive only — ของเก่าเปิดได้)
- `lite/ui-lite.html` — กระทบ (replace layer panel; HTML+JS เปลี่ยน)
- `lite-tests/*` — ต้องเพิ่ม marker `LITE_PAGE_FOLDER_LAYER_OK`

ระดับ risk: **MEDIUM** (schema migration + UI replacement, ไม่ใช่ measurement math)

## Next step

1. ผู้ใช้รีวิว spike → ตอบ 4 open Qs ด้านบน
2. ถ้า GO → `/bma-invent` หรือ `/bma-lite-dev` (ขึ้นกับว่าต้องการ explore เพิ่ม หรือพร้อมทำ implementation slice แล้ว)
3. ถ้า RESHAPE → กลับมา iterate ที่ spike นี้
