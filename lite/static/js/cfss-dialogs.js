/* CFSS-DIALOGS — Promote + Edit modals, extracted from cross-floor-shapes.js
   (cap discipline 2026-05-25). Behavior byte-equivalent to pre-extract.
   Loaded by page-folder-layers.js via __cfss_dialogs_script__ AFTER
   cross-floor-shapes.js, so the symbols this file references
   (cfssCommitPromote, cfssCommitEdit, masterById, instanceAreaM2, makeInstance,
    isInstance, addMaster, MASTERS, __cfss_nextMasterIdN) are available. */

if (window.__cfss_dialogs_loaded__) { /* already loaded */ } else {
window.__cfss_dialogs_loaded__ = true;

/* --- CSS for the promote/edit dialogs (injected once, scoped to #cfss-*) --- */
function _cfssInjectDialogCSS() {
  if (document.getElementById('cfss-style')) return;
  var s = document.createElement('style');
  s.id = 'cfss-style';
  s.textContent = [
    '#cfss-overlay{position:fixed;inset:0;background:rgba(6,8,12,.72);z-index:310;',
    '  display:flex;align-items:center;justify-content:center;}',
    '#cfss-dlg{background:#161a22;border:1px solid #2a3140;border-radius:12px;',
    '  padding:18px 20px;width:360px;max-height:80vh;display:flex;flex-direction:column;',
    '  color:#e7ecf3;font-family:"Segoe UI",system-ui,sans-serif;font-size:13px;}',
    '#cfss-dlg h4{margin:0 0 8px;font-size:14px;color:#4c8dff;}',
    '#cfss-dlg .cfss-info{font-size:11px;color:#8b97a8;margin-bottom:10px;}',
    '#cfss-dlg .cfss-field{margin-bottom:10px;}',
    '#cfss-dlg .cfss-field label{display:block;color:#8b97a8;font-size:11px;margin-bottom:3px;}',
    '#cfss-dlg .cfss-field input{width:100%;background:#0c0f14;border:1px solid #2a3140;',
    '  color:#e7ecf3;border-radius:6px;padding:6px 9px;font-size:13px;}',
    '#cfss-pages{flex:1;overflow-y:auto;max-height:220px;margin-bottom:12px;',
    '  border:1px solid #2a3140;border-radius:6px;padding:6px;}',
    '#cfss-pages .cfss-pg-row{display:flex;align-items:center;gap:8px;',
    '  padding:5px 6px;border-radius:5px;font-size:12px;cursor:pointer;}',
    '#cfss-pages .cfss-pg-row:hover{background:#222a37;}',
    '#cfss-pages .cfss-pg-warn{font-size:11px;color:#ffb454;padding:4px 6px;}',
    '#cfss-dlg .cfss-btns{display:flex;gap:8px;justify-content:flex-end;}',
    '#cfss-dlg .cfss-btn{padding:6px 14px;border-radius:7px;border:1px solid #2a3140;',
    '  background:#222a37;color:#e7ecf3;cursor:pointer;font-size:12px;}',
    '#cfss-dlg .cfss-btn.pri{background:#4c8dff;border-color:#4c8dff;color:#fff;}',
    '#cfss-dlg .cfss-btn:hover{filter:brightness(1.15);}',
    '#cfss-dlg .cfss-row{display:flex;gap:8px;margin-bottom:8px;}',
    '#cfss-dlg .cfss-row > .cfss-field{flex:1;}',
    '#cfss-dlg .cfss-field input[type=color]{padding:2px;height:28px;cursor:pointer;}',
    '#cfss-dlg .cfss-field input:disabled{opacity:.4;cursor:not-allowed;}',
    '#cfss-dlg .cfss-hint{color:#8b97a8;font-size:11px;margin-top:-4px;margin-bottom:8px;}'
  ].join('\n');
  document.head.appendChild(s);
}

/* --- Promote dialog --- */
var _cfssDlgEl = null;

function cfssOpenPromoteDialog(sourcePoly) {
  _cfssInjectDialogCSS();
  // Close any previous dialog
  if (_cfssDlgEl) { _cfssDlgEl.remove(); _cfssDlgEl = null; }

  // Find source page and ppm
  var srcPg = null;
  var pgKeys = Object.keys(window.PS || {});
  for (var ki = 0; ki < pgKeys.length; ki++) {
    var k = pgKeys[ki];
    var objs = window.PS[k] && window.PS[k].objects;
    if (objs && objs.indexOf(sourcePoly) >= 0) { srcPg = +k; break; }
  }
  var srcScale = srcPg && window.PS[srcPg] && window.PS[srcPg].scale;
  var ppm = srcScale && srcScale.pts_per_m > 0 ? srcScale.pts_per_m : null;

  // Compute bbox for info display
  var minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  (sourcePoly.pts || []).forEach(function(p) {
    if (p.x < minX) minX = p.x; if (p.y < minY) minY = p.y;
    if (p.x > maxX) maxX = p.x; if (p.y > maxY) maxY = p.y;
  });
  var wM = ppm ? ((maxX - minX) / ppm).toFixed(2) : '—';
  var hM = ppm ? ((maxY - minY) / ppm).toFixed(2) : '—';
  var aM = ppm ? instanceAreaM2(
    makeInstance('__tmp__', {x: minX, y: minY}),
    ppm
  ) : null;
  // Use a quick shoelace on source pts directly (master not created yet)
  if (ppm) {
    var n = sourcePoly.pts.length, a2 = 0;
    for (var ii = 0; ii < n; ii++) {
      var jj = (ii + 1) % n;
      a2 += (sourcePoly.pts[ii].x / ppm) * (sourcePoly.pts[jj].y / ppm)
           - (sourcePoly.pts[jj].x / ppm) * (sourcePoly.pts[ii].y / ppm);
    }
    aM = (Math.abs(a2) / 2).toFixed(2);
  }

  var defaultName = sourcePoly.name || ('Master ' + (window.__cfss_nextMasterIdN || 1));

  var overlay = document.createElement('div');
  overlay.id = 'cfss-overlay';
  var dlg = document.createElement('div');
  dlg.id = 'cfss-dlg';

  dlg.innerHTML = [
    '<h4>📏 ทำเป็นต้นแบบข้ามชั้น — เลือกหน้าที่จะติด</h4>',
    '<div class="cfss-info">',
    (ppm
      ? (wM + ' m × ' + hM + ' m = ' + aM + ' m²')
      : '<span style="color:#ffb454">⚠ ยังไม่ได้ตั้งสเกลหน้านี้</span>'),
    '</div>',
    '<div class="cfss-field"><label>ชื่อ (ชื่อมาสเตอร์)</label>',
    '<input id="cfss-name-inp" type="text" value="' + defaultName.replace(/"/g,'&quot;') + '"></div>',
    '<div id="cfss-pages"></div>',
    '<div class="cfss-btns">',
    '<button class="cfss-btn" id="cfss-cancel">ยกเลิก</button>',
    '<button class="cfss-btn pri" id="cfss-install">ติดตั้ง</button>',
    '</div>'
  ].join('');

  // Build page list
  var pagesDiv = dlg.querySelector('#cfss-pages');
  var totalPages = window.pageCount || 1;
  var hasNoScalePage = false;
  for (var pg = 1; pg <= totalPages; pg++) {
    if (pg === srcPg) continue;
    var pgScale = window.PS[pg] && window.PS[pg].scale;
    var pgPpm = pgScale && pgScale.pts_per_m > 0;
    var label = 'หน้า ' + pg; // หน้า N
    // Add floor label if available
    var tg = window.pageTags && window.pageTags[pg];
    if (tg === 'floor') {
      var fk = window.pageFloorKind && window.pageFloorKind[pg];
      var fnum = window.pageFloorNum && window.pageFloorNum[pg];
      var fLabel = window.FLOOR_KIND_LABELS && fk && window.FLOOR_KIND_LABELS[fk]
                   ? window.FLOOR_KIND_LABELS[fk] : '';
      if (fLabel) label += ' — ' + fLabel + (fnum ? (' ' + fnum) : '') + (fk !== 'custom' ? '' : '');
    }
    var row = document.createElement('div');
    row.className = 'cfss-pg-row';
    if (!pgPpm) {
      row.innerHTML = '<span style="color:#ffb454">⚠ หน้า ' + pg + ' — ยังไม่มีสเกล</span>';
      row.title = 'ตั้งสเกลหน้านี้ก่อนจึงจะติดได้';
      hasNoScalePage = true;
    } else {
      var cb = document.createElement('input');
      cb.type = 'checkbox'; cb.value = pg; cb.id = 'cfss-pg-' + pg;
      var lbl = document.createElement('label');
      lbl.htmlFor = 'cfss-pg-' + pg; lbl.textContent = label; lbl.style.cursor = 'pointer';
      row.appendChild(cb); row.appendChild(lbl);
      row.addEventListener('click', function(ev) {
        if (ev.target.tagName !== 'INPUT') {
          var inp = row.querySelector('input[type=checkbox]');
          if (inp) inp.checked = !inp.checked;
        }
      });
    }
    pagesDiv.appendChild(row);
  }
  if (hasNoScalePage) {
    var warn = document.createElement('div');
    warn.className = 'cfss-pg-warn';
    warn.textContent = '⚠ หน้าที่ไม่มีสเกลจะไม่ถูกเลือก';
    pagesDiv.appendChild(warn);
  }

  overlay.appendChild(dlg);
  document.body.appendChild(overlay);
  _cfssDlgEl = overlay;

  dlg.querySelector('#cfss-cancel').addEventListener('click', function() {
    overlay.remove(); _cfssDlgEl = null;
  });
  overlay.addEventListener('click', function(e) {
    if (e.target === overlay) { overlay.remove(); _cfssDlgEl = null; }
  });

  dlg.querySelector('#cfss-install').addEventListener('click', function() {
    var nameVal = (dlg.querySelector('#cfss-name-inp').value || '').trim() || 'Master';
    var targetPgs = [];
    pagesDiv.querySelectorAll('input[type=checkbox]:checked').forEach(function(cb) {
      targetPgs.push(+cb.value);
    });
    cfssCommitPromote(sourcePoly, nameVal, targetPgs);
    overlay.remove(); _cfssDlgEl = null;
    if (typeof window.draw === 'function') window.draw();
  });
}

/* --- Edit dialog --- */
var _cfssEditDlgEl = null;

function cfssOpenEditDialog(masterId) {
  _cfssInjectDialogCSS();
  if (_cfssEditDlgEl) { _cfssEditDlgEl.remove(); _cfssEditDlgEl = null; }
  var master = masterById(masterId);
  if (!master) return;

  var isRect = _cfssIsRect(master.metricPts);
  // Compute bbox W/H from metricPts
  var wxMin = Infinity, wxMax = -Infinity, wyMin = Infinity, wyMax = -Infinity;
  (master.metricPts || []).forEach(function(p) {
    if (p.x_m < wxMin) wxMin = p.x_m; if (p.x_m > wxMax) wxMax = p.x_m;
    if (p.y_m < wyMin) wyMin = p.y_m; if (p.y_m > wyMax) wyMax = p.y_m;
  });
  var wM = isRect ? (wxMax - wxMin).toFixed(3) : '';
  var hM = isRect ? (wyMax - wyMin).toFixed(3) : '';

  var overlay = document.createElement('div');
  overlay.id = 'cfss-overlay';
  var dlg = document.createElement('div');
  dlg.id = 'cfss-dlg';

  var dimHint = isRect ? '' : '<div class="cfss-hint">ไม่ใช่สี่เหลี่ยมแกนตรง — ขนาด W/H ไม่สามารถแก้ได้</div>';
  dlg.innerHTML = [
    '<h4>✏️ แก้ไขมาสเตอร์</h4>',
    '<div class="cfss-field"><label>ชื่อ</label>',
    '<input id="cfss-edit-name" type="text" value="' + (master.name || '').replace(/"/g, '&quot;') + '"></div>',
    '<div class="cfss-field"><label>สี</label>',
    '<input id="cfss-edit-color" type="color" value="' + (master.color || '#888888') + '"></div>',
    '<div class="cfss-row">',
    '<div class="cfss-field"><label>กว้าง (m)</label>',
    '<input id="cfss-edit-w" type="number" step="0.001" min="0.001"' + (!isRect ? ' disabled' : '') + ' value="' + wM + '"></div>',
    '<div class="cfss-field"><label>สูง (m)</label>',
    '<input id="cfss-edit-h" type="number" step="0.001" min="0.001"' + (!isRect ? ' disabled' : '') + ' value="' + hM + '"></div>',
    '</div>',
    dimHint,
    '<div class="cfss-btns">',
    '<button class="cfss-btn" id="cfss-edit-cancel">ยกเลิก</button>',
    '<button class="cfss-btn pri" id="cfss-edit-save">บันทึก</button>',
    '</div>'
  ].join('');

  overlay.appendChild(dlg);
  document.body.appendChild(overlay);
  _cfssEditDlgEl = overlay;

  function closeEdit() { overlay.remove(); _cfssEditDlgEl = null; }

  dlg.querySelector('#cfss-edit-cancel').addEventListener('click', closeEdit);
  overlay.addEventListener('click', function(e) { if (e.target === overlay) closeEdit(); });
  document.addEventListener('keydown', function esc(e) {
    if (e.key === 'Escape') { closeEdit(); document.removeEventListener('keydown', esc); }
  });

  dlg.querySelector('#cfss-edit-save').addEventListener('click', function() {
    var patch = {};
    var nameVal = (dlg.querySelector('#cfss-edit-name').value || '').trim();
    if (nameVal) patch.name = nameVal;
    patch.color = dlg.querySelector('#cfss-edit-color').value;
    if (isRect) {
      var wv = parseFloat(dlg.querySelector('#cfss-edit-w').value);
      var hv = parseFloat(dlg.querySelector('#cfss-edit-h').value);
      if (wv > 0 && hv > 0) { patch.widthM = wv; patch.heightM = hv; }
    }
    cfssCommitEdit(masterId, patch);
    closeEdit();
    if (typeof window.draw === 'function') window.draw();
  });
}

// Expose on window (in case any test or future code reads these directly).
window.cfssOpenPromoteDialog = cfssOpenPromoteDialog;
window.cfssOpenEditDialog = cfssOpenEditDialog;

// Inject CSS immediately on load (idempotent inside _cfssInjectDialogCSS).
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', _cfssInjectDialogCSS);
} else {
  _cfssInjectDialogCSS();
}

/* end of idempotent guard */ }
