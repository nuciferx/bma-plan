/* ============================================================
   OVERVIEW-SETUP — LOVS-1
   3-tab wizard (Classify → Number Floors → Review) injected into live #ov.
   Plain-globals module. No IIFE, no export, no bundler.
   Loaded dynamically from page-folder-layers.js (LOVS-1 dynamic inject).

   Globals required (ui-lite.html):
     pageTags, pageFloorNum, pageFloorKind, pageNames, pageCount, curPage,
     excluded, PS, PAGE_TAGS, state, pdfName
     liteSetTag(n,val), loadPage(n), closeOverlays(), api(path)
   Optional (page-folder-layers.js): reseedActivePageFolders()
   ============================================================ */

var _LOVS_TAG_CYCLE = ['','site','floor','plan','parking','amenity','detail'];
var _LOVS_TAG_KEYS  = {'1':'site','2':'floor','3':'plan','4':'parking','5':'amenity','6':'detail','0':''};
var _lovsOrigOpenOv = null;
var _lovsCurStep    = 1;
var _lovsFocusPage  = 1;
var _lovsSelected   = new Set();
var _lovsSelAnchor  = null;
var _lovsInited     = false;
window.__lovsSelected = _lovsSelected;

/* -- floor num writer -- */
function _lovsSetFloorNum(n, num) {
  if (num === "" || num == null) { delete pageFloorNum[n]; delete pageFloorKind[n]; return; }
  if (num === "roof" || num === "ROOF") { pageFloorNum[n] = "roof"; pageFloorKind[n] = "rooftop"; return; }
  var v = parseInt(num, 10);
  if (!isFinite(v)) { delete pageFloorNum[n]; return; }
  pageFloorNum[n] = v;
  if (!pageFloorKind[n] || pageFloorKind[n] === "rooftop") pageFloorKind[n] = "normal";
  if (typeof state !== "undefined") state.dirty = true;
}

/* -- floor kind writer (LOVS-2: basement/normal/mechanical/rooftop) --
   rooftop → auto-set pageFloorNum='roof' (no number needed)
   mechanical → clear pageFloorNum (no number needed)
   normal/basement → keep existing pageFloorNum (user types number separately) */
function _lovsSetFloorKind(n, kind) {
  if (!kind) { delete pageFloorKind[n]; delete pageFloorNum[n]; if (typeof state !== "undefined") state.dirty = true; return; }
  pageFloorKind[n] = kind;
  if (kind === "rooftop") { pageFloorNum[n] = "roof"; }
  else if (kind === "mechanical") { delete pageFloorNum[n]; }
  else if (kind === "basement" || kind === "normal") {
    // keep existing pageFloorNum if any; if it's 'roof', clear it (no longer a roof)
    if (pageFloorNum[n] === "roof") delete pageFloorNum[n];
  }
  if (typeof reseedActivePageFolders === "function" && typeof state !== "undefined" && state.pageFolderMode) reseedActivePageFolders();
  if (typeof state !== "undefined") state.dirty = true;
}

/* -- floor label resolver: kind + num → human label for chip/report -- */
function _lovsFloorLabel(n) {
  var kind = pageFloorKind[n];
  var num  = pageFloorNum[n];
  if (kind === "rooftop") return "ดาดฟ้า";
  if (kind === "mechanical") return "ห้องเครื่อง";
  if (kind === "basement") return "ใต้ดิน" + (num != null ? " " + num : "");
  if (kind === "normal") return "ชั้น " + (num != null ? num : "—");
  // legacy (no kind set, num='roof'): treat as rooftop
  if (num === "roof") return "ดาดฟ้า";
  if (num != null) return "ชั้น " + num;
  return "— ยังไม่ได้ตั้ง —";
}

