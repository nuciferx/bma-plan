# RUN_WIDGET_PLACEMENT_POLISH.md

Goal:
Polish existing left-side widgets to match mockup direction.

Polish:
- Workflow card
- Scale status
- Page info
- Review warning
- Export ready
- Inspection status panel

Rules:
- No new business logic.
- No export/save-load changes.
- Keep compact layout at 1366px.

Required tests:
- `python -m py_compile proto/server.py proto/e2e_ui_test.py`
- `python proto/e2e_ui_test.py smoke`
- `python proto/e2e_ui_test.py full`
