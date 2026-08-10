# INVENT — lite-zero-install-packaging

Date: 2026-08-10 · Pipeline: `/lite-invent` (7 เฟสเต็ม) · Status: **awaiting human CHECKPOINT (GO / NOGO / RESHAPE)**

## 1. PICK

ไอเดียตั้งต้นจากผู้ใช้: "ระบบเปิด server รันโปรแกรม ดีที่สุดแล้วหรือไม่ / คิดนอกกรอบ" → ตั้งต้นเป็น `lite-serverless` (ตัด FastAPI ทิ้งทั้งตัว)

## 2. RESEARCH (bma-researcher) — verdict: `PRIOR_ART_PARTIAL`

- ตัด server 100% ติดกำแพงจริง 3 ด่าน: **mupdf.js เป็น AGPL** (ไม่เหมาะกับเครื่องมือราชการ), **pdf-lib ไม่มีหลักฐานว่ารอดกับไฟล์สแกน 300-500MB**, และ spike เก่า `lite-range-streaming` (NOGO 2026-07-03) พิสูจน์แล้วว่า PDF.js worker heap คือเพดาน memory ที่ลดไม่ได้ (~600MB บน binder 95MB)
- Incumbent ทุกราย (Bluebeam/STACK/Stirling-PDF) วัดฝั่ง client แต่จัดโครงหน้า/bake annotation ฝั่ง server ทั้งหมด
- ไลบรารีที่พร้อมจริง: SheetJS CE / fflate (XLSX ฝั่ง JS), pdf-lib+fontkit (ไฟล์เล็ก-กลาง + ฝัง Sarabun)

**ผลวิจัย reshape โจทย์:** ปัญหาจริงไม่ใช่ "ไม่มี server" แต่คือ **"เจ้าหน้าที่เปิดใช้บนเครื่องราชการได้แบบ zero-install: ไม่มี Python ไม่มี pip ไม่ต้องต่อเน็ต ไม่ต้อง admin"** — server ซ่อนอยู่ข้างในได้ถ้าผู้ใช้ไม่ต้องรู้จักมัน

## 3. FRAME

- Forbidden: Electron/Tauri rewrite · SaaS/cloud · แก้ `measure-engine.js`/RS/`pdfToC`/`cToPdf` · `.bmaplan` non-additive
- `## Eval` (รันได้จริง, ≥3 เคส): (1) happy — เปิดโดย PATH ไร้ Python → server ขึ้นใน 30s; (2) edge — permit จริง 45 หน้า ชื่อไฟล์+โฟลเดอร์ภาษาไทย → upload/render/export XLSX (ตรวจ openpyxl); (3) adversarial — เปิดซ้อน 2 instance → จัดการ port สะอาด instance แรกไม่ล้ม

## 4-5. DIVERGE + SCORE (bma-inventor) — 5 แนวทาง เสมอ 3 ทางที่ 25/30

| # | แนวทาง | แกน | คะแนน | ผล |
|---|---|---|---|---|
| A | PyInstaller one-file exe | packaging | 25 | spike |
| B | โฟลเดอร์ portable + Python embed | runtime | 25 | spike คู่ |
| E | pywebview native window (WebView2 ของ OS — ไม่ bundle browser) | architecture | 25 | side-check + **รอ human ตัดสินเรื่อง Electron-adjacency** |
| C | client-first degrade (วัดได้แม้ server ตาย) | resilience | 19 | ตกรอบเฟรมนี้ — คนละโจทย์ เก็บเป็น invent แยก |
| D | hosted PWA + companion exe | distribution | 15 | ตกรอบ — ขัด offline constraint |

เหตุ spike A+B พร้อมกัน: failure mode กลับด้านกัน — A เสี่ยง self-extract ลง `%TEMP%` ที่มีชื่อผู้ใช้ไทย + AV, B ไม่มีขั้น extract เลย

## 6. SPIKE — ผล: **ผ่านทุกเคส ทั้ง A และ B** (หลักฐาน: `lite/sandbox/invent-lite-packaging/SPIKE_RESULTS.md` + `results.json`)

