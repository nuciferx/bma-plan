# BMA-Plan Session Continuation

อัปเดต: 2026-04-25

ไฟล์นี้ใช้สำหรับย้ายไปคุยต่อในเครื่องอื่นหรือแชตใหม่ โดยไม่ต้องไล่ context ทั้งหมดจากต้นทาง

## Current Project Location

```text
F:\drives\My Drive\01 project\ai\bma-plan
```

โปรแกรมหลักอยู่ใน:

```text
F:\drives\My Drive\01 project\ai\bma-plan\proto
```

## Current Running App

ตอนนี้ server รันอยู่ที่:

```text
http://localhost:8001/
```

Process ที่รันล่าสุด:

```powershell
Stop-Process -Id 13724
```

ถ้าจะรันใหม่:

```powershell
cd "F:\drives\My Drive\01 project\ai\bma-plan\proto"
python server.py
```

หมายเหตุ: `server.py` ปัจจุบันรันที่ port `8001` แต่เอกสารเก่าบางไฟล์ยังอ้าง `8000`

## Files Created/Updated In This Session

ไฟล์ที่เพิ่มใน session นี้:

- `AGENTS.md` - กติกาบังคับก่อนพัฒนา อ่านเอกสารและวางแผนก่อนแก้โค้ด
- `DEVELOPMENT_PLAN.md` - แผนพัฒนาระยะต่อไปของโปรเจกต์
- `UI_REGRESSION_REPORT.md` - รายงานเทียบ UI ใหม่กับเวอร์ชันก่อนหน้า
- `SESSION_CONTINUATION.md` - ไฟล์นี้ สำหรับย้าย session ไปคุยต่อ

## Required Reading In New Session

ให้เริ่มด้วยการอ่านไฟล์เหล่านี้ตามลำดับ:

1. `AGENTS.md`
2. `SESSION_CONTINUATION.md`
3. `UI_REGRESSION_REPORT.md`
4. `proto/STATUS.md`
5. `PROGRESS.md`
6. `BMA_PLAN_V2_SCOPE.md`
7. `HANDOFF.md`
8. Source ที่เกี่ยวข้องกับงาน:
   - `proto/server.py`
   - `proto/ui.html`
   - `proto/server.py.bak`
   - `proto/e2e_ui_test.py`

## Latest Decision

ผู้ใช้ทดสอบ UI ใหม่แล้วพบว่าใช้งานสู้ UI เดิมไม่ได้ โดยเฉพาะ:

- engine/flow การอ่าน PDF
- การ zoom เข้าออก
- ไม่มี scroll mouse zoom
- snap/measurement workflow รู้สึกแย่กว่าเดิม

ตรวจโค้ดแล้วพบ regression จริง:

- `proto/ui.html` ไม่มี `ws.addEventListener("wheel", ...)`
- `snap()` ใน UI ใหม่ไม่มี IX snap block
- `perpMode` มีปุ่ม แต่ไม่มี PERP snap logic
- `snapRadius` และ `closeRadius` ไม่ scale ตาม zoom
- `Opening mode` ผูกกับ `perpMode` ผิด ควรแยก `openingMode`

ข้อสรุป:

> ห้าม revert backend ทั้งก้อนไป commit เก่า เพราะ backend ปัจจุบันดีกว่า ให้รักษา `proto/server.py` ปัจจุบันไว้ แล้วนำ interaction/UI behavior จาก `proto/server.py.bak` กลับมาแก้ใน `proto/ui.html`

## Recommended Next Work

ลำดับแก้ที่ตกลงกัน:

1. คืน mouse wheel zoom และ zoom ที่ตำแหน่ง cursor
2. แก้ snap radius และ close polygon radius ให้หารด้วย `zoom`
3. คืน IX snap logic
4. คืน perpendicular snap logic และ `perpFoot()`
5. แยก `openingMode` ออกจาก `perpMode`
6. ทดสอบกับ real permit PDF

เริ่มจากข้อ 1-2 ก่อน เพราะแก้ง่าย กระทบต่ำ และเห็นผลกับ UX ทันที

## Source Of Truth For UI Fixes

ใช้ `proto/server.py.bak` เป็นแหล่งอ้างอิง interaction เดิมที่ดีกว่า:

- wheel zoom: ประมาณบรรทัด `2356`
- snap radius zoom-corrected: ประมาณบรรทัด `1632`
- IX snap: ประมาณบรรทัด `1672`
- PERP snap: ประมาณบรรทัด `1691`
- `perpFoot()`: ประมาณบรรทัด `1729`
- tool toggle/status: ประมาณบรรทัด `2388`

