/* INV-2026-07-lite-verify-scale — LITE port of proto's Verify Scale
   (INV-2026-05-20-001, proto/ui.html ~2761-2815). Second-reference
   cross-check against the page's existing calibration. Calibration is a
   single-sample measurement (~1-2% scale error -> ~2-4% area error,
   silently undetected) — Verify Scale lets the user click a SECOND known
   dimension and compare.

   Additive only: writes PS[pg].scale.verifyResult =
     {pct, action, verifyPts_per_m, ts}
   Never renames/removes existing scale fields. `st.calibScale = p.scale`
   in buildPageStore() (ui-lite.html) already serialises this object
   wholesale, so verifyResult rides the existing .bmaplan scale field with
   no further save/load plumbing needed.

   Reuses the EXISTING 2-point capture pipeline of the "scale" tool
   (mousedown draft-push + snap + live overlay, all in ui-lite.html) —
   this module never touches snap/draft/coordinate logic itself. The only
   ui-lite.html hook is: when state.tool==="scale" and a 2nd point lands
   while state.verifyMode is true, ui-lite.html calls
   VerifyScale.onTwoPoints() instead of openCalib().

   FORBIDDEN SURFACES — never touched by this file: measure-engine.js,
   RS, pdfToC/cToPdf, ptToScreen/screenToPt internals. Read-only reuse
   of getScaleForPage/state/pushUndo/setTool/draw/buildPicker (all
   defined in ui-lite.html before this script loads).
*/
(function () {
  "use strict";

  var _ctx = null; // {pg, sc, ptDist, enterM, measM, vPpm, pct}

  /* band(pct) — proto-identical thresholds: green <0.5%, yellow <2%, red >=2% */
  function band(pct) {
    return pct < 0.5 ? "green" : pct < 2 ? "yellow" : "red";
  }

  /* pure math — exposed for direct unit testing (page.evaluate) without
     driving clicks/prompt(). Mirrors proto verifyFinish()'s formulas. */
  function computeDeviation(ptDist, ppm, enterM) {
    var measM = ptDist / ppm;
    var vPpm = ptDist / enterM;
    var pct = 100 * Math.abs(measM - enterM) / enterM;
    return { measM: measM, vPpm: vPpm, pct: pct, band: band(pct) };
  }

  /* ---------------- entry point (menu item / Shift+S) ---------------- */
  function start() {
    if (typeof caseId === "undefined" || !caseId) { alert("เปิด PDF ก่อน"); return; }
    var sc = getScaleForPage(curPage);
    if (!sc || !(sc.pts_per_m > 0)) {
      alert("หน้านี้ยังไม่มี scale — ตั้ง Set Scale ก่อน แล้วจึง Verify");
      return;
    }
    setTool("scale");                 // resets draft/verifyMode, reuses existing 2-pt capture
    state.verifyMode = true;
    state.hintFlash = "🔎 Verify: คลิก 2 จุดบนเส้นที่รู้ระยะจริง (คนละเส้นกับที่สอบเทียบ)";
    if (typeof draw === "function") draw();
  }

  /* ---------------- called by ui-lite.html mousedown when the 2nd verify point lands ---------------- */
  function onTwoPoints() {
    var d = state.draft;
    state.verifyMode = false;
    state.hintFlash = "";
    if (!d || d.length < 2) { state.draft = null; return; }
    var ptDist = Math.hypot(d[1].x - d[0].x, d[1].y - d[0].y);
    state.draft = null;
    var pg = curPage, sc = getScaleForPage(pg);
    if (!sc || !(sc.pts_per_m > 0)) { alert("ไม่พบ scale หน้านี้"); if (typeof draw === "function") draw(); return; }
    var input = prompt("ระยะจริงระหว่าง 2 จุดที่คลิก (เมตร):", "");
    if (input === null) { if (typeof draw === "function") draw(); return; }
    var enterM = parseFloat(input);
    if (!(enterM > 0)) { alert("ระยะต้องมากกว่า 0"); if (typeof draw === "function") draw(); return; }
    var dev = computeDeviation(ptDist, sc.pts_per_m, enterM);
    _ctx = { pg: pg, sc: sc, ptDist: ptDist, enterM: enterM, measM: dev.measM, vPpm: dev.vPpm, pct: dev.pct };
    openResultModal();
    if (typeof draw === "function") draw();
  }

  /* ---------------- result modal (self-contained DOM — no ui-lite.html markup edits) ---------------- */
  function ensureModalDom() {
    var el = document.getElementById("vs-modal");
    if (el) return el;
    el = document.createElement("div");
    el.id = "vs-modal";
    el.style.cssText = "position:fixed;inset:0;background:rgba(6,8,12,.72);z-index:9500;display:none;align-items:center;justify-content:center;";
    el.innerHTML =
      '<div style="background:#161a22;border:1px solid #2a3140;border-radius:12px;padding:18px 20px;width:340px;color:#e7ecf3;font:13px/1.4 \'Segoe UI\',sans-serif">' +
      '<h4 style="margin:0 0 10px;font-size:15px">🔎 ผลตรวจสอบสเกล</h4>' +
      '<div id="vs-dev" style="font-size:38px;font-weight:800;text-align:center;margin:8px 0">—</div>' +
      '<div id="vs-band" style="text-align:center;font-size:12px;padding:5px 0;border-radius:6px;margin-bottom:10px;font-weight:700;color:#001">—</div>' +
      '<div style="display:flex;justify-content:space-between;font-size:12px;padding:3px 0;border-bottom:1px dashed #2a3340"><span>วัดได้ (สเกลปัจจุบัน)</span><b id="vs-meas">—</b></div>' +
      '<div style="display:flex;justify-content:space-between;font-size:12px;padding:3px 0;border-bottom:1px dashed #2a3340"><span>ระยะจริงที่ป้อน</span><b id="vs-enter">—</b></div>' +
      '<div style="display:flex;justify-content:space-between;font-size:12px;padding:3px 0;border-bottom:1px dashed #2a3340"><span>ผลต่อพื้นที่ (≈2×)</span><b id="vs-area">—</b></div>' +
      '<div style="margin-top:12px;display:flex;flex-direction:column;gap:6px">' +
      '<button id="vs-accept" style="padding:7px 14px;border-radius:7px;border:1px solid #4c8dff;background:#4c8dff;color:#fff;cursor:pointer">✓ ยอมรับ (Accept)</button>' +
      '<button id="vs-recal" style="padding:7px 14px;border-radius:7px;border:1px solid #2a3140;background:#222a37;color:#e7ecf3;cursor:pointer">↻ สอบเทียบใหม่ (Recalibrate)</button>' +
      '<button id="vs-avg" style="padding:7px 14px;border-radius:7px;border:1px solid #2a3140;background:#222a37;color:#e7ecf3;cursor:pointer">⌀ เฉลี่ย (Average)</button>' +
      '<button id="vs-close" style="padding:7px 14px;border-radius:7px;border:1px solid #2a3140;background:#222a37;color:#e7ecf3;cursor:pointer">ปิด</button>' +
      '</div>' +
      '<div style="font-size:10px;color:#9aa3b2;margin-top:6px">band: เขียว &lt;0.5% · เหลือง &lt;2% · แดง ≥2%</div>' +
      '</div>';
    document.body.appendChild(el);
    el.querySelector("#vs-accept").onclick = accept;
    el.querySelector("#vs-recal").onclick = recalibrate;
    el.querySelector("#vs-avg").onclick = average;
    el.querySelector("#vs-close").onclick = closeModal;
    return el;
  }

  var COL = { green: "#34c759", yellow: "#ffcc00", red: "#ff3b30" };

  function openResultModal() {
    if (!_ctx) return;
    var el = ensureModalDom();
    var b = band(_ctx.pct);
    var big = document.getElementById("vs-dev");
    big.textContent = _ctx.pct.toFixed(2) + "%";
    big.style.color = COL[b];
    var bandEl = document.getElementById("vs-band");
    bandEl.textContent = b === "green" ? "✓ แม่นยำดี (ยอมรับได้)" :
      b === "yellow" ? "⚠ คลาดเคลื่อนเล็กน้อย — ควรระวัง" :
      "✕ คลาดเคลื่อนสูง — แนะนำสอบเทียบใหม่";
    bandEl.style.background = COL[b];
    document.getElementById("vs-meas").textContent = _ctx.measM.toFixed(3) + " ม.";
    document.getElementById("vs-enter").textContent = _ctx.enterM.toFixed(3) + " ม.";
    document.getElementById("vs-area").textContent = "≈ " + (2 * _ctx.pct).toFixed(2) + "%";
    el.style.display = "flex";
  }

  function closeModal() {
    var el = document.getElementById("vs-modal");
    if (el) el.style.display = "none";
    _ctx = null;
    if (typeof setTool === "function") setTool("select");
    else if (typeof draw === "function") draw();
  }

  function flashMsg(msg) {
    if (typeof state === "undefined") return;
    state.hintFlash = msg;
    setTimeout(function () {
      state.hintFlash = "";
      if (typeof updateHUD === "function") updateHUD();
    }, 4000);
  }

  /* additive-only write: PS[pg].scale.verifyResult (rides the existing scale
     object — never renames/removes pts_per_m or any other field). */
  function writeResult(action, pct) {
    if (!_ctx || !_ctx.sc) return;
    _ctx.sc.verifyResult = {
      pct: +pct.toFixed(4),
      action: action,
      verifyPts_per_m: +_ctx.vPpm.toFixed(4),
      ts: Date.now()
    };
    if (typeof state !== "undefined") state.dirty = true;
  }

  function afterScaleChange() {
    if (typeof state !== "undefined") state.dirty = true;
    if (typeof buildPicker === "function") buildPicker();
  }

  /* ---------------- 3 result actions ---------------- */
  function accept() {
    if (!_ctx) return;
    if (typeof pushUndo === "function") pushUndo();
    writeResult("accept", _ctx.pct);
    var p = _ctx.pct;
    closeModal();
    flashMsg("✓ รับค่า scale เดิม (dev " + p.toFixed(2) + "%)");
  }

  function recalibrate() {
    if (!_ctx || !_ctx.sc) return;
    if (typeof pushUndo === "function") pushUndo();
    var sc = _ctx.sc, vPpm = _ctx.vPpm;
    sc.pts_per_m = vPpm;                      // replace scale with the 2nd-reference implied value
    writeResult("recalibrate", 0);            // post-recalibration deviation is 0 by definition (proto parity)
    var n = Math.round(1000 * (72 / 25.4) / vPpm);
    afterScaleChange();
    closeModal();
    flashMsg("↻ สอบเทียบใหม่จากเส้นที่ 2 → 1:" + n);
  }

  function average() {
    if (!_ctx || !_ctx.sc) return;
    if (typeof pushUndo === "function") pushUndo();
    var sc = _ctx.sc, avg = (sc.pts_per_m + _ctx.vPpm) / 2;
    sc.pts_per_m = avg;                       // average of the two pts_per_m samples
    writeResult("average", _ctx.pct);
    var n = Math.round(1000 * (72 / 25.4) / avg);
    afterScaleChange();
    closeModal();
    flashMsg("⌀ เฉลี่ย scale → 1:" + n);
  }

  /* ---------------- test hook — bypasses prompt()/DOM clicks so
     Playwright can drive the pure logic directly via page.evaluate. ---------------- */
  var __test = {
    computeCtx: function (pg, ptDist, enterM) {
      var sc = getScaleForPage(pg);
      if (!sc || !(sc.pts_per_m > 0)) return null;
      var dev = computeDeviation(ptDist, sc.pts_per_m, enterM);
      _ctx = { pg: pg, sc: sc, ptDist: ptDist, enterM: enterM, measM: dev.measM, vPpm: dev.vPpm, pct: dev.pct };
      return _ctx;
    },
    getCtx: function () { return _ctx; },
    clearCtx: function () { _ctx = null; }
  };

  window.VerifyScale = {
    start: start,
    onTwoPoints: onTwoPoints,
    accept: accept,
    recalibrate: recalibrate,
    average: average,
    band: band,
    computeDeviation: computeDeviation,
    __test: __test
  };
  window.verifyScaleStart = start;
})();
