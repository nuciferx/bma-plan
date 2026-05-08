# RUN_PROJECT_SETUP_UI.md — BMA-Plan Project Setup / Page Management UI

## Goal

Build a clean Project Setup / Page Management screen before the measurement canvas.

The purpose is to help users:
1. review all PDF pages,
2. name pages,
3. categorize pages,
4. enter project/building information,
5. start measurement only when ready.

## Design Reference

Use the new UI design direction:
- modern dark theme
- left project information panel
- central page management grid
- top summary chips
- clear green “เริ่มวัด” button
- no measurement canvas on this screen
- no duplicated layer controls

## Scope

Do:
1. Add a Project Setup screen/state after PDF upload and before measurement.
2. Show project info form:
   - เลขที่โครงการ
   - ประเภทอาคาร
   - ลักษณะงาน
   - จำนวนชั้น
   - GFA รวม (ตร.ม.)
   - จำนวนหน่วย
3. Show page cards for every PDF page:
   - thumbnail
   - page number
   - page name field
   - category dropdown
   - remove/exclude button if already supported; otherwise hide/remove button.
4. Add category options:
   - ผังบริเวณ
   - ชั้น
   - รูปด้าน
   - รูปตัด
   - รายละเอียด
   - ตาราง
   - อื่น ๆ
5. Add summary chips:
   - ทั้งหมด
   - จัดหมวดหมู่แล้ว
   - ยังไม่จัดหมวดหมู่
   - count by category
6. Add “ตั้งชื่ออัตโนมัติทุกหน้า” MVP:
   - simple rule-based default naming
   - no OCR
   - no AI
7. Add green “เริ่มวัด” button:
   - transitions to measurement canvas
   - preserves pageMeta and projectInfo
8. Store projectInfo and pageMeta in the existing project state/save-load structure if possible.
9. Update XLSX Cover sheet to include projectInfo if safe.
10. Update tests.

## Forbidden

Do not add:
- OCR
- AI checker
- legal rules
- Rule Engine
- FAR/OSR/setback logic
- K.1 generation
- Project PDF Save/Load
- large backend rewrite

Do not break:
- PDF upload
- page thumbnail rendering
- measurement canvas
- manual scale
- drawing area/opening
- overlapping picker
- layer lock
- properties panel
- XLSX export
- .bmaplan save/load

## Acceptance Criteria

Pass only if:
1. After opening PDF, user sees Project Setup screen first.
2. All pages appear as cards.
3. User can edit page name.
4. User can select page category.
5. Summary chips update.
6. Auto naming fills page names/categories.
7. Start measuring button opens measurement canvas.
8. Measurement workflow still works.
9. projectInfo/pageMeta persist in save/load if safe.
10. py_compile, smoke, full pass.
11. Scope grep finds no legal/OCR/AI/Rule Engine.

## Tests

Run:
python -m py_compile proto/server.py proto/e2e_ui_test.py
python proto/e2e_ui_test.py smoke
python proto/e2e_ui_test.py full

Scope grep:
rg -n "ZONE_RULES|runCheck|FAR|OSR|Rule Engine|OCR|AI checker|ข้อ 41|ข้อ 50|ผังเมือง" proto/ui.html proto/server.py

## Output

Update:
- PATCH_SUMMARY.md
- TEST_RESULT.md
- UI_MANUAL_TEST.md
- FINAL_REPORT_FOR_CHATGPT.md
- log.md



## Visual Design Requirements

Follow the approved mockup direction.

The Project Setup screen should visually look like a polished dark desktop app, not a raw form.

### Top Bar

Use a clean top bar with:
- BMA-Plan logo/name on the left
- screen title: ตั้งค่าโปรเจกต์
- loaded PDF filename on the right
- secondary button: บันทึก
- primary green button: เริ่มวัด ▶

### Left Project Panel

Make the left sidebar a clean card-like panel.

Use grouped sections:
1. ข้อมูลโครงการ
2. ข้อมูลอาคาร
3. การตั้งชื่อและจัดหมวดหมู่

Use:
- clear section headers
- icons if already available or simple text labels
- consistent input height
- better spacing
- collapsible-looking section headers if safe
- one clear blue button at the bottom: ตั้งชื่ออัตโนมัติทุกหน้า

Do not make the form cramped.

### Main Page Management Area

The main area should have:
- title: จัดการหน้า
- summary chips row at the top
- search box: ค้นหาหน้า...
- filter button: ตัวกรอง
- responsive grid of page cards

### Summary Chips

Use horizontal cards/chips for:
- ทั้งหมด
- จัดหมวดหมู่แล้ว
- ยังไม่จัดหมวดหมู่
- ผังบริเวณ
- ชั้น
- รูปด้าน
- รูปตัด
- รายละเอียด
- ตาราง

Each chip should show count clearly.

### Page Cards

Each page card should be visually consistent:
- thumbnail area
- small remove/exclude button only if functional
- page number centered under thumbnail
- page name input
- category dropdown with colored dot
- clear selected/focused state

Cards should not be too small or too tightly packed.

### Footer Status

Add a slim bottom status/tip bar:
- left: เคล็ดลับ about auto naming / category editing
- right: บันทึกอัตโนมัติแล้ว + time if safe

### Visual Quality

Use:
- dark background
- subtle borders
- rounded panels
- blue accent for selected/primary setup controls
- green accent for start measuring
- enough padding and spacing

Avoid:
- cramped controls
- huge empty black area
- duplicated controls
- fake buttons
- measurement canvas showing before clicking เริ่มวัด