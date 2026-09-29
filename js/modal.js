(function () {
  function ensureModal() {
    let backdrop = document.getElementById("wp-def-modal");
    if (backdrop) return backdrop;
    backdrop = document.createElement("div");
    backdrop.id = "wp-def-modal";
    backdrop.className = "wp-modal-backdrop";
    backdrop.hidden = true;
    backdrop.innerHTML = `
      <div class="wp-modal def-wide" role="dialog" aria-modal="true" aria-labelledby="wp-def-title">
        <header>
          <div>
            <div class="small muted" id="wp-def-meta"></div>
            <h2 id="wp-def-title">Penjelasan pekerjaan</h2>
          </div>
          <button type="button" class="btn" id="wp-def-close">Tutup</button>
        </header>
        <div id="wp-def-body"></div>
      </div>
    `;
    document.body.appendChild(backdrop);
    backdrop.addEventListener("click", (e) => {
      if (e.target === backdrop) closeDefinition();
    });
    backdrop.querySelector("#wp-def-close").onclick = closeDefinition;
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && !backdrop.hidden) closeDefinition();
    });
    return backdrop;
  }

  function closeDefinition() {
    const backdrop = document.getElementById("wp-def-modal");
    if (backdrop) backdrop.hidden = true;
  }

  function openDefinition(taskId) {
    const defs = window.WP_DEFINITIONS || {};
    const d = defs[taskId];
    const backdrop = ensureModal();
    const title = document.getElementById("wp-def-title");
    const meta = document.getElementById("wp-def-meta");
    const body = document.getElementById("wp-def-body");

    if (!d) {
      title.textContent = taskId;
      meta.textContent = "";
      body.innerHTML = `<p class="muted">Belum ada penjelasan untuk pekerjaan ini.</p>`;
      backdrop.hidden = false;
      return;
    }

    meta.textContent = `${d.wbs} · ${taskId} · ${d.phase_nama || d.phase}${
      d.cp ? " · Jangan sampai telat" : ""
    }`;
    title.textContent = d.nama;
    const steps = (d.langkah || [])
      .map(
        (s, i) =>
          `<li><span class="step-num">Langkah ${i + 1}</span><div class="step-text">${s}</div></li>`
      )
      .join("");
    const deps = (d.deps || []).length
      ? `<p class="small">Kerjakan setelah ini selesai dulu: <strong>${d.deps.join(", ")}</strong></p>`
      : `<p class="small muted">Tidak menunggu pekerjaan lain (boleh mulai lebih dulu).</p>`;

    body.innerHTML = `
      <div class="def-block">
        <h4>Bagian mana ini?</h4>
        <p>${d.konteks_fase || "—"}</p>
        <p class="small muted" style="margin-top:6px">Ini penjelasan kelompok besar (${(d.wbs || "").split(".")[0] || "?"}.x). Sama untuk pekerjaan seinduk.</p>
      </div>
      <div class="def-block">
        <h4>Pekerjaan ini ngapain?</h4>
        <p><strong>${d.esensi || d.tujuan || "—"}</strong></p>
        <p class="small muted" style="margin-top:6px">Ini esensi khusus untuk ${d.wbs || taskId} — baca dulu sebelum langkah detail.</p>
      </div>
      <div class="def-block def-steps">
        <h4>Langkah demi langkah (ikuti berurutan)</h4>
        <p class="small muted" style="margin-bottom:8px">Detail cara mengerjakan. Kerjakan satu per satu.</p>
        <ol class="step-list">${steps}</ol>
      </div>
      <div class="def-block">
        <h4>Hasil yang harus ada</h4>
        <p>${d.hasil || d.deliverable || "—"}</p>
      </div>
      <div class="def-block">
        <h4>Kapan dianggap selesai?</h4>
        <p>${d.selesai_bila}</p>
      </div>
      <div class="def-block">
        <h4>Yang sebaiknya dihindari</h4>
        <p>${d.hindari}</p>
      </div>
      <div class="def-block">
        <h4>Siapa yang pegang?</h4>
        <p>Yang bertanggung jawab: <strong>${d.pic}</strong> · Kerja sama dengan: <strong>${d.vendor}</strong></p>
        ${deps}
      </div>
    `;
    backdrop.hidden = false;
  }

  window.WPModal = { openDefinition, closeDefinition };
})();