/* -- CSS inject (idempotent) -- */
function _lovsInjectCSS() {
  if (document.getElementById("__lovs_css__")) return;
  var s = document.createElement("style"); s.id = "__lovs_css__";
  s.textContent =
    "#ov-panel{width:min(96vw,1280px);height:min(88vh,calc(100vh - 110px));display:flex;flex-direction:column;background:var(--panel,#161a22);border:1px solid var(--line,#2a3140);border-radius:12px;overflow:hidden}" +
    "#ov-head{display:flex;align-items:center;gap:10px;padding:10px 14px;border-bottom:1px solid var(--line,#2a3140);background:#1a1d24}" +
    "#ov-head h3{font-size:14px;font-weight:600;margin-right:8px}" +
    "#ov-head .ov-meta{color:var(--muted,#8b97a8);font-size:12px}" +
    "#ov-head .sp{flex:1}" +
    "#ov-head .kv{display:flex;gap:6px;align-items:center;font-size:11px;color:var(--muted,#8b97a8);margin-left:4px}" +
    "#ov-head .kv b{color:var(--ink,#e7ecf3);font-variant-numeric:tabular-nums}" +
    "#ov-head .kv b.acc{color:var(--accent,#4c8dff)}" +
    "#ov-head button{background:#2d3036;color:var(--ink,#e7ecf3);border:1px solid var(--line,#2a3140);padding:5px 11px;border-radius:5px;cursor:pointer;font-size:12px}" +
    "#ov-head button:hover{background:#343841}" +
    "#ov-steps{display:flex;border-bottom:1px solid var(--line,#2a3140);background:#11141a}" +
    "#ov-steps .step{flex:1;padding:9px 14px;border-right:1px solid var(--line,#2a3140);display:flex;align-items:center;gap:9px;cursor:pointer;color:var(--muted,#8b97a8);font-size:12px;user-select:none}" +
    "#ov-steps .step:last-child{border-right:0}" +
    "#ov-steps .step.act{background:var(--panel,#161a22);color:var(--ink,#e7ecf3)}" +
    "#ov-steps .step.done{color:var(--good,#39d98a)}" +
    "#ov-steps .step .num{width:22px;height:22px;border-radius:50%;background:#2d3036;border:1px solid var(--line,#2a3140);display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700}" +
    "#ov-steps .step.act .num{background:var(--accent,#4c8dff);color:#001218;border-color:var(--accent,#4c8dff)}" +
    "#ov-steps .step.done .num{background:var(--good,#39d98a);color:#011;border-color:var(--good,#39d98a)}" +
    "#ov-steps .step .lbl b{display:block;color:inherit;font-size:12px}" +
    "#ov-steps .step .lbl span{display:block;color:var(--muted,#8b97a8);font-size:10px;margin-top:1px}" +
    ".ov-hint{padding:7px 14px;font-size:11px;color:var(--muted,#8b97a8);background:#10131a;border-bottom:1px solid var(--line,#2a3140);display:flex;gap:14px;align-items:center;flex-wrap:wrap}" +
    ".ov-hint kbd{background:#26282d;border:1px solid var(--line,#2a3140);padding:1px 6px;border-radius:3px;font-family:ui-monospace,monospace;font-size:10px;color:var(--ink,#e7ecf3)}" +
    ".ov-hint .legend{display:flex;gap:5px;flex-wrap:wrap;align-items:center}" +
    "#ov-panel .tab-body{flex:1;overflow:auto;padding:0;display:none;position:relative}" +
    "#ov-panel .tab-body.act{display:block}" +
    "#grid-classify{padding:12px 14px;display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px;position:relative;min-height:100%}" +
    ".ov-tile{background:#0c0f14;border:2px solid var(--line,#2a3140);border-radius:8px;overflow:hidden;display:flex;flex-direction:column;cursor:pointer;transition:transform .08s,border-color .1s;position:relative;user-select:none}" +
    ".ov-tile:hover{transform:translateY(-1px);border-color:#3a4150}" +
    ".ov-tile.cur{border-color:var(--accent,#4c8dff);box-shadow:0 0 0 2px rgba(76,141,255,.25)}" +
    ".ov-tile.foc{border-color:var(--warn,#ffb454);box-shadow:0 0 0 2px rgba(255,180,84,.35)}" +
    ".ov-tile.sel{border-color:var(--accent,#4c8dff);background:#16263d;box-shadow:0 0 0 2px rgba(76,141,255,.45)}" +
    ".ov-tile.foc.sel{border-color:var(--warn,#ffb454);box-shadow:0 0 0 2px rgba(255,180,84,.5)}" +
    ".ov-tile.exc{opacity:.45}" +
    ".ov-tile .thumb{height:78px;background:#1a212c;display:flex;align-items:center;justify-content:center;color:var(--muted,#8b97a8);font-size:22px;position:relative;border-bottom:1px solid var(--line,#2a3140);pointer-events:none;overflow:hidden}" +
    ".ov-thumb-img{width:100%;height:78px;object-fit:cover;display:block;background:#1a212c;position:absolute;inset:0}" +
    ".ov-tile .pn{position:absolute;top:4px;left:6px;background:rgba(0,0,0,.7);padding:1px 5px;border-radius:3px;font-size:10px;color:var(--ink,#e7ecf3);font-weight:600;z-index:2}" +
    ".ov-tile .objc{position:absolute;top:4px;right:6px;background:rgba(57,217,138,.85);color:#001;padding:1px 5px;border-radius:3px;font-size:9px;font-weight:700;z-index:2}" +
    ".ov-tile .selchk{position:absolute;bottom:4px;left:6px;background:var(--accent,#4c8dff);color:#fff;padding:0 5px;border-radius:3px;font-size:9px;font-weight:700;display:none;z-index:2}" +
    ".ov-tile.sel .selchk{display:block}" +
    ".ov-tile .info{padding:5px 7px;display:flex;flex-direction:column;gap:4px;min-height:62px}" +
    ".ov-tile .nm{font-size:11px;color:var(--ink,#e7ecf3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:600}" +
    ".ov-tile .row{display:flex;gap:4px;align-items:center}" +
    ".ov-tag-chip{padding:2px 7px;border-radius:9px;font-size:10px;font-weight:600;color:#001218;cursor:pointer;white-space:nowrap;flex:1;text-align:center;line-height:1.4}" +
    ".ov-tag-chip:hover{outline:1px solid var(--accent,#4c8dff);outline-offset:1px}" +
    ".ov-tag-untagged{background:#2a2f38;color:var(--muted,#8b97a8);border:1px dashed var(--muted,#8b97a8)}" +
    ".ov-tag-site{background:#9ad14b}.ov-tag-floor{background:#4cc9f0;color:#001218}.ov-tag-plan{background:#8da4be;color:#001218}" +
    ".ov-tag-parking{background:#c87cae;color:#fff}.ov-tag-amenity{background:#d49a3b}.ov-tag-detail{background:#cf6f44;color:#fff}" +
    ".ov-floor-input{background:#1a1c20;border:1px solid var(--line,#2a3140);color:var(--ink,#e7ecf3);padding:2px 5px;border-radius:3px;font-size:11px;width:42px;text-align:center;font-variant-numeric:tabular-nums;flex:0 0 auto}" +
    ".ov-floor-input:focus{outline:1px solid var(--accent,#4c8dff);border-color:var(--accent,#4c8dff)}" +
    ".ov-fkind-sel{background:#1a1c20;border:1px solid var(--line,#2a3140);color:var(--ink,#e7ecf3);padding:2px 4px;border-radius:3px;font-size:10px;flex:1 1 auto;min-width:0;max-width:100%;cursor:pointer}" +
    ".ov-fkind-sel:focus{outline:1px solid var(--accent,#4c8dff);border-color:var(--accent,#4c8dff)}" +
    ".ov-floor-lab{font-size:10px;color:var(--muted,#8b97a8);margin-right:2px}" +
    ".ov-excl-btn{font-size:10px;color:var(--muted,#8b97a8);background:transparent;border:1px solid var(--line,#2a3140);border-radius:3px;padding:1px 5px;cursor:pointer}" +
    ".ov-excl-btn:hover{color:var(--bad,#ff6b6b);border-color:var(--bad,#ff6b6b)}" +
    ".ov-tile.exc .ov-excl-btn{color:var(--bad,#ff6b6b)}" +
    "#ov-dragbox{position:absolute;border:1px dashed var(--accent,#4c8dff);background:rgba(76,141,255,.1);pointer-events:none;z-index:5;display:none}" +
    "#bulkbar{position:sticky;top:0;left:0;right:0;background:linear-gradient(to bottom,#1a1d24f0,#11141af0);border-bottom:1px solid var(--accent,#4c8dff);padding:7px 14px;display:flex;align-items:center;gap:10px;font-size:12px;color:var(--ink,#e7ecf3);z-index:8;backdrop-filter:blur(4px)}" +
    "#bulkbar.hide{display:none}" +
    "#bulkbar .ct{color:var(--accent,#4c8dff);font-weight:700}" +
    "#bulkbar button{background:#2d3036;color:var(--ink,#e7ecf3);border:1px solid var(--line,#2a3140);padding:4px 9px;border-radius:4px;cursor:pointer;font-size:11px}" +
    "#bulkbar button:hover{background:#343841}" +
    "#bulkbar .ov-tag-chip{cursor:pointer;font-size:10px}" +
    "#tab-floors{padding:16px 22px}" +
    "#tab-floors .seq-bar{display:flex;align-items:center;gap:10px;background:#1a1d24;padding:10px 14px;border-radius:6px;margin-bottom:12px;border:1px solid var(--line,#2a3140)}" +
    "#tab-floors .seq-bar label{font-size:11px;color:var(--muted,#8b97a8)}" +
    "#tab-floors .seq-bar input{background:#0c0f14;color:var(--ink,#e7ecf3);border:1px solid var(--line,#2a3140);padding:4px 8px;width:60px;text-align:center;border-radius:3px;font-size:12px}" +
    "#tab-floors .seq-bar button{background:var(--accent,#4c8dff);color:#fff;border:0;padding:6px 14px;border-radius:4px;cursor:pointer;font-size:11px;font-weight:600}" +
    "#tab-floors .seq-bar button:hover{background:#3a7fe8}" +
    "#tab-floors .seq-bar button.sec{background:#2d3036;color:var(--ink,#e7ecf3);border:1px solid var(--line,#2a3140);font-weight:400}" +
    "#tab-floors .seq-bar button.sec:hover{background:#343841}" +
    "#floor-strip{display:flex;gap:10px;flex-wrap:wrap;padding:14px;background:#1a1d24;border:1px solid var(--line,#2a3140);border-radius:6px;min-height:140px;align-items:flex-start}" +
    ".fchip{background:#0c0f14;border:1px solid var(--line,#2a3140);border-radius:8px;padding:10px 12px;display:flex;flex-direction:column;align-items:center;gap:4px;cursor:grab;min-width:100px;position:relative}" +
    ".fchip:active{cursor:grabbing}.fchip.drg{opacity:.35}.fchip.over{border-color:var(--accent,#4c8dff);background:#16263d}" +
    ".fchip .num{font-size:20px;font-weight:700;color:var(--accent,#4c8dff);font-variant-numeric:tabular-nums}" +
    ".fchip.spec .num{color:var(--warn,#ffb454);font-size:14px}" +
    ".fchip .pg{font-size:10px;color:var(--muted,#8b97a8)}" +
    ".fchip .lb{font-size:10px;color:var(--ink,#e7ecf3);max-width:90px;text-align:center;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}" +
    ".fchip .clr{position:absolute;top:3px;right:5px;font-size:10px;color:var(--muted,#8b97a8);cursor:pointer;background:transparent;border:0;padding:0;line-height:1}" +
    ".fchip .clr:hover{color:var(--bad,#ff6b6b)}.fchip.empty .num{color:var(--muted,#8b97a8);font-size:14px}" +
    ".fhint{padding:10px 14px;background:#1a1d24;border:1px solid var(--line,#2a3140);border-left:3px solid var(--accent,#4c8dff);border-radius:6px;margin-bottom:10px;font-size:11px;color:var(--muted,#8b97a8);line-height:1.5}" +
    ".fhint b{color:var(--ink,#e7ecf3)}.fhint code{background:#0c0f14;padding:1px 5px;border-radius:3px;color:var(--accent,#4c8dff);font-size:11px}" +
    "#tab-review{padding:16px 22px}" +
    ".report{background:#fff;color:#222;border-radius:6px;padding:28px 36px;max-width:820px;margin:0 auto;font-family:'Sarabun','Tahoma',sans-serif;box-shadow:0 6px 24px rgba(0,0,0,.4)}" +
    ".report h1{font-size:18px;margin:0 0 4px;color:#0c2b3a}" +
    ".report h2{font-size:14px;border-bottom:2px solid #0c2b3a;padding-bottom:3px;color:#0c2b3a;margin:16px 0 6px;font-weight:600}" +
    ".report .sub{color:#666;font-size:11px;margin-bottom:12px}" +
    ".report table{width:100%;border-collapse:collapse;font-size:11px;margin:5px 0}" +
    ".report th,.report td{border:1px solid #ccc;padding:4px 7px;text-align:left}" +
    ".report th{background:#eef2f5;font-weight:600}.report td.num{text-align:right;font-variant-numeric:tabular-nums}" +
    ".report .tot{font-weight:700;background:#f8f8f8}" +
    ".report .pl{display:flex;flex-wrap:wrap;gap:3px;margin:4px 0 8px}" +
    ".report .pl span{background:#eef2f5;padding:1px 6px;border-radius:8px;font-size:10px;color:#345}" +
    ".report .pl span.exc{background:#f8e0e0;color:#722}" +
    ".report .calc{background:#fffaef;border:1px solid #f0d59c;padding:10px 14px;margin:8px 0;font-size:11px;border-radius:4px}" +
    ".report .calc .row{display:flex;justify-content:space-between;padding:2px 0}" +
    ".report .calc .row.tot{border-top:1px solid #d4b870;padding-top:5px;margin-top:4px;font-weight:700}" +
    ".report .warn{color:#a04;padding:6px 10px;background:#fde;border:1px solid #f9c;border-radius:4px;margin:8px 0;font-size:11px}" +
    "#ov-nav{display:flex;gap:8px;padding:10px 14px;border-top:1px solid var(--line,#2a3140);background:#11141a;align-items:center}" +
    "#ov-nav .sp{flex:1}" +
    "#ov-nav button{background:#2d3036;color:var(--ink,#e7ecf3);border:1px solid var(--line,#2a3140);padding:7px 16px;border-radius:5px;cursor:pointer;font-size:12px}" +
    "#ov-nav button:hover{background:#343841}" +
    "#ov-nav button.pri{background:var(--accent,#4c8dff);border-color:var(--accent,#4c8dff);color:#fff;font-weight:600}" +
    "#ov-nav button.pri:hover{background:#3a7fe8}" +
    "#ov-nav button:disabled{opacity:.4;cursor:not-allowed}" +
    "#ov-nav .prog{color:var(--muted,#8b97a8);font-size:11px;font-variant-numeric:tabular-nums}" +
    "#ov-ctxmenu{position:fixed;background:var(--panel,#161a22);border:1px solid var(--line,#2a3140);border-radius:6px;padding:4px;z-index:200;box-shadow:0 6px 24px rgba(0,0,0,.6);min-width:170px;display:none}" +
    "#ov-ctxmenu .it{padding:5px 9px;border-radius:4px;cursor:pointer;font-size:12px;display:flex;justify-content:space-between;gap:10px}" +
    "#ov-ctxmenu .it:hover{background:#343841}" +
    "#ov-ctxmenu .it .k{color:var(--muted,#8b97a8);font-size:10px;font-family:ui-monospace,monospace}" +
    "#ov-ctxmenu .sep{height:1px;background:var(--line,#2a3140);margin:3px 2px}";
  document.head.appendChild(s);
}

