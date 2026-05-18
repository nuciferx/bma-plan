# เครื่องมือวัดทั้งหมด

BMA-Plan มีเครื่องมือวัด 8 ประเภท เลือกตามรูปร่างจริงของพื้นที่ที่ต้องการวัด

## 1. Polygon `⬡` (Area)

เครื่องมือพื้นฐาน — คลิกทีละจุด, กด `Enter` หรือคลิกซ้ำที่จุดแรกเพื่อปิดวง

- เหมาะกับ: ห้อง / อาคาร / ที่ดิน / open space
- คีย์ลัด: `A` (activate area tool)
- ระหว่างวาด: กด `A` อีกครั้งเพื่อทำ **arc edge** ของขอบถัดไป (3-click arc — ดู Arc-polygon ด้านล่าง)

## 2. Rectangle `▭`

คลิก 2 มุมตรงข้าม → polygon 4 จุดอัตโนมัติ

- เหมาะกับ: ห้อง orthogonal / ฐานเสา / ที่จอด
- คีย์ลัด: `Shift+R`

## 3. Circle `⭕`

คลิกจุดศูนย์กลาง → คลิกจุดบนขอบวงกลม → ระบบสร้าง 32-gon polygon

- เหมาะกับ: คันโยกวงเวียน / บ่อน้ำ / ฐานเสากลม
- คีย์ลัด: `Shift+C`
- เก็บ `shape:'circle' + center + radius` เพิ่ม → render ละเอียดด้วย `ctx.arc` analytic

## 4. Ellipse `⬭`

คลิก 2 มุมของ bounding box → ระบบสร้าง 32-gon ellipse polygon

- เหมาะกับ: รูปไข่ / ทางวงรี / สวนวงรี
- คีย์ลัด: `Shift+E`

## 5. Arc-polygon (3-click inline arc) ✨

**ใหม่ INV-001 (2026-05-17):** ภายในเครื่องมือ Polygon, กด `A` หลังเพิ่ม vertex อย่างน้อย 1 จุด → click จุดบนเส้นโค้ง (through-point) → click จุดถัดไป → edge นี้กลายเป็น arc

- เหมาะกับ: ขอบที่ดินโค้ง / กำแพงโค้ง / สวนน้ำพุ
- พื้นที่คำนวณ exact ด้วย closed-form circular segment formula (err < 0.001%)
- กด `Esc` กลางทางเพื่อยกเลิก arc-mode

## 6. Path / Continuous distance `〽`

คลิกหลายจุด → ระบบคำนวณ **ระยะรวม** ของเส้น (ไม่ใช่พื้นที่)

- เหมาะกับ: ระยะทางเดิน / ความยาวรั้ว / รอบรูปที่ดิน
- กด `Enter` จบ
- คีย์ลัด: `Shift+D`

## 7. Distance `📏`

คลิก 2 จุด → แสดงระยะตรง

- เหมาะกับ: ระยะถอยร่น (setback) / ระยะระหว่างเสา / ระยะ door swing
- คีย์ลัด: `D`

## 8. Marker `🚗` (Parking + site markers)

คลิกตำแหน่งเดียว → วาง marker (1 click = 1 unit)

- ประเภท: `parking`, `parking_disabled`, `parking_fire`, `parking_ambulance`, `entrance`, `aed`, `sign`, `fire_escape`, `fire_elevator`
- เหมาะกับ: นับ count (ไม่ใช่พื้นที่)
- คีย์ลัด: `P`

## Snap / สอย

ระหว่างวาด ระบบ snap อัตโนมัติไป endpoint (EP), midpoint (MP), center (CT), intersection (IX), close-polygon (close), perpendicular (PERP), nearest (NL).

- เปิด/ปิด snap ประเภท: คีย์ `E` `M` `C` ตามลำดับ (toggle EP/MP/CT)
- ตัวบ่งชี้ snap: สีและรูปสัญลักษณ์เปลี่ยนตามประเภท (กล่อง = EP, สามเหลี่ยม = MP, วงกลม+กากบาท = CT)

## Loupe `🔍` แว่นขยาย

- เปิด/ปิด: ปุ่ม `🔍` บน toolbar
- ปรับขนาด: ปุ่มขนาดข้างๆ
- ใช้ระหว่างวาด — ขยายบริเวณ cursor เพื่อ click จุดได้แม่นยำ

## Tips

- ใช้ `Shift` ค้างเพื่อ ortho-lock (มุม 0°/90°/180°/270°)
- ใช้ `Space` ค้างเพื่อ pan ชั่วคราว
- กด `Esc` กลางการวาดเพื่อยกเลิก
- กด `Ctrl+Z` ระหว่างวาด → undo จุดล่าสุด (ไม่ใช่ undo object)
