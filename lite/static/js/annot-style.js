/* ============================================================
   LITE-ANNOT-STYLE — annotation style editor (color / opacity / font size)
   Standalone module, intentionally kept OUT of ui-lite.html.

   Public API (called from ui-lite.html via typeof-guards):
     window.openAnnStyle(ann, screenX, screenY)
     window.closeAnnStyle()

   Depends on these globals defined by the main inline script:
     PSpage(), draw(), pushUndo(), state, annStyle(a)
   Mutates ann.color / ann.opacity / ann.fontSize in place; one undo entry
   per editing session (first change pushes, the rest of the drag does not).
   ============================================================ */
(function () {
  "use strict";
  var PRESETS = ["#ff453a", "#ff9f0a", "#ffd60a", "#30d158", "#4c8dff", "#bf5af2", "#ffffff", "#ffe08a"];
  var cur = null;        // annotation being styled
  var sessDirty = false; // has this editing session pushed an undo snapshot yet
  var panel = null;

  function css() {
    if (document.getElementById("as-css")) return;
    var s = document.createElement("style"); s.id = "as-css";
    s.textContent = [
      ".annstyle-panel{position:fixed;display:none;z-index:140;width:226px;background:var(--panel,#161a21);",
      "border:1px solid var(--line,#2a3340);border-radius:10px;padding:11px 12px;",
      "box-shadow:0 10px 30px rgba(0,0,0,.55);font:13px 'Segoe UI','Noto Sans Thai',sans-serif;color:var(--ink,#e7eaf0);}",
      ".annstyle-panel .as-row{display:flex;align-items:center;gap:8px;margin-bottom:9px;}",
      ".annstyle-panel .as-row:last-child{margin-bottom:0;}",
      ".annstyle-panel .as-lbl{width:62px;font-size:11px;color:var(--muted,#8b97a8);flex:none;}",
      ".annstyle-panel .as-swatches{display:flex;gap:4px;flex-wrap:wrap;flex:1;}",
      ".annstyle-panel .as-sw{width:16px;height:16px;border-radius:50%;cursor:pointer;border:2px solid transparent;}",
      ".annstyle-panel .as-sw.on{border-color:#fff;}",
      ".annstyle-panel input[type=color]{width:26px;height:22px;padding:0;border:1px solid var(--line,#2a3340);background:none;border-radius:4px;cursor:pointer;flex:none;}",
      ".annstyle-panel input[type=range]{flex:1;accent-color:var(--accent,#4c8dff);}",
      ".annstyle-panel .as-val{width:34px;text-align:right;font-size:11px;color:var(--muted,#8b97a8);}",
      ".annstyle-panel .as-editrow{margin-bottom:7px;}",
      ".annstyle-panel .as-edit{width:100%;text-align:center;}",
      ".annstyle-panel .as-actions{justify-content:flex-end;gap:8px;margin-top:3px;}",
      ".annstyle-panel button{padding:5px 12px;border-radius:6px;border:1px solid var(--line,#2a3340);",
      "background:#222a37;color:var(--ink,#e7eaf0);cursor:pointer;font-size:12px;}",
      ".annstyle-panel button.as-del{border-color:#5a2730;background:#3a1d22;color:#ff8a8a;}",
      ".annstyle-panel button.as-close{border-color:var(--accent,#4c8dff);background:var(--accent,#4c8dff);color:#fff;}"
    ].join("");
    document.head.appendChild(s);
  }

  function build() {
    css();
    panel = document.createElement("div");
    panel.className = "annstyle-panel";
    panel.innerHTML =
      '<div class="as-row"><span class="as-lbl">สี</span>' +
        '<span class="as-swatches">' + PRESETS.map(function (c) {
          return '<span class="as-sw" data-c="' + c + '" style="background:' + c + '"></span>';
        }).join("") + '</span>' +
        '<input type="color" class="as-color"></div>' +
      '<div class="as-row"><span class="as-lbl">โปร่งแสง</span>' +
        '<input type="range" class="as-opacity" min="0.1" max="1" step="0.05"><span class="as-val as-opacity-val"></span></div>' +
      '<div class="as-row as-fontrow"><span class="as-lbl">ขนาดตัวอักษร</span>' +
        '<input type="range" class="as-font" min="8" max="48" step="1"><span class="as-val as-font-val"></span></div>' +
      '<div class="as-row as-editrow"><button class="as-edit"></button></div>' +
      '<div class="as-row as-actions"><button class="as-del">ลบ</button><button class="as-close">เสร็จ</button></div>';
    document.body.appendChild(panel);

    var colorIn = panel.querySelector(".as-color"),
        opac = panel.querySelector(".as-opacity"), opacVal = panel.querySelector(".as-opacity-val"),
        font = panel.querySelector(".as-font"), fontVal = panel.querySelector(".as-font-val");

    panel.addEventListener("mousedown", function (e) { e.stopPropagation(); });
    panel.querySelectorAll(".as-sw").forEach(function (sw) {
      sw.onclick = function () { setColor(sw.dataset.c); colorIn.value = sw.dataset.c; markSwatch(sw.dataset.c); };
    });
    colorIn.oninput = function () { setColor(colorIn.value); markSwatch(colorIn.value); };
    opac.oninput = function () { touch(); cur.opacity = parseFloat(opac.value); opacVal.textContent = Math.round(cur.opacity * 100) + "%"; redraw(); };
    font.oninput = function () { touch(); cur.fontSize = parseInt(font.value, 10); fontVal.textContent = cur.fontSize + "px"; redraw(); };
    panel.querySelector(".as-del").onclick = function () { del(); };
    panel.querySelector(".as-close").onclick = function () { window.closeAnnStyle(); };
    panel.querySelector(".as-edit").onclick = function () {
      var a = cur; if (!a) return;
      var f = (a.type === "ann_text" || a.type === "ann_comment") ? "text" : "label";
      if (typeof pushUndo === "function") pushUndo();
      window.closeAnnStyle();
      if (typeof openAnnEditor === "function") openAnnEditor(a, false, f);
    };
  }

  function markSwatch(c) {
    if (!panel) return;
    panel.querySelectorAll(".as-sw").forEach(function (sw) {
      sw.classList.toggle("on", (sw.dataset.c || "").toLowerCase() === String(c).toLowerCase());
    });
  }
  function touch() { if (!sessDirty) { if (typeof pushUndo === "function") pushUndo(); sessDirty = true; } }
  function redraw() { if (typeof draw === "function") draw(); }
  function setColor(c) { if (!cur) return; touch(); cur.color = c; redraw(); }
  function del() {
    if (!cur) return;
    if (typeof pushUndo === "function") pushUndo();
    var arr = PSpage().annotations, ix = arr.indexOf(cur);
    if (ix >= 0) arr.splice(ix, 1);
    if (typeof state !== "undefined") state.selAnn = null;
    window.closeAnnStyle(); redraw();
  }

  window.openAnnStyle = function (ann, sx, sy) {
    if (!panel) build();
    cur = ann; sessDirty = false;
    var st = (typeof annStyle === "function") ? annStyle(ann) : { color: ann.color || "#ff453a", opacity: ann.opacity != null ? ann.opacity : 1, fontSize: ann.fontSize || 13 };
    var isText = ann.type === "ann_text" || ann.type === "ann_comment";
    var editBtn = panel.querySelector(".as-edit");
    editBtn.textContent = isText ? "✎ แก้ข้อความ" : (ann.label ? "✎ แก้ป้ายข้อความ" : "🏷 เพิ่มป้ายข้อความ");
    panel.querySelector(".as-color").value = /^#[0-9a-f]{6}$/i.test(st.color) ? st.color : "#ff453a";
    markSwatch(st.color);
    var opac = panel.querySelector(".as-opacity"); opac.value = st.opacity; panel.querySelector(".as-opacity-val").textContent = Math.round(st.opacity * 100) + "%";
    panel.querySelector(".as-fontrow").style.display = isText ? "flex" : "none";
    if (isText) { panel.querySelector(".as-font").value = st.fontSize; panel.querySelector(".as-font-val").textContent = st.fontSize + "px"; }
    // position near the annotation, clamped to viewport
    var cv = document.getElementById("cv"), r = cv ? cv.getBoundingClientRect() : { left: 0, top: 0 };
    panel.style.display = "block";
    var pw = panel.offsetWidth || 226, ph = panel.offsetHeight || 150;
    var left = r.left + sx + 12, top = r.top + sy + 12;
    left = Math.max(8, Math.min(left, window.innerWidth - pw - 8));
    top = Math.max(8, Math.min(top, window.innerHeight - ph - 8));
    panel.style.left = left + "px"; panel.style.top = top + "px";
  };

  window.closeAnnStyle = function () { cur = null; sessDirty = false; if (panel) panel.style.display = "none"; };
})();