/* -- panel HTML builder -- */
function _lovsBuiltPanelHTML() {
  return '<div id="ov-panel">' +
    '<div id="ov-head">' +
      '<h3>Overview · Page Setup Wizard</h3>' +
      '<span class="ov-meta" id="ovh-meta">—</span>' +
      '<div class="kv">tagged <b id="ovh-tagged" class="acc">0/0</b></div>' +
      '<div class="kv">floors <b id="ovh-floors">0</b></div>' +
      '<div class="kv">numbered <b id="ovh-num">0</b></div>' +
      '<span class="sp"></span>' +
      '<button id="ov-close">✕ ปิด (Esc)</button>' +
    '</div>' +
    '<div id="ov-steps">' +
      '<div class="step act" data-step="1"><span class="num">1</span><span class="lbl"><b>Classify</b><span>ติด tag ทุกหน้า</span></span></div>' +
      '<div class="step" data-step="2"><span class="num">2</span><span class="lbl"><b>Number Floors</b><span>ลำดับชั้น</span></span></div>' +
      '<div class="step" data-step="3"><span class="num">3</span><span class="lbl"><b>Review</b><span>ตรวจรายงาน</span></span></div>' +
    '</div>' +
    '<div class="tab-body act" data-tab="1">' +
      '<div class="ov-hint"><span>คลิก=เลือก · <kbd>Shift</kbd>+คลิก=ช่วง · <kbd>Ctrl</kbd>+คลิก=toggle</span>' +
        '<span class="legend"><kbd>1</kbd><span class="ov-tag-chip ov-tag-site">site</span>' +
        '<kbd>2</kbd><span class="ov-tag-chip ov-tag-floor">floor</span>' +
        '<kbd>3</kbd><span class="ov-tag-chip ov-tag-plan">plan</span>' +
        '<kbd>4</kbd><span class="ov-tag-chip ov-tag-parking">parking</span>' +
        '<kbd>5</kbd><span class="ov-tag-chip ov-tag-amenity">amenity</span>' +
        '<kbd>6</kbd><span class="ov-tag-chip ov-tag-detail">detail</span>' +
        '<kbd>0</kbd><span style="color:var(--muted,#8b97a8);font-size:10px">ล้าง</span>' +
        '<kbd>X</kbd><span style="color:var(--muted,#8b97a8);font-size:10px">exclude</span>' +
        '<kbd>Ctrl+A</kbd><span style="color:var(--muted,#8b97a8);font-size:10px">ทั้งหมด</span></span>' +
      '</div>' +
      '<div id="grid-classify"></div><div id="ov-dragbox"></div>' +
    '</div>' +
    '<div class="tab-body" data-tab="2" id="tab-floors">' +
      '<div class="fhint"><b>Number Floors</b> — แสดงเฉพาะหน้า <code>tag=floor</code>. <b>ลากเรียง</b> ซ้าย=ล่าง → ขวา=บน. กดปุ่ม <b>⚡ Sequential</b> auto-assign 1→N</div>' +
      '<div class="seq-bar"><label>เริ่มที่ชั้น <input type="number" id="seq-start" value="1" min="-5" max="50"></label>' +
        '<button id="ov-seq">⚡ Sequential</button><button id="ov-clear-floor" class="sec">↺ ล้างเลขชั้น</button>' +
        '<span style="flex:1"></span><label>หน้า floor: <span id="fcount" style="color:var(--accent,#4c8dff);font-weight:600">—</span></label>' +
      '</div><div id="floor-strip"></div>' +
    '</div>' +
    '<div class="tab-body" data-tab="3" id="tab-review"><div class="report" id="report"></div></div>' +
    '<div id="ov-nav">' +
      '<button id="ov-prev">← ย้อน</button><span class="prog" id="ov-prog">Step 1 of 3</span>' +
      '<span class="sp"></span><span class="prog" id="ov-step-prog"></span>' +
      '<button id="ov-export" style="display:none">📄 ส่งออก PDF</button>' +
      '<button id="ov-next" class="pri">ถัดไป →</button>' +
    '</div>' +
  '</div><div id="ov-ctxmenu"></div>';
}

/* -- init panel once -- */
function _lovsInitPanel() {
  if (_lovsInited) return;
  _lovsInited = true;
  var ov = document.getElementById("ov");
  if (!ov) return;
  ov.innerHTML = _lovsBuiltPanelHTML();
  _lovsWireNav();
  _lovsWireKeyboard();
  document.addEventListener("click", function(e) { if (!e.target.closest("#ov-ctxmenu")) _lovsHideCtx(); });
}

/* -- wrapped openOv -- */
function _lovsOpenOv() {
  if (typeof caseId !== "undefined" && !caseId) return;
  _lovsInitPanel();
  _lovsFocusPage = (typeof curPage !== "undefined" && curPage) ? curPage : 1;
  _lovsSelected.clear(); _lovsSelAnchor = null;
  var ov = document.getElementById("ov");
  if (ov) ov.classList.add("show");
  _lovsGoStep(1);
}

/* -- step nav -- */
function _lovsGoStep(s) {
  if (s < 1 || s > 3) return;
  _lovsCurStep = s;
  document.querySelectorAll("#ov-steps .step").forEach(function(el, i) {
    el.classList.toggle("act", i + 1 === s);
    el.classList.toggle("done", i + 1 < s);
  });
  document.querySelectorAll("#ov-panel .tab-body").forEach(function(el) {
    el.classList.toggle("act", +el.dataset.tab === s);
  });
  var pe = document.getElementById("ov-prog"); if (pe) pe.textContent = "Step " + s + " of 3";
  var prev = document.getElementById("ov-prev"); if (prev) prev.disabled = s === 1;
  var next = document.getElementById("ov-next");
  if (next) { next.disabled = false; next.className = "pri";
    next.textContent = s === 3 ? "เสร็จ ✓" : s === 2 ? "ถัดไป → Review" : "ถัดไป →"; }
  /* Export button visible only on Step 3 (Review) */
  var exp = document.getElementById("ov-export");
  if (exp) exp.style.display = s === 3 ? "" : "none";
  _lovsRenderCurStep();
}

function _lovsRenderCurStep() {
  if (_lovsCurStep === 1) _lovsRenderClassify();
  else if (_lovsCurStep === 2) _lovsRenderFloors();
  else _lovsRenderReview();
  _lovsUpdateHeader();
}

function _lovsUpdateHeader() {
  var pc = (typeof pageCount !== "undefined") ? pageCount : 0;
  var tagged = 0, floors = 0, numbered = 0;
  for (var n = 1; n <= pc; n++) {
    var t = pageTags[n] || "";
    if (t) tagged++;
    if (t === "floor") { floors++; if (pageFloorNum[n] !== undefined) numbered++; }
  }
  var m = document.getElementById("ovh-meta"); if (m) m.textContent = (typeof pdfName !== "undefined" && pdfName) ? pdfName : "";
  var te = document.getElementById("ovh-tagged"); if (te) te.textContent = tagged + "/" + pc;
  var fe = document.getElementById("ovh-floors"); if (fe) fe.textContent = floors;
  var ne = document.getElementById("ovh-num"); if (ne) ne.textContent = numbered + "/" + floors;
  var sp = document.getElementById("ov-step-prog");
  if (sp) sp.textContent = _lovsCurStep === 1 ? "tagged " + tagged + "/" + pc : _lovsCurStep === 2 ? "numbered " + numbered + "/" + floors : "";
}

