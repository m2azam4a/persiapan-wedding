(function () {
  const PAGES = [
    { href: "index.html", id: "home", label: "Beranda" },
    { href: "gantt.html", id: "gantt", label: "Jadwal" },
    { href: "daily.html", id: "daily", label: "Harian" },
    { href: "vendors.html", id: "vendors", label: "Vendor" },
    { href: "settings.html", id: "settings", label: "Pengaturan" },
  ];

  function mountNav(active) {
    const top = document.createElement("header");
    top.className = "wp-top";
    top.innerHTML = `
      <div class="wp-brand">Persiapan <span>Nikah</span></div>
      <nav class="wp-nav" id="wp-nav"></nav>
      <div class="wp-top-actions">
        <span class="small muted" id="wp-save-indicator">Otomatis tersimpan</span>
        <button class="btn" type="button" id="wp-export">Simpan cadangan</button>
        <label class="btn" style="cursor:pointer;margin:0">
          Muat cadangan
          <input type="file" id="wp-import" accept="application/json,.json" hidden />
        </label>
      </div>
    `;
    document.body.prepend(top);
    const nav = top.querySelector("#wp-nav");
    PAGES.forEach((p) => {
      const a = document.createElement("a");
      a.href = p.href;
      a.textContent = p.label;
      if (p.id === active) a.classList.add("active");
      nav.appendChild(a);
    });

    window.addEventListener("wp-saved", () => {
      const el = document.getElementById("wp-save-indicator");
      if (!el) return;
      el.textContent = "Tersimpan jam " + new Date().toLocaleTimeString();
    });

    document.getElementById("wp-export").onclick = () => {
      const state = window.__WP_STATE || WP.load();
      const blob = new Blob([WP.exportJson(state)], { type: "application/json" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "cadangan-persiapan-nikah.json";
      a.click();
      WP.toast("Cadangan berhasil diunduh");
    };

    document.getElementById("wp-import").onchange = async (e) => {
      const file = e.target.files && e.target.files[0];
      if (!file) return;
      const text = await file.text();
      try {
        const state = WP.importJson(text);
        window.__WP_STATE = state;
        WP.toast("Cadangan berhasil dimuat — memuat ulang…");
        setTimeout(() => location.reload(), 500);
      } catch (err) {
        alert("Gagal memuat cadangan: " + err.message);
      }
    };
  }

  window.WPNav = { mountNav, PAGES };
})();
