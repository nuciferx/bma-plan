/* LMENU-1: menu-flyout.js — flyout submenu chrome for Measure + File dropdowns.
   Called after all tool-dispatch globals (setTool, toggleSnap, openReport,
   closeMenus) are defined in ui-lite.html.
   This file only restructures menu chrome — no new tools, no new behaviors. */

/* ---------------------------------------------------------------------------
   FLYOUT_GROUPS — extend by adding entries.
   Each item must have exactly one of {tool, action, sep}:
     tool     -> setTool(tool) + optional hintFlash for 5s
     action   -> named global function call
     sep:true -> renders a separator element (no click handler)
     snapType -> (optional) marks item for live ✓ label refresh by snap-types.js
   hint (optional) -> sets state.hintFlash for 5s after activating the tool.
--------------------------------------------------------------------------- */
var FLYOUT_GROUPS = {
  area: {
    parentLabel: 'Area ▶',
    items: [
      { label: 'Polygon (A)', tool: 'poly' },
      { label: 'Polygon + Arc edges (A→A)', tool: 'poly',
        hint: 'กด A ระหว่างวาด → arc edge' }
    ]
  },
  distance: {
    parentLabel: 'Distance ▶',
    items: [
      { label: 'Single segment (D)', tool: 'dist' },
      { label: 'Continuous path (⇧D)', tool: 'path' }
    ]
  },
  snap: {
    parentLabel: 'Snap Modes ▶',
    items: [
      { label: 'Endpoint (E)',   action: 'toggleSnapTypeEndpoint',     snapType: 'endpoint' },
      { label: 'Midpoint (M)',   action: 'toggleSnapTypeMidpoint',     snapType: 'midpoint' },
      { label: 'Center (C)',     action: 'toggleSnapTypeCenter',       snapType: 'center' },
      { label: 'Intersection',   action: 'toggleSnapTypeIntersection', snapType: 'intersection' },
      { label: 'Nearest on Edge', action: 'toggleSnapTypeNearest',     snapType: 'nearest' },   // SNAP-2026-07-04 slice 3
      { sep: true },
      { label: 'Disable All (G)', action: 'toggleSnap' }
    ]
  },
  /* S-6 (REVIEW_LITE_LAYER_REPORT_20260704 ledger, slice D/4): the 3 real
     export/report doors of the app, all in one place with truthful Thai
     labels. "XLSX (Ctrl+E)" spells out the existing hotkey so it stays
     discoverable from the submenu too (see _rebuildFileMenu for the
     flat #mi-xlsx item, which is unhidden, not removed). */
  export: {
    parentLabel: 'Export ▶',
    items: [
      { label: 'รายงาน (แก้ไข/พิมพ์ได้)', action: 'openReport' },
      { label: 'XLSX (Ctrl+E)',           action: 'exportXlsx' },
      { label: 'PDF ทับ Annotation',       action: 'exportPdfOverlay' }
    ]
  }
};

/* ---------------------------------------------------------------------------
   exportXlsx — global action for XLSX Summary item in Export ▶ submenu.
   Guards against missing caseId / helpers so it is safe to call at any time.
--------------------------------------------------------------------------- */
window.exportXlsx = function () {
  if (typeof caseId === 'undefined' || !caseId) { alert(typeof gateNoCaseMsg==='function'?gateNoCaseMsg():'เปิด PDF ก่อน'); return; }
  if (typeof dlPost !== 'function' || typeof buildExportData !== 'function' || typeof baseName !== 'function') return;
  dlPost('/export-xlsx', buildExportData(), baseName() + '.xlsx');
  if (typeof closeMenus === 'function') closeMenus();
};

/* ---------------------------------------------------------------------------
   exportPdfOverlay — global action for "PDF ทับ Annotation" in Export ▶.
   Thin delegate to ExportAnnotate.exportPdfOverlay (export-annotate.js),
   which already guards caseId/alerts -- no logic duplicated here.
--------------------------------------------------------------------------- */
window.exportPdfOverlay = function () {
  if (typeof ExportAnnotate === 'undefined' || typeof ExportAnnotate.exportPdfOverlay !== 'function') return;
  ExportAnnotate.exportPdfOverlay();
};