/* ============================================================  STEP 1 */
function _lovsRenderClassify() {
  var g = document.getElementById("grid-classify"); if (!g) return;
  var pc = (typeof pageCount !== "undefined") ? pageCount : 0;
  var pt = (typeof PAGE_TAGS !== "undefined") ? PAGE_TAGS : {};
  var h = "";
  /* LFLOOR-1c: pre-compute per-tag sequence (excl floor + excluded pages).
     _tagSeq[n] = 1-based position within its tag; _tagTot[tag] = total */
  var _tagSeq = {}, _tagTot = {};
  for (var ti = 1; ti <= pc; ti++) {
    var ttag = pageTags[ti];
    if (!ttag || ttag === "floor" || excluded[ti]) continue;
    _tagTot[ttag] = (_tagTot[ttag] || 0) + 1;
    _tagSeq[ti] = _tagTot[ttag];
  }
  if (_lovsSelected.size >= 2) {
    h += '<div id="bulkbar"><span>เลือก <span class="ct">' + _lovsSelected.size + '</span> หน้า</span>' +
      '<button id="bulk-clearsel">ล้าง (Esc)</button><span style="opacity:.5">|</span>';
    _LOVS_TAG_CYCLE.filter(function(t) { return t; }).forEach(function(t) {
      h += '<span class="ov-tag-chip ov-tag-' + t + '" data-bulk-tag="' + t + '">' + t + '</span>';
    });
    h += '<span class="ov-tag-chip ov-tag-untagged" data-bulk-tag="">ล้าง</span>' +
      '<span style="opacity:.5">|</span><button id="bulk-excl">⛔ exclude</button></div>';
  }
  for (var n = 1; n <= pc; n++) {
    var tag = pageTags[n] || "";
    var tagLbl = tag ? (pt[tag] || tag) : "— ไม่ระบุ —";
    var fl = pageFloorNum[n];
    var flStr = fl === undefined ? "" : (fl === "roof" ? "roof" : String(fl));
    /* Default kind=normal for any tag=floor page that hasn't been classified yet — so the
       floor-input always shows (existing test classifyRendersTiles expects hasFloorInput4). */
    var fkind = pageFloorKind[n] || (fl === "roof" ? "rooftop" : "normal");
    var fkindNeedsNum = (fkind === "normal" || fkind === "basement");
    var objc = (PS[n] && PS[n].objects && PS[n].objects.length) ? PS[n].objects.length : 0;
    var thumbUrl = (typeof api === "function") ? api("/thumb/" + n) : ""; // LPM slice 4+: route through pageMgr.serverNum(n) once mutations exist
    var cls = "ov-tile" + ((typeof curPage !== "undefined" && n === curPage) ? " cur" : "") +
      (n === _lovsFocusPage ? " foc" : "") + (excluded[n] ? " exc" : "") + (_lovsSelected.has(n) ? " sel" : "");
    h += '<div class="' + cls + '" data-pg="' + n + '">' +
      '<div class="thumb">' +
        (thumbUrl ? '<img class="ov-thumb-img" loading="lazy" src="' + thumbUrl + '" alt="p' + n + '" onerror="this.style.display=\'none\'">' : "") +
        '<span class="pn">p' + n + '</span>' + (objc ? '<span class="objc">' + objc + '</span>' : "") +
        '<span class="selchk">✓</span>' + (thumbUrl ? "" : "📄") +
      '</div><div class="info">' +
        '<div class="nm">หน้า ' + n + (pageNames[n] ? ' · ' + pageNames[n] : '') + '</div>' +
        '<div class="row"><span class="ov-tag-chip ov-tag-' + (tag || "untagged") + '" data-tag="' + tag + '">' + tagLbl + '</span></div>' +
        '<div class="row" style="justify-content:space-between">' +
          (tag === "floor"
            ? '<select class="ov-fkind-sel" data-fkind="' + n + '" title="ประเภทชั้น">' +
                '<option value="normal"'     + (fkind === "normal"     ? " selected" : "") + '>🏢 ชั้น</option>' +
                '<option value="basement"'   + (fkind === "basement"   ? " selected" : "") + '>⬇ ใต้ดิน</option>' +
                '<option value="mezzanine"'  + (fkind === "mezzanine"  ? " selected" : "") + '>🪜 ชั้นลอย</option>' +
                '<option value="mechanical"' + (fkind === "mechanical" ? " selected" : "") + '>⚙ ห้องเครื่อง</option>' +
                '<option value="rooftop"'    + (fkind === "rooftop"    ? " selected" : "") + '>⛅ ดาดฟ้า</option>' +
              '</select>' +
              (fkindNeedsNum
                ? '<input class="ov-floor-input" type="text" value="' + (fl != null && fl !== "roof" ? flStr : "") + '" placeholder="N" data-floor="' + n + '" title="เลขชั้น">'
                : '<span style="flex:0 0 50px;text-align:center;color:var(--muted,#8b97a8);font-size:10px">' + (fkind === "rooftop" ? "ROOF" : fkind === "mezzanine" ? "MEZ" : "MEC") + '</span>')
            : (tag && _tagSeq[n]
                ? '<span style="flex:1;text-align:center;color:var(--accent,#4c8dff);font-size:11px;font-weight:600;font-variant-numeric:tabular-nums" title="ลำดับใน tag ' + tag + '">#' + _tagSeq[n] + '/' + _tagTot[tag] + '</span>'
                : '<span style="flex:1"></span>')) +
          '<button class="ov-excl-btn" data-excl="' + n + '">' + (excluded[n] ? "⛔" : "·") + '</button>' +
        '</div>' +
      '</div></div>';
  }
  g.innerHTML = h;
  _lovsWireClassify();
}

function _lovsWireClassify() {
  var g = document.getElementById("grid-classify"); if (!g) return;
  g.querySelectorAll(".ov-tile").forEach(function(tile) {
    var pn = +tile.dataset.pg;
    tile.addEventListener("mousedown", function(e) {
      if (e.button !== 0 || e.target.closest(".ov-tag-chip") || e.target.closest(".ov-floor-input") || e.target.closest(".ov-fkind-sel") || e.target.closest(".ov-excl-btn")) return;
      e.stopPropagation();
    });
    tile.addEventListener("click", function(e) {
      if (e.target.closest(".ov-tag-chip") || e.target.closest(".ov-floor-input") || e.target.closest(".ov-fkind-sel") || e.target.closest(".ov-excl-btn")) return;
      if (e.shiftKey && _lovsSelAnchor != null) {
        var lo = Math.min(_lovsSelAnchor, pn), hi = Math.max(_lovsSelAnchor, pn);
        _lovsSelected.clear(); for (var i = lo; i <= hi; i++) _lovsSelected.add(i);
        _lovsFocusPage = pn;
      } else if (e.ctrlKey || e.metaKey) {
        if (_lovsSelected.has(pn)) _lovsSelected.delete(pn); else _lovsSelected.add(pn);
        _lovsSelAnchor = pn; _lovsFocusPage = pn;
      } else {
        _lovsSelected.clear(); _lovsSelected.add(pn); _lovsSelAnchor = pn; _lovsFocusPage = pn;
      }
      _lovsRenderClassify();
    });
    tile.addEventListener("dblclick", function(e) {
      if (e.target.closest(".ov-floor-input")) return;
      // BUG-20260526-lite-wizard-followup (A): block dblclick escape during initial setup.
      // LWIZ lock active means user must finish Page Setup before navigating to any PDF page.
      if (window.__lwizAutoLockActive) {
        if (typeof _lwizShowBlockHint === "function") _lwizShowBlockHint();
        return;
      }
      if (typeof loadPage === "function") loadPage(pn);
      if (typeof closeOverlays === "function") closeOverlays();
      _lovsSelected.clear();
    });
    var chip = tile.querySelector(".ov-tag-chip");
    if (chip) {
      chip.addEventListener("click", function(e) { e.stopPropagation(); _lovsCycleTag(pn); });
      chip.addEventListener("contextmenu", function(e) { e.preventDefault(); e.stopPropagation(); _lovsShowCtxMenu(e, pn); });
    }
    var fi = tile.querySelector(".ov-floor-input");
    if (fi) {
      fi.addEventListener("mousedown", function(e) { e.stopPropagation(); });
      fi.addEventListener("click", function(e) { e.stopPropagation(); });
      fi.addEventListener("change", function() { _lovsSetFloorNum(pn, fi.value.trim()); _lovsRenderClassify(); });
      fi.addEventListener("keydown", function(e) { if (e.key === "Enter") fi.blur(); });
    }
    var fk = tile.querySelector(".ov-fkind-sel");
    if (fk) {
      fk.addEventListener("mousedown", function(e) { e.stopPropagation(); });
      fk.addEventListener("click", function(e) { e.stopPropagation(); });
      fk.addEventListener("change", function() { _lovsSetFloorKind(pn, fk.value); _lovsRenderClassify(); });
    }
    var eb = tile.querySelector(".ov-excl-btn");
    if (eb) eb.addEventListener("click", function(e) { e.stopPropagation(); excluded[pn] = !excluded[pn]; _lovsRenderClassify(); });
  });
  var bb = document.getElementById("bulkbar");
  if (bb) {
    bb.querySelectorAll("[data-bulk-tag]").forEach(function(chip) {
      chip.addEventListener("click", function() {
        var t = chip.dataset.bulkTag;
        _lovsSelected.forEach(function(n) { liteSetTag(n, t); });
        _lovsRenderClassify();
      });
    });
    var bcs = document.getElementById("bulk-clearsel"); if (bcs) bcs.addEventListener("click", function() { _lovsSelected.clear(); _lovsRenderClassify(); });
    var bex = document.getElementById("bulk-excl");
    if (bex) bex.addEventListener("click", function() {
      var any = false; _lovsSelected.forEach(function(n) { if (excluded[n]) any = true; });
      _lovsSelected.forEach(function(n) { excluded[n] = !any; }); _lovsRenderClassify();
    });
  }
  _lovsWireDragBox();
}

