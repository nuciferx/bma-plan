# RUN_PAGE_META_IDENTITY — แก้ระบบหน้า lite: meta ถูกล้างตอน Save + id ชนกันหลังเปิดไฟล์เก่า

> **เอกสารสั่งงานสำหรับ implementer (model อื่น / session ใหม่)** — อ่านไฟล์นี้จบแล้วลงมือได้เลย
> เขียน: 2026-08-10 (Opus, จากรีวิวรายโมดูล 35 ไฟล์) · สถานะ: **ready-to-build** · ประมาณงาน: 1 session

---

## คำสั่งหลัก (ให้ implementer ทำตามลำดับ ห้ามสลับ)

```
GATE-0  ปลดด่านชุดเทสต์ (roadmap-recon FAIL)          — ต้องเขียวก่อนแตะโค้ดใดๆ
SLICE-A แก้ meta wipe ใน projectToGlobals              — guard test RED ก่อน แล้วค่อยแก้ให้เขียว
SLICE-B แก้ _idc ชนกับ id ที่โหลดจากไฟล์               — guard test RED ก่อน แล้วค่อยแก้ให้เขียว
FINAL   รัน test suite เต็ม + sprint outputs + commit
```

ทุก slice: **commit แยกกัน** ข้อความ commit ระบุท้ายเอกสาร

---

## บริบท (ทำไมต้องแก้)

อาการที่ผู้ใช้เจอ: "เลเยอร์มั่ว การจัดการหน้ามั่ว" — รากคือ 2 บั๊กใน `lite/static/js/page-manager.js`:

1. **Meta wipe (I5):** `_pmCommit()` (`lite/ui-lite.html:422-428`) เรียก
   `pageMgr.projectToGlobals(PS)` — ส่งเฉพาะ **content** สด แต่ meta
   (tag / rot / floorKind / floorNum / name / excluded) ถูกอ่านจาก
   `meta_by_id` ซึ่ง snapshot ไว้**ตอนเปิดไฟล์เท่านั้น** (`page-manager.js:491`)
   ขณะที่ตัวแก้ meta ตัวจริง (`liteSetTag`/`liteSetFloorNum`/`rotatePage`/exclude toggle)
   เขียนลง **globals แบบ number-keyed เท่านั้น** ไม่เคยแตะ model
   → ทุกครั้งที่ Save / Apply / Merge (ทุกทางเรียก `_pmCommit`) meta ที่ทำหลังเปิดไฟล์
   **ถูกย้อนกลับทั้งหมด** → `reseedActivePageFolders()` (บรรทัดถัดมา :427) จัดโฟลเดอร์ชั้น
   ใหม่ตามข้อมูลเก่า → ผู้ใช้เห็นเป็น "เลเยอร์มั่ว"
   (นี่คือครึ่งที่เหลือของ BUG-20260703 — ครึ่ง content แก้ไปแล้วด้วย `_liveContentFor`)

2. **ID collision (I9):** `_idc = 0` ทุก session (`page-manager.js:28`) แต่
   `load()` (:342) และ `seedFromGlobals()` (:409) **adopt id เดิมจากไฟล์โดยไม่เลื่อน counter**
   → เปิด `.bmaplan` ที่มี `pageIdentities` `pg0..pg44` แล้วกด duplicate หน้าใดก็ตาม
   → `newId()` คืน **`pg0` ซ้ำ** → `PS_by_id['pg0']` ถูกทับ + `pageOrder` มี id ซ้อน
   → ข้อมูลวัดหน้าแรกพัง

## ขอบเขต (แตะได้ / ห้ามแตะ)

