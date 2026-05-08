# BMA-Plan Skill Spec — ทำเป็น Skill ได้อย่างไร

> Skill (ทักษะทำงานซ้ำได้) ในที่นี้หมายถึง workflow ที่ AI/agent ทำซ้ำได้เป็นขั้นตอน มี input/output/checklist/test ชัดเจน ไม่ใช่แค่ prompt สวย ๆ

---

## 1. Skill หลักที่ควรสร้าง

```text
bma-plan-review-and-development-skill
```

### เป้าหมาย
ให้ AI ช่วยรีวิว วางแผน แก้โค้ด และทดสอบ BMA-Plan โดยไม่ทำ behavior เดิมพัง

### Input
- Google Drive folder หรือ project folder
- เอกสาร handoff/status/progress
- source files
- test files
- user task

### Output
- diagnosis (วิเคราะห์ปัญหา)
- development plan (แผนพัฒนา)
- patch plan (แผนแก้โค้ด)
- acceptance criteria (เกณฑ์รับงาน)
- test command (คำสั่งทดสอบ)
- updated docs
- optional patch/code

---

## 2. Skill Workflow (ลำดับการทำงาน)

```text
1. Discover project files
2. Read status/handoff/progress
3. Classify task type
4. Identify risk area
5. Create plan before coding
6. Apply patch only inside relevant files
7. Run baseline tests
8. Compare behavior against regression rules
9. Update docs
10. Summarize result + remaining gaps
```

---

## 3. Task Classifier (ตัวจำแนกชนิดงาน)

| Task Type | ตัวอย่าง | ต้องอ่าน | ต้องทดสอบ |
|---|---|---|---|
| UI Interaction | wheel zoom, snap, toolbar | ui.html, e2e_ui_test.py | smoke + manual/E2E |
| Measurement Engine | scale, dimension, area | server.py, ui.html, STATUS.md | smoke/full |
| Export | CSV/JSON/XLSX/PDF | server.py, e2e_ui_test.py | full |
| Rotation/Persistence | page rotation, save/load | server.py, ui.html | full |
| Security | secret, upload guard | server.py, config | smoke |
| Legal Rule | FAR, OSR, setback | legal source + code | legal-source test + full |
| Documentation | status, plan, handoff | docs | no code test unless changed behavior |

---

## 4. Skill Guardrails (รั้วกันพัง)

### Guardrail A — Scale Truth

ห้ามให้ output เป็นเมตร/ตร.ม. โดยไม่มี scale source

Required fields:

```json
{
  "scale_source": "manual | title_block_text | scale_bar | dimension_cross_check | unknown",
  "confidence": 0.0,
  "verified": false
}
```

### Guardrail B — Export Consistency

ค่าใน UI summary ต้องตรงกับ export

Check:

```text
UI summary == JSON derived metrics == XLSX summary == PDF annotation labels
```

### Guardrail C — Legal Source

legal rule ต้องมี source ต้นฉบับ

Required fields:

```json
{
  "rule_id": "...",
  "legal_source": "...",
  "effective_date": "...",
  "condition": "...",
  "threshold": "..."
}
```

### Guardrail D — No Regression

ถ้า feature เหล่านี้พัง ถือว่า reject:

- wheel zoom
- snap radius by zoom
- IX snap
- perpendicular snap
- close polygon
- opening mode
- save/load `.bmaplan`
- PDF rotation export
- case_id isolation

---

## 5. Skill Commands (ชุดคำสั่งมาตรฐาน)

### 5.1 Review Project

```text
Review this BMA-Plan folder. Identify:
1. current architecture
2. current capabilities
3. known gaps
4. highest-risk assumptions
5. next 3 development sprints
6. tests required before shipping
```

### 5.2 Plan Patch

```text
Create a patch plan for [TASK].
Before coding, list:
- files to read
- files to edit
- contracts to preserve
- acceptance criteria
- tests to run
Do not patch until the plan is complete.
```

### 5.3 Review Patch

```text
Review this patch against BMA-Plan rules:
- case_id isolation
- raw geometry recalculation
- scale confidence
- export/UI consistency
- no legal rule without source
- no UI regression
Return pass/fail with reasons.
```

### 5.4 Generate Idea Card

```text
Convert this project problem into an Idea Card:
- problem
- hypothesis
- research/product questions
- required data
- acceptance criteria
- implementation path
- risks
- skill that can be extracted
```

---

## 6. Skill Template File

เอาไฟล์นี้ไปทำเป็น skill ได้:

```md
# Skill: BMA-Plan Review and Development

## Purpose
Help develop BMA-Plan safely by reviewing context, planning patches, preserving measurement correctness, and enforcing test discipline.

## When to Use
Use when the user asks to review, improve, debug, refactor, extend, or document BMA-Plan.

## Inputs
- Project folder
- Current task
- STATUS.md
- PROGRESS.md
- HANDOFF.md
- source files
- test files

## Procedure
1. Read index/status/progress/handoff.
2. Classify task.
3. Identify risk.
4. Produce plan before coding.
5. Preserve contracts.
6. Patch minimally.
7. Run tests.
8. Update docs.
9. Summarize outcome.

## Contracts
- preserve case_id isolation
- preserve raw geometry recalculation
- preserve export/UI consistency
- keep auto scale unverified unless validated
- never add legal rules without primary source

## Output
- diagnosis
- plan
- patch summary
- test result
- updated docs
- remaining gaps
```

---

## 7. Skill แตกย่อยที่ควรมี

| Skill | ใช้ทำอะไร | Priority |
|---|---|---:|
| `pdf-scale-verification-skill` | หา/ตรวจ scale จาก PDF | P1 |
| `pdf-dimension-extraction-skill` | อ่าน dimension text | P1 |
| `cad-snap-engine-skill` | snap endpoint/intersection/perpendicular | P1 |
| `measurement-audit-export-skill` | export ที่ตรวจย้อนกลับได้ | P1 |
| `site-plan-measurement-workflow-skill` | วัดผังบริเวณ | P2 |
| `parking-count-report-skill` | นับและรายงานที่จอดรถ | P2 |
| `permit-report-k1-draft-skill` | สร้างรายงาน/ร่าง ค.1 | P3 |
| `bma-plan-agent-dev-skill` | ให้ coding agent ทำงานปลอดภัย | P0 |

---

## 8. MVP Skill ที่ควรทำก่อน

ให้เริ่มจาก skill นี้ก่อน:

```text
measurement-audit-export-skill
```

เหตุผล:

- ต่อจากระบบที่มีอยู่แล้ว
- เพิ่มความน่าเชื่อถือทันที
- ยังไม่ต้องแตะกฎหมาย
- ช่วยให้ทุกตัวเลขตรวจย้อนกลับได้
- เป็นฐานให้ report และ ค.1 ภายหลัง

MVP acceptance:

1. ทุก object มี object_id
2. export JSON มี raw geometry + derived metrics
3. XLSX มี Audit Trail sheet
4. PDF annotation มี label อ้างอิง object_id
5. recalibrate แล้ว derived metrics เปลี่ยนตรงกันทุก export
