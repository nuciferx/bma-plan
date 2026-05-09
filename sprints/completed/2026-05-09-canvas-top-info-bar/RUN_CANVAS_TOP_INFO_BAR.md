# RUN_CANVAS_TOP_INFO_BAR.md

Goal:
Add a canvas top info bar.

Show:
- current page / total pages
- page name or floor
- scale status
- zoom if available
- current tool
- active layer
- coordinates only if already available safely

Rules:
- Must not block canvas drawing.
- Must not introduce new drawing behavior.

Required tests:
- `python -m py_compile proto/server.py proto/e2e_ui_test.py`
- `python proto/e2e_ui_test.py smoke`
- `python proto/e2e_ui_test.py full`