| แตะได้ | ห้ามแตะ |
|---|---|
| `lite/static/js/page-manager.js` (533/1000 — มีที่ ~40 บรรทัด) | `lite/static/js/measure-engine.js` (sha256-pinned) |
| `lite/ui-lite.html` **เฉพาะบรรทัด `_pmCommit` (:424)** — แก้ in-place ห้ามเพิ่มบรรทัดสุทธิ (ไฟล์อยู่ 1189/1200 เหลือ 11 บรรทัด) | `RS` / `pdfToC` / `cToPdf` / snap internals |
| `lite/tests/test_page_manager.py` (+เทสต์ใหม่) | schema `.bmaplan` (ห้าม rename/ลบ field — additive เท่านั้น) |
| `docs/status/PHASE_INDEX.md` + `docs/status/ROADMAP_DONE.md` (GATE-0) | `proto/**` ทั้งหมด |

---

## GATE-0 — ปลดด่านชุดเทสต์

ตอนนี้ `python lite/tests/run_all_tests.py` **FAIL ตั้งแต่ preflight**:
`[FAIL] roadmap-recon` → `TRUTH_CHECK_FAIL (1/5)` — สาเหตุคือ `docs/status/PHASE_INDEX.md`
มีแถว `✅ shipped` ค้าง (ประมาณบรรทัด 56-57) ที่ต้องย้ายไป `docs/status/ROADMAP_DONE.md`

ขั้นตอน:
1. `python scripts/reconcile_roadmap.py` — อ่าน findings ที่มันพิมพ์ (อย่าเดาเอง แก้ตามที่สคริปต์ระบุ)
2. ย้าย/แก้แถวตามนั้น (โดยปกติ: ตัดแถว shipped ออกจาก PHASE_INDEX แล้ว append เข้า ROADMAP_DONE ตาม format ที่ไฟล์ปลายทางใช้อยู่)
3. ยืนยัน: `python scripts/check_executable_truth.py` → ต้องได้ `TRUTH_CHECK_OK (5/5)`
4. commit แยก: `docs: unblock roadmap-recon gate — reconcile shipped rows PHASE_INDEX → ROADMAP_DONE`

**STOP-CONDITION:** ถ้า reconcile รายงานอย่างอื่นนอกจาก shipped-row drift (เช่น ledger เสีย, commit hash หาย) — หยุด รายงานกลับ อย่าเดาแก้

---

## SLICE-A — meta wipe

### A1. Guard test (ต้อง RED ก่อนแก้)

เพิ่มเทสต์ใน `lite/tests/test_page_manager.py` (ตาม harness เดิมของไฟล์นั้น — มันรัน PageModel ผ่าน Node อยู่แล้ว ดู E1-E16 เป็นแบบ):

```
TEST E17-meta-live (marker: LITE_PM_META_LIVE_OK)
  seed:  seedFromGlobals({pageCount:3, pageTags:{}, pageRot:{}, ...ว่าง, pageIdentities:undefined})
  act:   liveMeta = {pageTags:{1:'floor'}, pageRot:{2:90}, pageFloorNum:{1:3},
                     pageNames:{}, pageFloorKind:{1:'normal'}, excluded:{3:true}}
         g = m.projectToGlobals(livePS, liveMeta)
  assert g.pageTags[1]==='floor' && g.pageRot[2]===90 && g.pageFloorNum[1]===3
         && g.pageFloorKind[1]==='normal' && g.excluded[3]===true
```

รันให้เห็น **RED** (พฤติกรรมปัจจุบัน: ค่าทั้งหมดหายเพราะอ่านจาก snapshot) — บันทึกผล RED ไว้ใน TEST_RESULT

### A2. การแก้ — mirror pattern `_liveContentFor` ที่มีอยู่แล้วเป๊ะๆ

ใน `page-manager.js` เพิ่ม method ข้างๆ `_liveContentFor` (:463):

