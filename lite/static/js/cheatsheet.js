/* LHELP-1: cheatsheet.js — F1 / ? keyboard shortcut reference panel.
   Fully self-contained: injects its own CSS, owns the overlay DOM, installs
   its own keydown listener. No edits to ui-lite.html style block needed.
   Globals declared: openCheatsheet, closeCheatsheet, toggleCheatsheet. */

/* ---------------------------------------------------------------------------
   SHORTCUTS data — only shortcuts that are ACTUALLY wired in lite.
   Verified against ui-lite.html keydown handlers, snap-types.js, ortho-mode.js.
--------------------------------------------------------------------------- */
var SHORTCUTS = {
  'เครื่องมือ': [
    ['Select',               'V'],
    ['Pan (สลับ)',           'H'],
    ['Set Scale',            'S'],
    ['Verify Scale',         '⇧S'],
    ['Polygon area',         'A'],
    ['Arc edge (ขณะวาด)',   'A → A'],
    ['Distance',             'D'],
    ['Distance (ต่อเนื่อง / Path)', '⇧D'],
    ['Reference line',       'R'],
    ['Count marker',         'N'],
    ['Finish drawing',       'Enter'],
    ['Cancel drawing',       'Esc']
  ],
  'Annotate': [
    ['ตัวหนังสือ (Text)',     '⇧T'],
    ['คอมเมนต์ (Comment)',   '⇧M'],
    ['ลูกศร (Arrow)',         '⇧A'],
    ['ไฮไลต์ (Highlight)',    '⇧H'],
    ['กรอบสี่เหลี่ยม (Rect)', '⇧R'],
    ['กรอบวงกลม (Circle)',    '⇧C'],
    ['กรอบเมฆ (Cloud)',      '⇧U']
  ],
  'Snap & helper': [
    ['Endpoint snap (toggle)',   'E'],
    ['Midpoint snap (toggle)',   'M'],
    ['Center snap (toggle)',     'C'],
    ['Disable all snaps',        'G'],
    ['Ortho mode',               '⇧O'],
    ['Loupe',                    'L']
  ],
  'หน้า / ดู': [
    ['Fit window',           'F / Ctrl+0'],
    ['Actual size',          'Ctrl+1'],
    ['Zoom in / out',        'Ctrl+ / Ctrl−'],
    ['Focus mode',           '⇧F'],
    ['Overview',             'F12'],
    ['Page Manager',         '⇧F12'],
    ['Page search',          'Ctrl+K'],
    ['Page Setup',           'Ctrl+,'],
    ['Prev / next page',     'PgUp / PgDn']
  ],
  'แก้ไข': [
    ['Undo',                 'Ctrl+Z'],
    ['Redo',                 'Ctrl+Y / ⇧Ctrl+Z'],
    ['Delete selected',      'Del'],
    ['Duplicate',            'Ctrl+D'],
    ['Save project',         'Ctrl+S'],
    ['Export XLSX',          'Ctrl+E']
  ]
};

/* ---------------------------------------------------------------------------
   CSS — injected once into <head> so ui-lite.html's style block is untouched.
--------------------------------------------------------------------------- */
(function _injectCSS() {
  var style = document.createElement('style');
  style.id = 'cheatsheet-css';
  style.textContent = [
    '.cheatsheet-backdrop{',
    '  position:fixed;inset:0;',
    '  background:rgba(0,0,0,.55);',
    '  z-index:200;',
    '  display:none;',
    '  align-items:center;justify-content:center;',
    '}',
    '.cheatsheet-backdrop.open{display:flex;}',
    '.cheatsheet-panel{',
    '  background:var(--panel,#222228);',
    '  border:1px solid var(--line,#3a3a48);',
    '  border-radius:8px;',
    '  max-width:720px;width:90vw;',
    '  max-height:80vh;overflow:auto;',
    '  padding:20px;',
    '  box-shadow:0 8px 32px rgba(0,0,0,.6);',
    '  color:var(--ink,#cdd6f4);',
    '  font-size:13px;',
    '}',
    '.cheatsheet-panel h3{',
    '  margin:0 0 16px;font-size:15px;font-weight:600;',
    '  display:flex;align-items:baseline;justify-content:space-between;',
    '}',
    '.cheatsheet-panel h3 small{',
    '  font-size:11px;color:var(--muted,#6c7086);font-weight:400;',
    '}',
    '.cheatsheet-grid{',
    '  display:grid;grid-template-columns:1fr 1fr;gap:18px;',
    '}',
    '@media(max-width:520px){.cheatsheet-grid{grid-template-columns:1fr;}}',
    '.cheatsheet-section h4{',
    '  margin:0 0 8px;font-size:12px;font-weight:600;',
    '  color:var(--accent,#89b4fa);',
    '  text-transform:uppercase;letter-spacing:.04em;',
    '}',
    '.cheatsheet-section .kv{',
    '  display:flex;justify-content:space-between;',
    '  align-items:center;',
    '  padding:2px 0;gap:8px;',
    '}',
    '.cheatsheet-section .kv span{',
    '  color:var(--muted,#6c7086);font-size:12px;flex:1;',
    '}',
    'kbd{',
    '  display:inline-block;',
    '  background:var(--panel2,#1e1e2e);',
    '  border:1px solid var(--line,#3a3a48);',
    '  border-radius:3px;',
    '  padding:1px 5px;',
    '  font-family:monospace;font-size:11px;',
    '  white-space:nowrap;',
    '  color:var(--ink,#cdd6f4);',
    '  flex-shrink:0;',
    '}'
  ].join('\n');
  document.head.appendChild(style);
})();