| Eval case | A (exe เดี่ยว) | B (โฟลเดอร์ portable) |
|---|---|---|
| 1 zero-Python launch | ✅ PASS | ✅ PASS |
| 2 permit 45 หน้า ชื่อไทย (upload/render/XLSX) | ✅ PASS ทุก HTTP 200, XLSX parse | ✅ PASS |
| 3 เปิดซ้อน 2 ตัว | ✅ PASS (8100+8101, ตัวแรก serve ต่อ) | ✅ PASS |
| side-check E (WebView2) | ✅ หน้าต่างเปิด UI เต็ม ปิดสะอาด | — |

ตัวเลขสำคัญ:
- **A**: exe 77.7MB · cold start **20.9s ครั้งแรก / 8.3s warm** (self-extract คือตัวถ่วง — `--onedir` จะตัดออกได้เกือบหมด) · RSS ~116MB
- **B**: โฟลเดอร์ 112MB / 2,993 ไฟล์ · cold start **6.5s สม่ำเสมอ** · RSS ~103MB
- PyInstaller 6.22 build บน Python 3.14 ผ่านรอบแรก · `launch_lite.py` **ไม่ถูกแก้เลย** (ใช้ wrapper ฝั่ง sandbox จัดการ `sys._MEIPASS`)

Caveat ที่ต้องรู้ก่อนตัดสิน:
1. เคส 1 เป็นการ **จำลอง** เครื่องไร้ Python (sanitize PATH) — เครื่อง Windows สดจริงยังไม่ได้ทดสอบ (VC++/WebView2 DLL บนเครื่อง dev มีอยู่แล้ว)
2. ภาษี launch ของ A มีจริง 8-21s และ AV บนเครื่องลูกค้าจะทำให้แย่ลง
3. B เด้ง browser ทุกครั้งที่เปิด — แก้ได้ด้วย flag additive 1 บรรทัดใน `launch_lite.py` (spike ใช้ env `BMA_LITE_NO_BROWSER` ฝั่ง wrapper แล้ว)
4. ความเสี่ยงร่วมทุกแนวทาง: AppLocker/SmartScreen บนเครื่องราชการอาจ block exe ที่ไม่ได้ sign — การ code-sign เป็นงานแยกที่กระทบทุก option เท่ากัน

## 7. CHECKPOINT — คำถามถึง human

1. **GO รูปแบบไหน?** ข้อเสนอของ pipeline: **artifact แบบโฟลเดอร์** (B หรือ A แบบ `--onedir` ซึ่งโครงเดียวกัน) เป็นตัว ship — cold start 6.5s, ไม่มีความเสี่ยง temp-path/AV-extract แล้วค่อยชั้น E (native window) ทับเพื่อ UX
2. **คำตัดสินเรื่อง E**: pywebview + WebView2 ของ OS (ไม่ bundle Chromium) นับว่าอยู่ในข่าย "ห้าม Electron/Tauri" หรือไม่? spike ยืนยันแล้วว่าทำงานได้บนเครื่องนี้
3. งานที่จะเข้า sprint card ถ้า GO: `lite/build_portable.bat` หรือ `BMA-Plan-Lite.spec --onedir` production + flag `BMA_LITE_NO_BROWSER` (additive 1 บรรทัด) + ทดสอบบนเครื่อง Windows สดจริง 1 เครื่องก่อนแจก
4. NOGO/RESHAPE: ถ้าต้องการกลับไปทาง serverless เต็มตัว (pdf-lib) — research ชี้ว่าควรรอให้พิสูจน์ pdf-lib กับไฟล์ 300MB+ ก่อน และเก็บ C (degrade mode) เป็น invent pass แยก

## Decision

**GO** (user, 2026-08-10) — ship รูปแบบ **portable folder (B)** เป็น artifact หลัก + flag `BMA_LITE_NO_BROWSER` (additive 1 บรรทัดใน launch_lite.py) · **E (pywebview) ยังไม่ตัดสิน — พักไว้** ไม่อยู่ในขอบเขต build นี้ · เงื่อนไขก่อนแจกจริง: user ทดสอบบนเครื่อง Windows สดจริง 1 เครื่อง (เช็คลิสต์ 7 ข้อในแชท 2026-08-10)