function _lovsWireDragBox() {
  var g = document.getElementById("grid-classify"), box = document.getElementById("ov-dragbox");
  if (!g || !box) return;
  var ds = null, drg = false, addM = false;
  g.addEventListener("mousedown", function(e) {
    if (e.target !== g || e.button !== 0) return;
    addM = e.ctrlKey || e.metaKey; if (!addM) _lovsSelected.clear();
    var gr = g.getBoundingClientRect();
    ds = {x: e.clientX - gr.left + g.scrollLeft, y: e.clientY - gr.top + g.scrollTop}; drg = false;
  });
  g.addEventListener("mousemove", function(e) {
    if (!ds) return;
    var gr = g.getBoundingClientRect();
    var x = e.clientX - gr.left + g.scrollLeft, y = e.clientY - gr.top + g.scrollTop;
    if (!drg && (Math.abs(x - ds.x) > 4 || Math.abs(y - ds.y) > 4)) drg = true;
    if (drg) {
      var lx = Math.min(x, ds.x), ly = Math.min(y, ds.y), w = Math.abs(x - ds.x), h = Math.abs(y - ds.y);
      box.style.cssText = "display:block;left:" + lx + "px;top:" + ly + "px;width:" + w + "px;height:" + h + "px";
      var sel = addM ? new Set(_lovsSelected) : new Set();
      g.querySelectorAll(".ov-tile").forEach(function(tile) {
        var tr = tile.getBoundingClientRect();
        var tx = tr.left - gr.left + g.scrollLeft, ty = tr.top - gr.top + g.scrollTop;
        if (tx + tr.width > lx && tx < lx + w && ty + tr.height > ly && ty < ly + h) sel.add(+tile.dataset.pg);
      });
      _lovsSelected = sel; window.__lovsSelected = _lovsSelected;
      g.querySelectorAll(".ov-tile").forEach(function(tile) { tile.classList.toggle("sel", _lovsSelected.has(+tile.dataset.pg)); });
    }
  });
  g.addEventListener("mouseup", function(e) {
    box.style.display = "none";
    if (ds && drg) { if (_lovsSelected.size) { var mn = Infinity; _lovsSelected.forEach(function(n) { if (n < mn) mn = n; }); _lovsSelAnchor = mn; } _lovsRenderClassify(); }
    else if (ds && !drg && e.target === g) { _lovsSelected.clear(); _lovsSelAnchor = null; _lovsRenderClassify(); }
    ds = null; drg = false;
  });
}

function _lovsCycleTag(pn) {
  var cur = pageTags[pn] || "", i = _LOVS_TAG_CYCLE.indexOf(cur);
  liteSetTag(pn, _LOVS_TAG_CYCLE[(i + 1) % _LOVS_TAG_CYCLE.length]);
  _lovsFocusPage = pn; _lovsRenderClassify();
}

function _lovsSetTagViaKey(k) {
  if (!(k in _LOVS_TAG_KEYS)) return false;
  var t = _LOVS_TAG_KEYS[k], pc = (typeof pageCount !== "undefined") ? pageCount : 0;
  if (_lovsSelected.size > 1) { _lovsSelected.forEach(function(n) { liteSetTag(n, t); }); _lovsRenderClassify(); return true; }
  if (!_lovsFocusPage) return false;
  liteSetTag(_lovsFocusPage, t);
  if (_lovsFocusPage < pc) _lovsFocusPage++;
  _lovsSelected.clear(); _lovsSelected.add(_lovsFocusPage); _lovsSelAnchor = _lovsFocusPage;
  _lovsRenderClassify();
  var el = document.querySelector('#grid-classify .ov-tile[data-pg="' + _lovsFocusPage + '"]');
  if (el) el.scrollIntoView({block: "nearest"});
  return true;
}

/* -- context menu -- */
function _lovsShowCtxMenu(e, pn) {
  var m = document.getElementById("ov-ctxmenu"); if (!m) return;
  var targets = _lovsSelected.has(pn) ? (function() { var a = []; _lovsSelected.forEach(function(n) { a.push(n); }); return a; })() : [pn];
  var pt = (typeof PAGE_TAGS !== "undefined") ? PAGE_TAGS : {};
  var h = targets.length > 1 ? '<div style="padding:4px 9px;font-size:10px;color:var(--muted,#8b97a8)">ทำกับ ' + targets.length + ' หน้า</div><div class="sep"></div>' : "";
  _LOVS_TAG_CYCLE.forEach(function(k) {
    var lbl = k ? (pt[k] || k) : "— ล้าง tag —";
    var cur = targets.length === 1 && (pageTags[targets[0]] || "") === k ? " ✓" : "";
    var ky = k ? ((Object.entries(_LOVS_TAG_KEYS).find(function(kv) { return kv[1] === k; }) || [])[0] || "") : "0";
    h += '<div class="it" data-ctx-tag="' + k + '"><span>' + lbl + cur + '</span><span class="k">' + ky + '</span></div>';
  });
  h += '<div class="sep"></div><div class="it" data-ctx-act="excl"><span>toggle exclude</span><span class="k">X</span></div>';
  if (targets.length === 1) h += '<div class="it" data-ctx-act="goto"><span>ไปหน้านี้</span><span class="k">Enter</span></div>';
  m.innerHTML = h; m.style.left = e.clientX + "px"; m.style.top = e.clientY + "px"; m.style.display = "block";
  m.querySelectorAll(".it").forEach(function(it) {
    it.addEventListener("click", function() {
      if (it.dataset.ctxAct === "excl") { var any = targets.some(function(t) { return excluded[t]; }); targets.forEach(function(t) { excluded[t] = !any; }); }
      else if (it.dataset.ctxAct === "goto") { if (typeof loadPage === "function") loadPage(targets[0]); if (typeof closeOverlays === "function") closeOverlays(); _lovsSelected.clear(); }
      else { targets.forEach(function(t) { liteSetTag(t, it.dataset.ctxTag); }); }
      _lovsRenderClassify(); _lovsHideCtx();
    });
  });
}

function _lovsHideCtx() { var m = document.getElementById("ov-ctxmenu"); if (m) m.style.display = "none"; }

/* ============================================================  STEP 2 */
function _lovsRenderFloors() {
  var strip = document.getElementById("floor-strip"); if (!strip) return;
  var pc = (typeof pageCount !== "undefined") ? pageCount : 0;
  var floors = [];
  for (var n = 1; n <= pc; n++) { if (pageTags[n] === "floor") floors.push({p: n, floor: pageFloorNum[n]}); }
  var fc = document.getElementById("fcount"); if (fc) fc.textContent = floors.length;
  floors.sort(function(a, b) {
    var fa = a.floor === "roof" ? 9999 : a.floor != null ? +a.floor : 10000 + a.p;
    var fb = b.floor === "roof" ? 9999 : b.floor != null ? +b.floor : 10000 + b.p;
    return fa - fb;
  });
  if (!floors.length) { strip.innerHTML = '<div style="color:var(--muted,#8b97a8);padding:20px;text-align:center;width:100%">⚠ ยังไม่มีหน้า <code style="color:#4cc9f0">tag=floor</code> — กลับ Step 1</div>'; return; }
  var h = "";
  floors.forEach(function(f) {
    var kind = pageFloorKind[f.p] || (f.floor === "roof" ? "rooftop" : (f.floor != null ? "normal" : ""));
    var isSpec = (kind === "rooftop" || kind === "mechanical");
    var isEmpty = !kind;
    var numStr;
    if (kind === "rooftop") numStr = "⛅ROOF";
    else if (kind === "mechanical") numStr = "⚙MEC";
    else if (kind === "basement") numStr = "⬇B" + (f.floor != null ? f.floor : "?");
    else if (kind === "normal") numStr = f.floor != null ? String(f.floor) : "–";
    else numStr = "–";
    h += '<div class="fchip' + (isSpec ? " spec" : "") + (isEmpty ? " empty" : "") + '" draggable="true" data-p="' + f.p + '">' +
      '<button class="clr">✕</button><div class="num">' + numStr + '</div>' +
      '<div class="pg">p' + f.p + '</div><div class="lb">' + (pageNames[f.p] || "หน้า " + f.p) + '</div></div>';
  });
  strip.innerHTML = h;
  _lovsWireFloorDnd();
}