/* ---------------------------------------------------------------------------
   Overlay DOM — created lazily on first open.
--------------------------------------------------------------------------- */
var _csBackdrop = null;

function _buildCheatsheet() {
  if (_csBackdrop) return;

  var bd = document.createElement('div');
  bd.className = 'cheatsheet-backdrop';
  bd.setAttribute('role', 'dialog');
  bd.setAttribute('aria-modal', 'true');
  bd.setAttribute('aria-label', 'Keyboard shortcuts');

  var panel = document.createElement('div');
  panel.className = 'cheatsheet-panel';

  // Header
  var h3 = document.createElement('h3');
  h3.innerHTML = 'Keyboard Shortcuts <small>Esc หรือคลิกนอกกรอบเพื่อปิด</small>';
  panel.appendChild(h3);

  // Grid
  var grid = document.createElement('div');
  grid.className = 'cheatsheet-grid';

  Object.keys(SHORTCUTS).forEach(function (sectionName) {
    var rows = SHORTCUTS[sectionName];
    var section = document.createElement('div');
    section.className = 'cheatsheet-section';

    var h4 = document.createElement('h4');
    h4.textContent = sectionName;
    section.appendChild(h4);

    rows.forEach(function (pair) {
      var label = pair[0], key = pair[1];
      var kv = document.createElement('div');
      kv.className = 'kv';

      var sp = document.createElement('span');
      sp.textContent = label;

      var kbd = document.createElement('kbd');
      kbd.textContent = key;

      kv.appendChild(sp);
      kv.appendChild(kbd);
      section.appendChild(kv);
    });

    grid.appendChild(section);
  });

  panel.appendChild(grid);
  bd.appendChild(panel);
  document.body.appendChild(bd);

  // Click-outside closes; click inside panel does NOT close (no bubble from panel)
  bd.addEventListener('click', function (e) {
    if (e.target === bd) closeCheatsheet();
  });

  _csBackdrop = bd;
}

/* ---------------------------------------------------------------------------
   Public API
--------------------------------------------------------------------------- */
function openCheatsheet() {
  _buildCheatsheet();
  _csBackdrop.classList.add('open');
}

function closeCheatsheet() {
  if (_csBackdrop) _csBackdrop.classList.remove('open');
}

function toggleCheatsheet() {
  if (!_csBackdrop || !_csBackdrop.classList.contains('open')) {
    openCheatsheet();
  } else {
    closeCheatsheet();
  }
}

/* ---------------------------------------------------------------------------
   Keyboard listener — installed once on DOMContentLoaded.
   F1       → toggleCheatsheet  (preventDefault: browser uses F1 for help)
   ?        → toggleCheatsheet  (Shift+/ on US / Thai layouts; key === '?')
   Escape   → closeCheatsheet ONLY if overlay is open (does NOT consume otherwise)
   Guard:   skip if INPUT/TEXTAREA/contentEditable focused; skip if modalOpen()
--------------------------------------------------------------------------- */
function _isEditorFocused() {
  var ae = document.activeElement;
  if (!ae) return false;
  var tag = ae.tagName;
  if (tag === 'INPUT' || tag === 'TEXTAREA') return true;
  if (ae.isContentEditable) return true;
  return false;
}

document.addEventListener('DOMContentLoaded', function () {
  window.addEventListener('keydown', function (e) {
    // Escape: only consume if overlay is open, so other Esc handlers still run
    if (e.key === 'Escape') {
      if (_csBackdrop && _csBackdrop.classList.contains('open')) {
        e.preventDefault();
        closeCheatsheet();
      }
      return; // always let Escape propagate to other handlers unless consumed above
    }

    // F1 and ? need editable-focus + modal guard
    if (e.key === 'F1' || e.key === '?') {
      if (_isEditorFocused()) return;
      // F-7: modalOpen() now reports the cheatsheet itself as "a modal is open"
      // (so app hotkeys don't leak while it's showing). That means once open,
      // modalOpen() would always be true here too — skip the guard when the
      // cheatsheet is ALREADY open so F1/? can still toggle it CLOSED; the
      // guard still applies (blocks opening) when some OTHER modal is up.
      var alreadyOpen = _csBackdrop && _csBackdrop.classList.contains('open');
      if (!alreadyOpen && typeof modalOpen === 'function' && modalOpen()) return;
      e.preventDefault();
      toggleCheatsheet();
    }
  });
});
