# Zen Mode + Command Palette

โหมดทำงานแบบ chrome-hide สำหรับงาน multi-page หนาๆ — ซ่อน ribbon / panel / status bar เพื่อให้ canvas ใหญ่ที่สุด พร้อม HUD มุมจอ + minimap หน้าทุกแผ่น + คีย์บอร์ดสลับหน้าเร็ว

> ใช้ได้ตั้งแต่ INV-2026-05-19-001a (Zen) + 001b (Palette) + 001c (polish)

## 1. เข้า / ออก Zen Mode

| Action | คีย์ / เมนู |
|---|---|
| เข้า Zen Mode | `F11` หรือ View menu → `⛶ Zen Mode` |
| ออก Zen Mode | `F11` ซ้ำ หรือ `Esc` |

เข้าโหมดแล้วจะ:
- ซ่อน menu bar / ribbon / left panel / right panel / status bar / summary widget
- ขยาย canvas เป็น ~94% ของความสูงจอ
- แสดง HUD 3 มุม + minimap ด้านข้าง
- บันทึก preference (`PREFS.layout.zenMode`) ค้างไว้ข้าม session

## 2. HUD 3 มุม (อ่านสถานะตอนวาด)

| มุม | แสดง |
|---|---|
| บน-ซ้าย (TL) | Scale chip + tool ปัจจุบัน |
| บน-ขวา (TR) | Objects count + active layer |
| ล่าง-ซ้าย (BL) | Save state (ดิสก์ / แก้ไขแล้ว) |

**Scale chip สี:**
- ⚪ ขาว = `manual` (สอบเทียบเองแล้ว เชื่อถือได้)
- 🟠 ส้ม = `auto-unverified` หรือยังไม่ตั้ง scale → hover ดู tooltip
- เตือนสายตาก่อนวาดเยอะแล้วต้อง recalibrate

**ชื่อหน้าใน HUD:** Format `ชื่อหน้า (N/total)` อ่านตรงจาก `pageNames[curPage]` (อัปเดตทันทีเมื่อสลับหน้าเร็วๆ ผ่าน minimap)

## 3. Sheet Minimap (5-col grid)

- แสดง thumbnail หน้าทุกแผ่นเป็น grid 5 คอลัมน์ ด้านข้าง
- **Lazy load:** ใช้ `IntersectionObserver` ต่อ cell — โหลด thumbnail เฉพาะที่ scroll เข้ามาในจอ (กันปัญหา `malloc failed` ใน PDF เยอะหน้า)
- คลิก cell → jump ไปหน้านั้น (HUD ชื่อหน้าอัปเดตทันที)
- หน้าปัจจุบันมีกรอบไฮไลต์

## 4. Command Palette (Ctrl+K)

ค้นหาและ jump หน้าด้วยคีย์บอร์ด — ใช้ได้ทั้งในและนอก Zen Mode

| Action | คีย์ |
|---|---|
| เปิด palette | `Ctrl+K` / `Cmd+K` หรือ View menu → `🔍 ค้นหาหน้า` |
| เลื่อนผลลัพธ์ | `ArrowUp` / `ArrowDown` |
| Jump | `Enter` |
| ปิด | `Esc` |

**ค้นได้ด้วย:**
- เลขหน้า (`12`, `45`)
- ชื่อหน้า (substring; e.g. `ชั้น 3`, `elev`)
- Tag ภาษาอังกฤษ: `site` / `plan` / `elev` / `section` / `detail`
- Tag ภาษาไทย: `ผังบริเวณ` / `ชั้น` / `รูปด้าน` / `รูปตัด` / `รายละเอียด` / `ตาราง`

**Tag chip สี** (ในผลลัพธ์): แต่ละหน้าโชว์ chip สีตาม tag (site / plan / elev / section / detail) — ระบุประเภทแบบได้เร็ว

**Empty-state hint (001c):** ถ้าพิมพ์คำไทยอย่าง `ผังบริเวณ` แล้วยังไม่มีผลลัพธ์ (เพราะหน้ายังไม่ได้ tag) จะขึ้น hint:

> 💡 แท็กภาษาไทยใช้ได้หลังตั้งค่าหน้าใน Page Setup

## 5. ข้อจำกัด / กฎความปลอดภัย

- **Mid-draw guard:** เปิด palette ไม่ได้ขณะกำลังวาด (`mPts.length > 0`) — กดปุ่มจะเงียบ ไม่ทำลายงานที่วาดค้าง
- **Scale gate (HT-7):** palette jump ไปหน้าที่ยังไม่ได้ตั้ง scale ก็ jump ได้ปกติ แต่ scale gate ของเครื่องมือวัดยัง enforce ตามเดิม
- **Z-index:** palette = 9500, ลอยอยู่เหนือ Zen HUDs (1500) — compose กันได้ไม่ทับ
- **Esc ใน Zen:** กด `Esc` ขณะ palette เปิด → ปิด palette เท่านั้น; กดอีกครั้งจึงจะออก Zen
- **คีย์บอร์ดในช่อง input อื่นๆ:** ArrowUp/Down/Enter/Esc ใน palette ทำงานก่อน `inInput` guard — ไม่โดน text field ดูด

## 6. Workflow แนะนำ

**สำหรับงาน 20+ หน้า:**

1. เปิด PDF → ตั้ง scale หน้าแรก
2. ไป Page Setup → tag หน้าทุกแผ่น (site/plan/elev/...) + ตั้งชื่อ
3. `F11` เข้า Zen Mode
4. `Ctrl+K` → พิมพ์ tag เช่น `plan` → Enter → ไปหน้าชั้นถัดไป
5. วาดเสร็จ → `Ctrl+K` อีกครั้ง → ข้ามไปหน้าอื่น
6. `F11` ออก Zen เมื่อต้องใช้ properties panel / summary widget

ดู Scale chip บน HUD ตลอด — ถ้า 🟠 ส้ม แปลว่าหน้านี้ scale ยังไม่ trust → ตั้งก่อนวาด

## 7. หน้าที่เกี่ยวข้อง

- [Keyboard Shortcuts](#manual/keyboard-shortcuts) — คีย์ลัดทั้งหมด
- [ตั้ง Scale](#manual/set-scale) — สำคัญก่อนเข้า Zen Mode
- [เครื่องมือวัด](#manual/measure-tools) — วาดอย่างไรใน Zen