function _lovsWireFloorDnd() {
  var strip = document.getElementById("floor-strip"); if (!strip) return;
  var dragP = null;
  strip.querySelectorAll(".fchip").forEach(function(c) {
    var cb = c.querySelector(".clr");
    if (cb) cb.addEventListener("click", function(e) {
      e.stopPropagation(); var p = +c.dataset.p; delete pageFloorNum[p]; delete pageFloorKind[p];
      _lovsRenderFloors(); _lovsUpdateHeader();
    });
    c.addEventListener("dragstart", function(e) { dragP = +c.dataset.p; c.classList.add("drg"); e.dataTransfer.effectAllowed = "move"; e.dataTransfer.setData("text/plain", String(dragP)); });
    c.addEventListener("dragend", function() { c.classList.remove("drg"); strip.querySelectorAll(".fchip.over").forEach(function(x) { x.classList.remove("over"); }); });
    c.addEventListener("dragover", function(e) { e.preventDefault(); c.classList.add("over"); });
    c.addEventListener("dragleave", function() { c.classList.remove("over"); });
    c.addEventListener("drop", function(e) {
      e.preventDefault(); c.classList.remove("over");
      var dp = +c.dataset.p; if (dragP === dp) return;
      var a = pageFloorNum[dragP], b = pageFloorNum[dp], ka = pageFloorKind[dragP], kb = pageFloorKind[dp];
      if (b !== undefined) pageFloorNum[dragP] = b; else delete pageFloorNum[dragP];
      if (a !== undefined) pageFloorNum[dp] = a; else delete pageFloorNum[dp];
      if (kb !== undefined) pageFloorKind[dragP] = kb; else delete pageFloorKind[dragP];
      if (ka !== undefined) pageFloorKind[dp] = ka; else delete pageFloorKind[dp];
      if (typeof state !== "undefined") state.dirty = true;
      if (typeof reseedActivePageFolders === "function" && typeof state !== "undefined" && state.pageFolderMode) reseedActivePageFolders();
      _lovsRenderFloors(); _lovsUpdateHeader();
    });
  });
}

function _lovsSequentialFloor() {
  var sEl = document.getElementById("seq-start"), start = sEl ? (+sEl.value || 1) : 1;
  var pns = []; document.querySelectorAll("#floor-strip .fchip").forEach(function(c) { pns.push(+c.dataset.p); });
  if (!pns.length) return;
  // Pre-count basement total so we can number descending (leftmost=deepest=largest)
  var basementTotal = 0;
  for (var bi = 0; bi < pns.length; bi++) {
    if ((pageFloorKind[pns[bi]] || "normal") === "basement") basementTotal++;
  }
  var basementSeen = 0;
  var n = start;
  for (var i = 0; i < pns.length; i++) {
    var pi = pns[i];
    var kind = pageFloorKind[pi] || "normal";
    // Skip non-counted kinds: mezzanine/mechanical/rooftop are inserted but don't consume a number
    if (kind === "mezzanine" || kind === "mechanical" || kind === "rooftop") {
      delete pageFloorNum[pi];
      continue;
    }
    // Basement: descending. Leftmost basement = basementTotal, rightmost = 1
    if (kind === "basement") {
      _lovsSetFloorNum(pi, basementTotal - basementSeen);
      basementSeen++;
      continue;
    }
    if (i === pns.length - 1 && pns.length >= 4 && kind === "normal") _lovsSetFloorNum(pi, "roof");
    else { _lovsSetFloorNum(pi, n); n++; }
  }
  if (typeof reseedActivePageFolders === "function" && typeof state !== "undefined" && state.pageFolderMode) reseedActivePageFolders();
  _lovsRenderFloors(); _lovsUpdateHeader();
}

function _lovsClearFloors() {
  var pc = (typeof pageCount !== "undefined") ? pageCount : 0;
  for (var n = 1; n <= pc; n++) { if (pageFloorNum[n] !== undefined) { delete pageFloorNum[n]; delete pageFloorKind[n]; } }
  _lovsRenderFloors(); _lovsUpdateHeader();
}

/* ============================================================  STEP 3 — REAL BINDING (LOVS-3)
   Replaces the LOVS-2 mock constants with computeSummary() + folder-scoped
   layer aggregation. Falls back to global-role sum when LPFL mode is OFF
   or no PF folders exist. ที่ดิน + ปกคลุม shown as INDEPENDENT quantities;
   ที่ว่าง = ที่ดิน − ปกคลุม (derived, formula explicit).
============================================================ */

/* Sum poly object areas for a single layerId across all NON-excluded pages.
   Uses vendored polyMetricsAnyShape (arc-inclusive) + per-page scale. Returns 0 if no data. */
function _lovsLayerArea(layerId) {
  if (typeof PS === "undefined" || typeof polyMetricsAnyShape !== "function") return 0;
  var total = 0;
  Object.keys(PS).forEach(function(k) {
    var pg = +k;
    if (typeof excluded !== "undefined" && excluded[pg]) return;
    var objs = (PS[k] && PS[k].objects) || [];
    for (var i = 0; i < objs.length; i++) {
      var o = objs[i];
      if (o.catId !== layerId || o.counting || o.kind !== "poly") continue;
      var a = polyMetricsAnyShape(o, pg).area;
      if (a != null && isFinite(a)) total += a;
    }
  });
  return total;
}

/* Sum areas of all descendant layers under folderId, optionally filtered by role.
   Walks ancestorsOf for each layer to check folder membership (handles nested folders). */
function _lovsFolderArea(folderId, roleFilter) {
  if (typeof LAYERS === "undefined" || typeof ancestorsOf !== "function") return 0;
  var total = 0;
  for (var i = 0; i < LAYERS.length; i++) {
    var l = LAYERS[i];
    if (roleFilter && l.role !== roleFilter) continue;
    var chain = ancestorsOf(l.id);
    if (chain.indexOf(folderId) >= 0) total += _lovsLayerArea(l.id);
  }
  return total;
}

/* Sum across all layers with a given role (no folder scope). Fallback when LPFL OFF. */
function _lovsRoleArea(role) {
  if (typeof LAYERS === "undefined") return 0;
  var total = 0;
  for (var i = 0; i < LAYERS.length; i++) {
    if (LAYERS[i].role === role) total += _lovsLayerArea(LAYERS[i].id);
  }
  return total;
}