/* ---------------------------------------------------------------------------
   _flyoutDispatch — dispatch an item's action or tool.
   Sep items are never dispatched (they have no click handler).
--------------------------------------------------------------------------- */
function _flyoutDispatch(item) {
  if (item.tool) {
    setTool(item.tool);
    if (item.hint) {
      state.hintFlash = item.hint;
      setTimeout(function () {
        state.hintFlash = '';
        if (typeof updateHUD === 'function') updateHUD();
      }, 5000);
    }
  } else if (item.action) {
    var fn = window[item.action];
    if (typeof fn === 'function') fn();
  }
  // snapType items: toggleSnapType updates labels live; don't close menu so user
  // can toggle multiple types in one open session. Other items close as before.
  if (!item.snapType) {
    if (typeof closeMenus === 'function') closeMenus();
  }
}

/* ---------------------------------------------------------------------------
   _buildSubItem — create a single .item inside a .sub-dd.
   Returns a .sep element for {sep:true} items (no click handler).
   Returns a .item element for all others.
   snapType items get data-snap-type attribute and a ✓ chip label (from
   snapTypeChip if available, else plain label).
--------------------------------------------------------------------------- */
function _buildSubItem(item) {
  // Separator
  if (item.sep) {
    var sep = document.createElement('div');
    sep.className = 'sep';
    return sep;
  }

  var el = document.createElement('div');
  el.className = 'item';

  // snapType items: show live ✓ chip; keep menu open so user can multi-toggle
  if (item.snapType) {
    el.dataset.snapType = item.snapType;
    // Initial label: use snapTypeChip if snap-types.js already loaded
    if (typeof snapTypeChip === 'function') {
      var shortcut = { endpoint: 'E', midpoint: 'M', center: 'C', intersection: null, nearest: null }[item.snapType];
      el.textContent = shortcut
        ? snapTypeChip(item.snapType) + ' (' + shortcut + ')'
        : snapTypeChip(item.snapType);
    } else {
      el.textContent = item.label;
    }
  } else {
    el.textContent = item.label;
  }

  // store data for test assertions
  if (item.tool)   el.dataset.tool   = item.tool;
  if (item.action) el.dataset.action = item.action;
  if (item.hint)   el.dataset.hint   = item.hint;

  el.addEventListener('click', function (e) {
    e.stopPropagation();
    _flyoutDispatch(item);
  });
  return el;
}

/* ---------------------------------------------------------------------------
   _buildParentItem — create a .item.has-sub element with a .sub-dd child.
--------------------------------------------------------------------------- */
function _buildParentItem(group) {
  var parent = document.createElement('div');
  parent.className = 'item has-sub';
  parent.dataset.flyoutGroup = group.key;

  var label = document.createElement('span');
  label.textContent = group.parentLabel;
  parent.appendChild(label);

  var sub = document.createElement('div');
  sub.className = 'sub-dd';
  group.items.forEach(function (item) {
    sub.appendChild(_buildSubItem(item));
  });
  parent.appendChild(sub);
  return parent;
}