```js
/* Meta twin of _liveContentFor (BUG-20260703 second half):
 * live number-keyed meta dicts are the runtime truth — liteSetTag / rotatePage /
 * exclude write ONLY there. Resolve each id's meta from live dicts via its
 * baseline position; dup pages resolve via dupSrc; merged pages keep model meta. */
PageModel.prototype._liveMetaFor = function (id, liveMeta) {
  if (!liveMeta) return null;
  var b = this._initialIds.indexOf(id);
  if (b < 0) {
    var src = this.dupSrc && this.dupSrc[id];
    if (src) b = this._initialIds.indexOf(src);
  }
  if (b < 0) return null;               // merged page — model meta is authority
  var n = b + 1, mt = blankMeta();
  mt.rot       = (liveMeta.pageRot       && liveMeta.pageRot[n])       || 0;
  mt.tag       = (liveMeta.pageTags      && liveMeta.pageTags[n])      || '';
  mt.name      = (liveMeta.pageNames     && liveMeta.pageNames[n])     || '';
  mt.floorKind = (liveMeta.pageFloorKind && liveMeta.pageFloorKind[n]) || '';
  var fn = liveMeta.pageFloorNum && liveMeta.pageFloorNum[n];
  mt.floorNum  = (fn === undefined || fn === null) ? null : fn;
  mt.excl      = !!(liveMeta.excluded && liveMeta.excluded[n]);
  return mt;
};
```

แก้ `projectToGlobals` (:476) — เพิ่มพารามิเตอร์ที่ 2 และ resolve+refresh snapshot:

```js
PageModel.prototype.projectToGlobals = function (livePS, liveMeta) {
  ...
  this.pageOrder.forEach(function (id, i) {
    var n  = i + 1;
    var mt = self._liveMetaFor(id, liveMeta) || self.meta_by_id[id] || blankMeta();
    self.meta_by_id[id] = mt;            // refresh snapshot (เหมือนที่ทำกับ PS_by_id :496)
    ...ส่วน fan-out เดิมคงไว้ทุกบรรทัด...
```

แก้ผู้เรียก `lite/ui-lite.html:424` **in-place บรรทัดเดียว** (ห้ามเพิ่มบรรทัด):

```js
var g=pageMgr.projectToGlobals(PS,{pageTags:pageTags,pageFloorKind:pageFloorKind,pageFloorNum:pageFloorNum,pageNames:pageNames,pageRot:pageRot,excluded:excluded});
```

**เหตุผลของ design นี้ (อย่าเปลี่ยน):** `liveMeta` เป็น optional เหมือน `livePS` →
เทสต์ pure-model เดิมทั้งหมด (เรียกแบบไม่ส่ง arg) พฤติกรรมไม่เปลี่ยน = backward compatible
duplicate resolve ผ่าน `dupSrc` ให้พฤติกรรมตรงกับ content ทุกประการ

### A3. ยืนยัน

- E17 เขียว + เทสต์เดิมใน `test_page_manager.py` เขียวครบ (E1-E16)
- `python lite/tests/run_all_tests.py` — MR-save-roundtrip / MR-dirty (I4, I9) ต้องไม่แดงเพิ่ม
- manual check 1 รอบ: เปิด PDF → tag หน้า + หมุนหน้า → Ctrl+S → tag/rotation **ยังอยู่** และโฟลเดอร์ชั้นไม่เด้ง

---

## SLICE-B — id collision

### B1. Guard test (ต้อง RED ก่อนแก้)

```
TEST E18-id-no-collision (marker: LITE_PM_ID_SEED_OK)
  seed:  m.load(doc ที่มี pageIdentities:['pg0','pg1','pg2'])   // จำลองไฟล์ session เก่า
  act:   m.duplicate(1)
  assert pageOrder ไม่มี id ซ้ำ (new Set(pageOrder).size === pageOrder.length)
         && id ใหม่ไม่อยู่ใน ['pg0','pg1','pg2']
  ทำซ้ำอีกเคสผ่าน seedFromGlobals({pageIdentities:['pg0','pg1','pg2'], ...})
```

รันให้เห็น **RED** (ปัจจุบัน: duplicate มินต์ `pg0` ซ้ำ)

### B2. การแก้

ใน `page-manager.js` ข้าง `newId()` (:31) เพิ่ม:

```js
// Adopted ids from a prior session must advance the mint counter,
// or newId() re-mints pg0 and overwrites page 1 (I9).
function adoptId(id) {
  var m = /^pg(\d+)$/.exec(String(id));
  if (m && +m[1] >= _idc) _idc = +m[1] + 1;
  return id;
}
```

แล้วครอบจุด adopt ทั้ง 2 จุด:
- `:342` → `var id = hasIds ? adoptId(doc.pageIdentities[i]) : newId();`
- `:409` → `var id = hasIds ? adoptId(g.pageIdentities[n - 1]) : newId();`

(id ที่ไม่ match `^pg\d+$` — เช่นไฟล์แก้มือ — ผ่านได้เฉยๆ ไม่ throw; counter ไม่ขยับ ซึ่งปลอดภัยเพราะ pattern ใหม่ไม่มีวันชนกับมัน)

### B3. ยืนยัน

- E18 เขียว + E1-E16 เขียว + `run_all_tests.py` ผ่าน tier ที่เกี่ยว (I4/I9)
- manual: save `.bmaplan` → ปิด → เปิดใหม่ → duplicate หน้า 1 → หน้า 1 เดิมข้อมูลครบ หน้าใหม่เป็นสำเนา

---

## FINAL — ปิดงาน

1. `python scripts/check_executable_truth.py` → `TRUTH_CHECK_OK` (line-caps ต้องผ่าน — เช็ค `wc -l lite/ui-lite.html` ≤ 1200)
2. `python lite/tests/run_all_tests.py` → เขียวทั้ง suite (หรือแดงเฉพาะตัวที่แดงอยู่ก่อนแล้ว — ถ้ามี ให้บันทึกรายชื่อเทียบ baseline ใน TEST_RESULT)
3. อัปเดต sprint outputs 7 ไฟล์ (ใช้ `/bma-sprint-finalize` ได้): `log.md`, `PATCH_SUMMARY.md`, `TEST_RESULT.md` (รวมหลักฐาน RED→GREEN ของ E17/E18), `FINAL_REPORT_FOR_CHATGPT.md`, `CURRENT_STATUS.md`, `docs/status/LATEST_STATUS.md`, `docs/status/NEXT_ACTIONS.md`
4. อัปเดต `docs/status/SHIPS.jsonl` ถ้าโปรเจกต์ใช้ ledger นี้กับ lite ships (ดู entry เดิมเป็น format; guard markers = `LITE_PM_META_LIVE_OK`, `LITE_PM_ID_SEED_OK`)
5. ย้าย sprint card นี้ไป `sprints/completed/2026-08-10-page-meta-identity/`

Commit messages (แยก 3 commit):
```
docs: unblock roadmap-recon gate — reconcile shipped rows PHASE_INDEX → ROADMAP_DONE
fix(lite): PM-META — projectToGlobals resolves meta from live dicts (BUG-20260703 second half, I5)
fix(lite): PM-ID — adopted pageIdentities advance _idc, duplicate can no longer re-mint pg0 (I9)
```

## Stop conditions (หยุดแล้วรายงาน อย่าฝืน)

- GATE-0 พบ drift ชนิดอื่นนอกจาก shipped-row
- Guard test เขียนแล้ว **ไม่ RED** (= เข้าใจบั๊กผิด — ห้ามแก้โค้ดต่อ)
- แก้แล้วเทสต์เดิมตัวใดแดง (เทียบ baseline ก่อนแก้เสมอ)
- ต้องเพิ่มบรรทัดสุทธิใน `ui-lite.html` เกิน 0 (ชนเพดาน 1200 — ต้องกลับมาปรึกษา)

## งานต่อเนื่องที่ *ไม่ใช่* ของ sprint นี้ (อย่าแถม)

remap `pageRot`/`_scanned` ตาม identity ตอน reorder · thumbnail ใช้ `serverNum()` ·
sync canvas/pageCount หลัง mutate ใน PM overlay · tag-jit banner ผิดหน้า —
ทั้งหมดถูก file ไว้แล้วในรีวิว 2026-08-10 เป็นคิวถัดไป