function _lovsRenderReview() {
  var r = document.getElementById("report"); if (!r) return;
  var pc = (typeof pageCount !== "undefined") ? pageCount : 0;
  var floorPages = [], sitePages = [];
  for (var n = 1; n <= pc; n++) {
    if (pageTags[n] === "floor") floorPages.push(n);
    if (pageTags[n] === "site" && !excluded[n]) sitePages.push(n);
  }
  floorPages.sort(function(a, b) {
    return ((pageFloorNum[a] === "roof" ? 9999 : pageFloorNum[a] || 0)) - ((pageFloorNum[b] === "roof" ? 9999 : pageFloorNum[b] || 0));
  });
  function fmt(n) { return n.toLocaleString("th-TH", {minimumFractionDigits: 2, maximumFractionDigits: 2}); }

  /* === SITE / COVERAGE BINDING ===
     ที่ดิน + ปกคลุม are INDEPENDENT quantities (NOT summed):
       - ที่ดิน  = Σ area of role='site' layers (boundary polygons)
       - ปกคลุม = Σ area of role='gfa' layers under PF_site folder if LPFL ON;
                  fallback: 0 (cannot infer ปกคลุม from global gfa role
                  because that includes per-floor GFA from PF_floor_*)
       - ที่ว่าง = ที่ดิน − ปกคลุม  (always derived, formula shown)
  */
  var hasPFSite = (typeof folderById === "function") && !!folderById("PF_site");
  var landArea  = _lovsRoleArea("site");
  var coverArea = hasPFSite ? _lovsFolderArea("PF_site", "gfa") : 0;
  var coverSource = hasPFSite ? "PF_site / gfa layers" : "—";
  var openArea  = Math.max(0, landArea - coverArea);

  /* === GFA PER-FLOOR BINDING ===
     For each tag=floor page, build a row from its PF_floor_<N> folder
     (gfa = gross, ded = deduction, both summed across pages in folder).
     Falls back to "—" if LPFL mode OFF or no PF folder.
  */
  var rows = floorPages.map(function(p) {
    var fl = pageFloorNum[p];
    var kind = pageFloorKind[p] || (fl === "roof" ? "rooftop" : (fl != null ? "normal" : ""));
    var label = _lovsFloorLabel(p);
    var hasFloor = (kind === "rooftop" || kind === "mechanical") || (fl != null && fl !== "roof");
    var floorId = "PF_floor_" + (fl != null ? fl : "?");
    var hasPF = (typeof folderById === "function") && !!folderById(floorId);
    var gross = hasPF ? _lovsFolderArea(floorId, "gfa") : 0;
    var ded   = hasPF ? _lovsFolderArea(floorId, "ded") : 0;
    return {p: p, label: label, kind: kind, gross: gross, ded: ded, net: gross - ded, hasFloor: hasFloor, hasPF: hasPF, pfId: floorId};
  });
  var totG = 0, totD = 0; rows.forEach(function(rw) { totG += rw.gross; totD += rw.ded; });
  var totN = totG - totD;
  var FAR = landArea > 0 ? totN / landArea : 0;
  var COV = landArea > 0 ? coverArea / landArea * 100 : 0;
  var OSR = totN > 0 ? openArea / totN * 100 : 0;

  /* === LRV / report-vars ===
     If global computeReportVars exists (lite/static/js/report-vars.js), pull
     named quantities. They render alongside derived Section 4 for parity
     with #btn-sum / lite-report.html. */
  var lrv = [];
  if (typeof computeReportVars === "function" && typeof computeSummary === "function") {
    try {
      var _s = computeSummary();
      var _agg = {}; Object.keys(_s.all || {}).forEach(function(k){_agg[k]=_s.all[k];});
      Object.keys(_s.allCnt || {}).forEach(function(k){_agg[k]=_s.allCnt[k];});
      lrv = computeReportVars(_agg);
    } catch (e) { /* LRV not initialized — silent */ }
  }

  /* === traceability + counts === */
  var tagged = 0; for (var n2 = 1; n2 <= pc; n2++) { if (pageTags[n2]) tagged++; }
  var excPages = [], measPages = [], missingFloor = rows.filter(function(rw) { return !rw.hasFloor; }).length;
  var missingPF = rows.filter(function(rw) { return rw.hasFloor && !rw.hasPF; }).length;
  var excCount = 0; for (var xk in excluded) { if (excluded[xk]) excCount++; }
  for (var ni = 1; ni <= pc; ni++) {
    var tg = pageTags[ni] || "";
    if (excluded[ni] || !tg || tg === "detail" || tg === "plan" || tg === "parking" || tg === "amenity") excPages.push(ni);
    else if (tg === "site" || tg === "floor") measPages.push(ni);
  }

  /* === RENDER === */
  var html = '<h1>รายงานสรุป — Page Setup Wizard</h1>' +
    '<div class="sub">tagged ' + tagged + '/' + pc + ' · ' + floorPages.length + ' floor pages · ' +
    'data: real (polyMetrics + folder aggregation)</div>';

  if (missingFloor) html += '<div class="warn">⚠ มี ' + missingFloor + ' หน้า tag=floor ยังไม่ได้ใส่เลขชั้น/ประเภท</div>';
  if (!sitePages.length) html += '<div class="warn">⚠ ยังไม่มีหน้า tag=site — ที่ดินจะเป็น 0 จนกว่าจะวาดขอบเขตในหน้า site</div>';
  if (!hasPFSite) html += '<div class="warn">⚠ ยังไม่ได้เปิด <b>📂 page-folder mode</b> หรือยังไม่มี folder PF_site — พื้นที่อาคารปกคลุมจะเป็น 0</div>';
  if (missingPF) html += '<div class="warn">⚠ มี ' + missingPF + ' floor page ที่ยังไม่มี folder PF_floor_N (เปิด page-folder mode เพื่อ auto-seed)</div>';
  if (landArea === 0 && coverArea === 0 && totG === 0)
    html += '<div class="warn">ℹ️ ยังไม่มีพื้นที่ที่วัด — ตั้งสเกล (S) + วาด polygon (A) บนหน้าที่ tag เรียบร้อย แล้วเปิด page-folder mode (📂)</div>';

  html += '<h2>1. สรุป Page Setup</h2><table>' +
    '<tr><th>รายการ</th><th class="num">จำนวน</th><th>หมายเหตุ</th></tr>' +
    '<tr><td>หน้าทั้งหมด</td><td class="num">' + pc + '</td><td></td></tr>' +
    '<tr><td>ติด tag</td><td class="num">' + tagged + '</td><td>' + (pc ? (tagged / pc * 100).toFixed(0) : 0) + '%</td></tr>' +
    '<tr><td>site</td><td class="num">' + sitePages.length + '</td><td>' + (sitePages.map(function(p){return"p"+p;}).join(", ")||"—") + '</td></tr>' +
    '<tr><td>floor</td><td class="num">' + floorPages.length + '</td><td>' + rows.filter(function(rw){return rw.hasFloor;}).length + '/' + floorPages.length + ' numbered</td></tr>' +
    '<tr><td>excluded</td><td class="num">' + excCount + '</td><td></td></tr></table>';

  /* === Section 2: Site + Coverage as 2 INDEPENDENT root quantities === */
  html += '<h2>2. ที่ดิน + พื้นที่ปกคลุม (independent quantities)</h2>' +
    '<table><tr><th>รายการ</th><th class="num" style="width:130px">พื้นที่ (m²)</th><th>ที่มา</th></tr>' +
    '<tr><td><b>ที่ดิน</b> (Land area)</td><td class="num"><b>' + fmt(landArea) + '</b></td>' +
      '<td>Σ layer role=site · ' + (sitePages.map(function(p){return"p"+p;}).join(", ")||"ยังไม่มี") + '</td></tr>' +
    '<tr><td><b>พื้นที่อาคารปกคลุม</b> (Coverage)</td><td class="num"><b>' + fmt(coverArea) + '</b></td>' +
      '<td>Σ ' + coverSource + '</td></tr>' +
    '</table>' +
    '<div class="calc" style="margin-top:8px"><div class="row">' +
      '<span><b>ที่ว่าง</b> (Open Space) = ที่ดิน − พื้นที่อาคารปกคลุม</span>' +
      '<b>' + fmt(landArea) + ' − ' + fmt(coverArea) + ' = <span style="color:#0a6">' + fmt(openArea) + '</span> m²</b>' +
    '</div></div>';

  html += '<h2>3. GFA Breakdown ต่อชั้น</h2>' +
    '<table><tr><th>ชั้น</th><th>หน้า</th><th class="num">Gross (m²)</th><th class="num">หัก (m²)</th><th class="num">Net (m²)</th><th>folder</th></tr>';
  if (!rows.length) html += '<tr><td colspan="6" style="text-align:center;color:#a04">ไม่มี floor page</td></tr>';
  rows.forEach(function(rw) {
    var rowStyle = !rw.hasFloor ? ' style="color:#a04"' : (!rw.hasPF ? ' style="color:#a60"' : "");
    html += '<tr' + rowStyle + '><td>' + rw.label + '</td><td>p' + rw.p + '</td>' +
      '<td class="num">' + fmt(rw.gross) + '</td><td class="num">−' + fmt(rw.ded) + '</td>' +
      '<td class="num"><b>' + fmt(rw.net) + '</b></td>' +
      '<td style="font-size:10px;color:#888">' + (rw.hasPF ? rw.pfId : "—") + '</td></tr>';
  });
  html += '<tr class="tot"><td colspan="2">รวม GFA</td><td class="num">' + fmt(totG) +
    '</td><td class="num">−' + fmt(totD) + '</td><td class="num"><b>' + fmt(totN) + '</b></td><td></td></tr></table>';

  html += '<h2>4. ตัวเลขควบคุม (Derived)</h2><div class="calc">' +
    '<div class="row"><span>FAR = GFA / ที่ดิน</span><b>' + (landArea > 0 ? fmt(totN) + " / " + fmt(landArea) + " = " + FAR.toFixed(3) : "— (ยังไม่มีที่ดิน)") + '</b></div>' +
    '<div class="row"><span>Coverage = ปกคลุม / ที่ดิน × 100</span><b>' + (landArea > 0 ? COV.toFixed(2) + " %" : "—") + '</b></div>' +
    '<div class="row"><span>OSR = ที่ว่าง / GFA × 100</span><b>' + (totN > 0 ? OSR.toFixed(2) + " %" : "—") + '</b></div>' +
    '<div class="row tot"><span>หมายเหตุ</span><span style="font-weight:400;font-size:11px">' +
      (landArea > 0 || coverArea > 0 || totG > 0 ?
        "ข้อมูลจริงจาก polyMetrics (per-page scale) + folder aggregation" :
        "ยังไม่มีข้อมูล — ที่ดิน/ปกคลุม/GFA ทั้งหมด = 0") +
    '</span></div></div>';

  if (lrv && lrv.length) {
    html += '<h2>5. ตัวแปรรายงาน (LRV registry)</h2><table>' +
      '<tr><th>ชื่อ</th><th class="num">ค่า</th><th>หน่วย</th></tr>' +
      lrv.map(function(v) {
        var val = (v.err ? '<span style="color:#a04">' + v.err + '</span>' : (v.value != null ? fmt(v.value) : "—"));
        return '<tr><td>' + (v.name || "") + '</td><td class="num">' + val + '</td><td>' + (v.unit || "") + '</td></tr>';
      }).join('') + '</table>';
  }

  html += '<h2>' + (lrv && lrv.length ? '6' : '5') + '. Traceability</h2>' +
    '<div style="font-size:11px;color:#555">หน้าที่ใช้คำนวณ (' + measPages.length + ')</div>' +
    '<div class="pl">' + (measPages.map(function(p){return '<span>p'+p+' '+pageTags[p]+(pageFloorNum[p]!=null?' '+pageFloorNum[p]:'')+'</span>';}).join('')||'—') + '</div>' +
    '<div style="font-size:11px;color:#555;margin-top:6px">หน้าที่ไม่ใช้ (' + excPages.length + ')</div>' +
    '<div class="pl">' + (excPages.map(function(p){return '<span class="exc">p'+p+' '+(pageTags[p]||'ว่าง')+'</span>';}).join('')||'—') + '</div>';
  r.innerHTML = html;
}