/* ---------------------------------------------------------------------------
   _rebuildMeasureMenu — replaces the flat poly/dist/path items in the
   Measure dropdown with Area ▶ and Distance ▶ flyout parents, and adds
   Snap Modes ▶ replacing the flat snap item.
   Items that stay flat: select, scale, ref, count, mi-snap→removed, mi-loupe.
--------------------------------------------------------------------------- */
function _rebuildMeasureMenu() {
  var dd = document.querySelector('.menu[data-m="measure"] .dd');
  if (!dd) return;

  // Collect items we want to keep (flat, in order)
  var selectItem = dd.querySelector('[data-tool="select"]');
  var scaleItem  = dd.querySelector('[data-tool="scale"]');
  var verifyItem = dd.querySelector('#mi-verify-scale');  // INV-2026-07-lite-verify
  var refItem    = dd.querySelector('[data-tool="ref"]');
  var countItem  = dd.querySelector('[data-tool="count"]');
  var sepBefore  = dd.querySelector('.sep');   // separator before snap/loupe

  // Remove the flat poly/dist/path items (they move into flyouts)
  ['poly', 'dist', 'path'].forEach(function (t) {
    var el = dd.querySelector('[data-tool="' + t + '"]');
    if (el) el.remove();
  });

  // Remove the flat snap item (replaced by Snap Modes flyout)
  var miSnap = dd.querySelector('#mi-snap');
  if (miSnap) miSnap.remove();

  // Build Area ▶ flyout parent, insert after scale item
  var areaGroup = Object.assign({ key: 'area' }, FLYOUT_GROUPS.area);
  var areaParent = _buildParentItem(areaGroup);

  var distGroup = Object.assign({ key: 'distance' }, FLYOUT_GROUPS.distance);
  var distParent = _buildParentItem(distGroup);

  var snapGroup = Object.assign({ key: 'snap' }, FLYOUT_GROUPS.snap);
  var snapParent = _buildParentItem(snapGroup);

  // Insert order: select · scale · [sep] · Area▶ · Distance▶ · ref · count · [sep] · SnapModes▶ · loupe · ortho · hint
  // We rebuild by clearing and re-inserting in order.
  // Keep the loupe, ortho, and hint items.
  var loupeItem = dd.querySelector('#mi-loupe');
  var orthoItem = dd.querySelector('#mi-ortho');
  var hintItem  = dd.querySelector('[style*="pointer-events:none"]');

  // Clear all children and rebuild
  while (dd.firstChild) dd.removeChild(dd.firstChild);

  if (selectItem) dd.appendChild(selectItem);
  if (scaleItem)  dd.appendChild(scaleItem);
  if (verifyItem) dd.appendChild(verifyItem);

  var sep1 = document.createElement('div'); sep1.className = 'sep';
  dd.appendChild(sep1);

  dd.appendChild(areaParent);
  dd.appendChild(distParent);

  if (refItem)   dd.appendChild(refItem);
  if (countItem) dd.appendChild(countItem);

  var sep2 = document.createElement('div'); sep2.className = 'sep';
  dd.appendChild(sep2);

  dd.appendChild(snapParent);
  if (loupeItem) dd.appendChild(loupeItem);
  if (orthoItem) dd.appendChild(orthoItem);
  if (hintItem)  dd.appendChild(hintItem);
}

/* ---------------------------------------------------------------------------
   _rebuildFileMenu — S-6 (REVIEW_LITE_LAYER_REPORT_20260704 ledger, slice
   D/4): Export ▶ is now the ONE grouped door for all 3 export/report
   actions (Report / XLSX / PDF overlay) -- no new actions, matches spec's
   "menu count discipline".
   - mi-report's DOM position becomes the Export ▶ flyout parent.
   - mi-xlsx is UNHIDDEN (previously display:none while Ctrl+E still called
     it -- a "ghost feature": working but undiscoverable). It now stays a
     normal visible flat File-menu item alongside the Export ▶ submenu's own
     "XLSX (Ctrl+E)" item -- both point at the same exportXlsx action, same
     tolerated pattern as the overview-setup.js wizard button also pointing
     at openReport (one of the 3 actions, reachable from more than one
     place, never a 4th distinct action).
   - mi-pdfov (previously a separate flat File-menu item, not grouped with
     Export at all) is absorbed/removed outright into Export ▶'s 3rd item --
     no hotkey depends on it, so unlike mi-xlsx it doesn't need to stay.
--------------------------------------------------------------------------- */
function _rebuildFileMenu() {
  var dd = document.querySelector('.menu[data-m="file"] .dd');
  if (!dd) return;

  var miPdfov = dd.querySelector('#mi-pdfov');
  if (miPdfov) miPdfov.remove();

  // Build Export ▶ flyout parent -- 3 items: Report / XLSX / PDF overlay
  var expGroup = Object.assign({ key: 'export' }, FLYOUT_GROUPS.export);
  var expParent = _buildParentItem(expGroup);

  // Replace the existing mi-report item with the flyout parent
  var miReport = dd.querySelector('#mi-report');
  if (miReport) {
    // Remove the onclick wired to openReport (flyout item handles it)
    miReport.parentNode.replaceChild(expParent, miReport);
  } else {
    // mi-report not found: append the flyout at the end as fallback
    dd.appendChild(expParent);
  }
}

/* ---------------------------------------------------------------------------
   init — called once DOMContentLoaded fires (or immediately if already ready,
   since this script is loaded at the end of <body>).
--------------------------------------------------------------------------- */
function _flyoutInit() {
  _rebuildMeasureMenu();
  _rebuildFileMenu();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', _flyoutInit);
} else {
  _flyoutInit();
}