ไฟล์เป้าหมายที่ควรแก้:

```text
proto/ui.html
```

ไม่ควรแก้ backend ถ้าไม่ได้จำเป็น:

```text
proto/server.py
```

## Current Git/Repo Notes

ใน `proto` มี `.git` แยกจาก root project

สถานะที่พบล่าสุด:

- `proto/server.py` modified
- `proto/STATUS.md` modified
- `proto/launch.py` modified
- `proto/requirements.txt` modified
- `proto/ui.html` ยังเป็น untracked file
- build artifacts เช่น `proto/build/`, `proto/dist2/` ไม่ควรแตะ เว้นแต่ทำ release

ข้อควรแก้ก่อน release:

- เพิ่ม `proto/ui.html` เข้า repo ไม่งั้น deploy แล้วเว็บจะหา UI ไม่เจอ
- เพิ่ม `xlsxwriter` ใน `proto/requirements.txt` ถ้า Export XLSX เป็น feature หลัก
- จัด port docs ให้ตรงกันระหว่าง `8000`/`8001`
- `opencode.json` มี API key plaintext ต้อง rotate และย้ายไป env var

## Verification Commands

หลังแก้ interaction ให้รันอย่างน้อย:

```powershell
cd "F:\drives\My Drive\01 project\ai\bma-plan"
python -m py_compile proto/server.py proto/e2e_ui_test.py
```

ถ้าแก้ behavior UI สำคัญ ให้เปิด server แล้วทดสอบด้วย browser:

```powershell
cd "F:\drives\My Drive\01 project\ai\bma-plan\proto"
python server.py
```

เปิด:

```text
http://localhost:8001/
```

ถ้าแตะ export, rotation, persistence, หรือ session isolation:

```powershell
cd "F:\drives\My Drive\01 project\ai\bma-plan"
python proto/e2e_ui_test.py smoke
python proto/e2e_ui_test.py full
```

## Prompt To Paste Into A New Chat

ใช้ข้อความนี้เปิดแชตใหม่เพื่อให้ทำงานต่อได้เร็ว:

```text
คุณเป็นหัวหน้าทีมวิศวกรและนักพัฒนาในโปรเจกต์ BMA-Plan

โปรเจกต์อยู่ที่:
F:\drives\My Drive\01 project\ai\bma-plan

ก่อนทำงานให้อ่านไฟล์:
1. AGENTS.md
2. SESSION_CONTINUATION.md
3. UI_REGRESSION_REPORT.md
4. proto/STATUS.md
5. PROGRESS.md
6. BMA_PLAN_V2_SCOPE.md
7. HANDOFF.md

สถานะล่าสุด:
- Backend ปัจจุบันใน proto/server.py ดีแล้ว ใช้ case_id, PDFium, upload guard, degraded mode
- UI ใหม่ใน proto/ui.html มี regression
- ผู้ใช้ต้องการให้ UX กลับไปใกล้ UI เดิม โดยเฉพาะ scroll mouse zoom และ snap workflow
- ห้าม revert backend ทั้งก้อน
- ให้แก้ proto/ui.html โดยเอา interaction จาก proto/server.py.bak กลับมา

งานแรกที่ต้องทำ:
1. เพิ่ม mouse wheel zoom ที่ตำแหน่ง cursor
2. แก้ snapRadius/closeRadius ให้หารด้วย zoom
3. คืน IX snap
4. คืน perpendicular snap
5. แยก openingMode ออกจาก perpMode

ก่อนแก้ไฟล์ ให้สรุปแผนสั้น ๆ ตาม AGENTS.md แล้วค่อยลงมือ
หลังแก้ให้รัน py_compile และทดสอบ browser ที่ http://localhost:8001/
```

## Short Context Summary

BMA-Plan คือ prototype สำหรับเปิด PDF แบบก่อสร้าง กทม., detect scale, snap vector, วัดระยะ/พื้นที่, tag หน้า, export report/PDF/XLSX และต่อยอดเป็นเครื่องมือตรวจแบบ

ทิศทางตอนนี้ไม่ใช่สร้างใหม่ แต่คือ:

1. รักษา backend ปัจจุบัน
2. ซ่อม interaction regression ใน UI ใหม่
3. ทำให้ UX อ่านแบบ/วัดแบบกลับมาลื่นเหมือน UI เดิม
4. แล้วค่อยเดินต่อ Sprint ตรวจแบบ กทม.