/* Export-to-PDF / open-report — reuse live's buildReportPayload + openReport flow.
   Called from Step 3 nav button. If openReport() exists (mi-report wired in
   ui-lite.html L1019), call it directly. Otherwise, alert + close. */
function _lovsExportReport() {
  if (typeof caseId !== "undefined" && !caseId) { alert("เปิด PDF ก่อน"); return; }
  if (typeof openReport === "function") {
    var ov = document.getElementById("ov");
    if (ov) ov.classList.remove("show");
    openReport();
    return;
  }
  if (typeof buildReportPayload === "function") {
    var payload = buildReportPayload();
    if (!payload.pages.length) { alert("ยังไม่มีพื้นที่ที่วัด — วาด polygon ก่อน"); return; }
    try { sessionStorage.setItem("bmaReportPayload", JSON.stringify(payload)); }
    catch (e) { alert("เตรียมรายงานไม่สำเร็จ: " + e.message); return; }
    window.open("/report", "_blank");
    return;
  }
  alert("ฟังก์ชันสร้างรายงานไม่พร้อม — ยืนยันว่าโหลด lite/static/js/report-vars.js แล้ว");
}

/* -- force-fill missing tags on Done (LWIZ-FORCE-FILL) -- */
function _lovsForceFillMissingTags() {
  if (typeof pageCount === "undefined" || pageCount <= 0) return;
  if (typeof pageTags === "undefined") return;

  var missing = [];
  var tagged  = [];
  for (var i = 1; i <= pageCount; i++) {
    if (pageTags[i]) {
      tagged.push({
        idx: i,
        tag: pageTags[i],
        floor: (typeof pageFloorNum !== "undefined") ? pageFloorNum[i] : undefined,
        kind: (typeof pageFloorKind !== "undefined") ? pageFloorKind[i] : undefined
      });
    } else {
      missing.push(i);
    }
  }

  // No tagged page at all → fallback all missing to "excluded"
  if (tagged.length === 0) {
    for (var j = 0; j < missing.length; j++) {
      if (typeof liteSetTag === "function") liteSetTag(missing[j], "excluded");
      else pageTags[missing[j]] = "excluded";
    }
    return;
  }

  // For each missing page, find nearest by page#-distance (tiebreak: lower idx wins)
  for (var k = 0; k < missing.length; k++) {
    var m = missing[k];
    var best = null, bestDist = Infinity;
    for (var n = 0; n < tagged.length; n++) {
      var t = tagged[n];
      var d = Math.abs(t.idx - m);
      if (d < bestDist || (d === bestDist && best !== null && t.idx < best.idx)) {
        best = t;
        bestDist = d;
      }
    }
    if (best) {
      if (typeof liteSetTag === "function") liteSetTag(m, best.tag);
      else pageTags[m] = best.tag;
      if (best.floor !== undefined && typeof pageFloorNum !== "undefined") pageFloorNum[m] = best.floor;
      if (best.kind  !== undefined && typeof pageFloorKind !== "undefined") pageFloorKind[m] = best.kind;
    }
  }

  // Trigger reseed of PF folders so they pick up new pages
  if (typeof reseedActivePageFolders === "function") reseedActivePageFolders();
  // BUG-20260526-lite-wizard-followup (B): refresh left panel so user sees the
  // auto-seeded base layers immediately. Without this, FOLDERS+LAYERS are
  // populated but the picker DOM still shows the pre-seed state.
  if (typeof buildPicker === "function") buildPicker();
}

/* -- nav wiring -- */
function _lovsWireNav() {
  var cb = document.getElementById("ov-close");
  if (cb) cb.addEventListener("click", function() { var ov = document.getElementById("ov"); if (ov) ov.classList.remove("show"); _lovsSelected.clear(); _lovsHideCtx(); });
  var prev = document.getElementById("ov-prev"); if (prev) prev.addEventListener("click", function() { _lovsGoStep(_lovsCurStep - 1); });
  var next = document.getElementById("ov-next");
  if (next) next.addEventListener("click", function() {
    if (_lovsCurStep < 3) _lovsGoStep(_lovsCurStep + 1);
    else {
      // Done (Step 3): force-fill any untagged pages before closing
      _lovsForceFillMissingTags();
      // BUG-20260526-lite-wizard-followup: lift LWIZ lock unconditionally on Done.
      // _lwizCheckLiftLock only lifts if ≥1 non-excluded tag exists — so if user
      // clicked Done with 0 tags (force-fill defaulted everything to "excluded"),
      // the lock would otherwise stay stuck and re-block on next wizard open.
      if (typeof _lwizAutoLiftLock === "function") _lwizAutoLiftLock();
      var ov = document.getElementById("ov"); if (ov) ov.classList.remove("show"); _lovsSelected.clear();
    }
  });
  document.querySelectorAll("#ov-steps .step").forEach(function(el) { el.addEventListener("click", function() { _lovsGoStep(+el.dataset.step); }); });
  var sq = document.getElementById("ov-seq"); if (sq) sq.addEventListener("click", _lovsSequentialFloor);
  var cf = document.getElementById("ov-clear-floor"); if (cf) cf.addEventListener("click", _lovsClearFloors);
  var ex = document.getElementById("ov-export"); if (ex) ex.addEventListener("click", _lovsExportReport);
}

/* -- keyboard -- */
function _lovsWireKeyboard() {
  document.addEventListener("keydown", function(e) {
    var ov = document.getElementById("ov");
    if (!ov || !ov.classList.contains("show")) return;
    if (document.activeElement && document.activeElement.tagName === "INPUT") return;
    if (e.key === "Escape") {
      if (_lovsSelected.size > 0) {
        _lovsSelected.clear(); _lovsRenderClassify();
        e.preventDefault(); e.stopPropagation(); return; // prevent live Esc handler from closing overlay
      }
      ov.classList.remove("show"); _lovsHideCtx(); e.preventDefault(); return;
    }
    if (_lovsCurStep !== 1) return;
    var pc = (typeof pageCount !== "undefined") ? pageCount : 0;
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "a") {
      _lovsSelected.clear(); for (var i = 1; i <= pc; i++) _lovsSelected.add(i);
      _lovsSelAnchor = 1; _lovsRenderClassify(); e.preventDefault(); return;
    }
    if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
      _lovsFocusPage = e.key === "ArrowRight" ? Math.min(pc, _lovsFocusPage + 1) : Math.max(1, _lovsFocusPage - 1);
      if (!e.shiftKey) { _lovsSelected.clear(); _lovsSelected.add(_lovsFocusPage); _lovsSelAnchor = _lovsFocusPage; }
      else if (_lovsSelAnchor != null) {
        var lo = Math.min(_lovsSelAnchor, _lovsFocusPage), hi = Math.max(_lovsSelAnchor, _lovsFocusPage);
        _lovsSelected.clear(); for (var ri = lo; ri <= hi; ri++) _lovsSelected.add(ri);
      }
      _lovsRenderClassify();
      var el = document.querySelector('#grid-classify .ov-tile[data-pg="' + _lovsFocusPage + '"]');
      if (el) el.scrollIntoView({block: "nearest"});
      e.preventDefault(); return;
    }
    if (e.key === "Enter") { if (typeof loadPage === "function") loadPage(_lovsFocusPage); if (typeof closeOverlays === "function") closeOverlays(); _lovsSelected.clear(); e.preventDefault(); return; }
    if (e.key.toLowerCase() === "x") {
      var tgts = _lovsSelected.size > 0 ? (function(){var a=[];_lovsSelected.forEach(function(n){a.push(n);});return a;})() : [_lovsFocusPage];
      var any = tgts.some(function(t) { return excluded[t]; });
      tgts.forEach(function(t) { excluded[t] = !any; });
      _lovsRenderClassify(); e.preventDefault(); return;
    }
    if (_lovsSetTagViaKey(e.key)) e.preventDefault();
  });
}

/* -- bootstrap --
   This script is injected dynamically AFTER DOMContentLoaded has already fired.
   Use setTimeout(0) to let any in-progress scripts finish, then wrap openOv.
   Guard with __lovsWrapped to make idempotent.
*/
function _lovsBootstrap() {
  if (window.__lovsWrapped) return;
  window.__lovsWrapped = true;
  _lovsInjectCSS();
  if (typeof openOv === "function" && !openOv.__lovsWrapped) {
    _lovsOrigOpenOv = openOv;
    openOv = function() { _lovsOpenOv(); };
    openOv.__lovsWrapped = true;
  }
  /* Rebind #btn-ov click — ui-lite.html L1087 captured the ORIGINAL openOv
     reference at parse time (before our wrap). Without this, the button
     still calls the old openOv → tries to write to #ov-grid which we
     replaced → throws "Cannot set properties of null". F12 (L1159) is
     fine because it calls global openOv() at event-fire-time. */
  var _btnOv = document.getElementById("btn-ov");
  if (_btnOv) _btnOv.onclick = function() { openOv(); };
}

// If DOMContentLoaded already fired (dynamic inject), run immediately via setTimeout(0).
// If not (e.g. test env where script is in <head>), listen for the event.
if (document.readyState === "loading") {
  window.addEventListener("DOMContentLoaded", _lovsBootstrap);
} else {
  setTimeout(_lovsBootstrap, 0);
}
