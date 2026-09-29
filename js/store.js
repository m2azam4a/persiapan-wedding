/* Shared persistence + helpers for Wedding Planner HTML */
(function () {
  const KEY = "wedding-planner-html-v1";

  const ASSET_CATEGORIES = [
    { id: "catatan", label: "Catatan" },
    { id: "wag", label: "WAG" },
    { id: "spreadsheet", label: "Spreadsheet" },
    { id: "gdrive", label: "Link Gdrive" },
  ];

  function deepClone(o) {
    return JSON.parse(JSON.stringify(o));
  }

  function assetCategoryLabel(id) {
    const c = ASSET_CATEGORIES.find((x) => x.id === id);
    return c ? c.label : id;
  }

  function normalizeCategories(raw) {
    let list = [];
    if (Array.isArray(raw)) list = raw;
    else if (typeof raw === "string" && raw) list = [raw];
    const valid = ASSET_CATEGORIES.map((c) => c.id);
    const uniq = [];
    list.forEach((id) => {
      const c = String(id || "").trim();
      if (valid.includes(c) && !uniq.includes(c)) uniq.push(c);
    });
    return uniq.length ? uniq : ["catatan"];
  }

  function normalizeAsset(a, i) {
    if (!a || typeof a !== "object") return null;
    const categories = normalizeCategories(a.categories != null ? a.categories : a.category);
    const title = String(a.title || "").trim();
    const url = String(a.url || "").trim();
    const detail = String(a.detail || "").trim();
    if (!title && !url && !detail) return null;
    return {
      id: String(a.id || `asset-${Date.now()}-${i}`),
      categories,
      // category = label utama (pertama) untuk kompatibilitas lama
      category: categories[0],
      title: title || (url ? "Link" : "Tanpa judul"),
      url,
      detail,
    };
  }

  function normalizeAssets(list) {
    if (!Array.isArray(list)) return [];
    return list.map(normalizeAsset).filter(Boolean);
  }

  /** Satu kali: tebak aset dari catatan lama (kalau field assets masih kosong). */
  function migrateAssetsFromNotes(notes) {
    const text = String(notes || "").trim();
    if (!text) return [];
    const out = [];
    const urlRe = /https?:\/\/[^\s<>"')\]]+/gi;
    const urls = text.match(urlRe) || [];
    urls.forEach((raw, i) => {
      const url = raw.replace(/[.,;]+$/, "");
      const u = url.toLowerCase();
      let categories = ["gdrive"];
      let title = "Link Gdrive";
      if (u.includes("docs.google.com/spreadsheets") || /\.xlsx?(\?|$)/i.test(u)) {
        categories = ["spreadsheet"];
        title = "Spreadsheet";
      } else if (u.includes("drive.google.com")) {
        categories = ["gdrive"];
        title = "Folder / file Gdrive";
      } else if (u.includes("chat.whatsapp.com") || u.includes("wa.me")) {
        categories = ["wag"];
        title = "Link WAG";
      } else {
        categories = ["catatan", "gdrive"];
        title = "Link";
      }
      out.push({ id: `migrated-url-${i}`, categories, title, url, detail: "" });
    });

    text.split(/\r?\n/).forEach((line, i) => {
      const L = line.trim();
      if (!L || /https?:\/\//i.test(L)) return;
      const wa = L.match(/^(WA\s*Grup[^:]*|Grup\s*WA[^:]*)\s*[:：]\s*(.+)$/i);
      if (wa) {
        out.push({
          id: `migrated-wag-${i}`,
          categories: ["wag"],
          title: wa[1].trim(),
          url: "",
          detail: wa[2].trim(),
        });
      }
    });

    if (!out.length) {
      out.push({
        id: "migrated-note-0",
        categories: ["catatan"],
        title: text.length > 80 ? text.slice(0, 77) + "…" : text,
        url: "",
        detail: text.length > 80 ? text : "",
      });
    }
    return normalizeAssets(out);
  }

  function mergeTasks(defaults, saved) {
    const map = new Map((saved || []).map((t) => [t.id, t]));
    return defaults.map((d) => {
      const s = map.get(d.id);
      if (!s) {
        const base = deepClone(d);
        base.assets = normalizeAssets(base.assets);
        return base;
      }
      let assets = normalizeAssets(s.assets);
      if (!assets.length && typeof s.notes === "string" && s.notes.trim()) {
        assets = migrateAssetsFromNotes(s.notes);
      }
      // Jangan hilangkan catatan: kalau saved notes kosong tapi default/juga kosong, tetap string.
      // Kalau saved punya notes (termasuk string kosong eksplisit dari user), pakai saved.
      // Prefer notes non-kosong jika salah satu pihak punya isi.
      let notes = typeof s.notes === "string" ? s.notes : d.notes || "";
      if (!String(notes).trim() && typeof d.notes === "string" && d.notes.trim()) {
        notes = d.notes;
      }
      return {
        ...deepClone(d),
        start: Number.isFinite(s.start) ? s.start : d.start,
        end: Number.isFinite(s.end) ? s.end : d.end,
        status: s.status || d.status,
        progress: Number.isFinite(s.progress) ? s.progress : d.progress,
        notes,
        deps: Array.isArray(s.deps) ? s.deps : d.deps,
        assets,
      };
    });
  }

  function mergeDaily(defaults, saved) {
    const map = new Map((saved || []).map((d) => [d.day, d]));
    return defaults.map((d) => {
      const s = map.get(d.day);
      if (!s) return deepClone(d);
      const itemMap = new Map((s.items || []).map((i) => [i.id, i]));
      return {
        day: d.day,
        items: d.items.map((it) => {
          const si = itemMap.get(it.id);
          return si ? { ...it, done: !!si.done, text: si.text || it.text } : deepClone(it);
        }),
      };
    });
  }

  function load() {
    const base = deepClone(window.WP_DEFAULT);
    base.tasks = base.tasks.map((t) => ({ ...t, assets: normalizeAssets(t.assets) }));
    try {
      const raw = localStorage.getItem(KEY);
      if (!raw) return base;
      const saved = JSON.parse(raw);
      return {
        version: 1,
        settings: { ...base.settings, ...(saved.settings || {}) },
        phases: base.phases,
        tasks: mergeTasks(base.tasks, saved.tasks),
        daily: mergeDaily(base.daily, saved.daily),
      };
    } catch (e) {
      console.warn("WP store load failed", e);
      return base;
    }
  }

  function save(state) {
    const payload = {
      version: 1,
      settings: state.settings,
      tasks: state.tasks.map((t) => ({
        id: t.id,
        start: t.start,
        end: t.end,
        status: t.status,
        progress: t.progress,
        notes: t.notes,
        deps: t.deps,
        assets: normalizeAssets(t.assets),
      })),
      daily: state.daily.map((d) => ({
        day: d.day,
        items: d.items.map((i) => ({ id: i.id, done: !!i.done, text: i.text })),
      })),
    };
    localStorage.setItem(KEY, JSON.stringify(payload));
    window.dispatchEvent(new CustomEvent("wp-saved", { detail: { at: Date.now() } }));
  }

  function reset() {
    localStorage.removeItem(KEY);
    return load();
  }

  function exportJson(state) {
    return JSON.stringify(
      {
        version: 1,
        exportedAt: new Date().toISOString(),
        settings: state.settings,
        tasks: state.tasks.map((t) => ({
          ...t,
          assets: normalizeAssets(t.assets),
        })),
        daily: state.daily,
      },
      null,
      2
    );
  }

  function importJson(text) {
    const parsed = JSON.parse(text);
    const base = deepClone(window.WP_DEFAULT);
    const state = {
      version: 1,
      settings: { ...base.settings, ...(parsed.settings || {}) },
      phases: base.phases,
      tasks: mergeTasks(base.tasks, parsed.tasks),
      daily: mergeDaily(base.daily, parsed.daily),
    };
    save(state);
    return state;
  }

  function labelDay(d) {
    if (d === 0) return "H";
    return d < 0 ? `H${d}` : `H+${d}`;
  }

  function absDate(settings, dayRel) {
    if (!settings.weddingDate) return null;
    const base = new Date(settings.weddingDate + "T12:00:00");
    if (Number.isNaN(base.getTime())) return null;
    base.setDate(base.getDate() + dayRel);
    return base.toISOString().slice(0, 10);
  }

  function dayFromAbs(settings, iso) {
    if (!settings.weddingDate || !iso) return null;
    const h = new Date(settings.weddingDate + "T12:00:00");
    const d = new Date(iso + "T12:00:00");
    return Math.round((d - h) / 86400000);
  }

  function taskMap(tasks) {
    const m = {};
    tasks.forEach((t) => (m[t.id] = t));
    return m;
  }

  function rescheduleFrom(tasks, rootId, settings) {
    if (!settings.autoReschedule) return tasks;
    const next = tasks.map((t) => ({ ...t }));
    const map = taskMap(next);
    const queue = [rootId];
    const seen = new Set();
    while (queue.length) {
      const id = queue.shift();
      if (seen.has(id)) continue;
      seen.add(id);
      const succs = next.filter((t) => (t.deps || []).includes(id));
      for (const s of succs) {
        const preds = (s.deps || []).map((d) => map[d]).filter(Boolean);
        const minStart = Math.max(...preds.map((p) => p.end), settings.dayMin);
        const dur = Math.max(1, s.end - s.start);
        if (s.start < minStart) {
          s.start = minStart;
          s.end = Math.min(settings.dayMax + 1, s.start + dur);
          if (s.end <= s.start) s.end = s.start + 1;
          queue.push(s.id);
        }
      }
    }
    return next;
  }

  function stats(state) {
    const total = state.tasks.length;
    const done = state.tasks.filter((t) => t.status === "done").length;
    const doing = state.tasks.filter((t) => t.status === "doing").length;
    const blocked = state.tasks.filter((t) => t.status === "blocked").length;
    const cp = state.tasks.filter((t) => t.cp).length;
    const dailyItems = state.daily.flatMap((d) => d.items);
    const dailyDone = dailyItems.filter((i) => i.done).length;
    const assetCount = state.tasks.reduce((n, t) => n + normalizeAssets(t.assets).length, 0);
    return { total, done, doing, blocked, cp, dailyTotal: dailyItems.length, dailyDone, assetCount };
  }

  function toast(msg) {
    let el = document.getElementById("wp-toast");
    if (!el) {
      el = document.createElement("div");
      el.id = "wp-toast";
      el.className = "wp-toast";
      document.body.appendChild(el);
    }
    el.textContent = msg;
    el.classList.add("show");
    clearTimeout(el._t);
    el._t = setTimeout(() => el.classList.remove("show"), 1800);
  }

  function statusLabel(status) {
    const map = {
      todo: "Belum mulai",
      doing: "Sedang dikerjakan",
      done: "Selesai",
      blocked: "Terhambat",
    };
    return map[status] || status;
  }

  function listAssets(state) {
    const items = [];
    (state.tasks || []).forEach((t) => {
      normalizeAssets(t.assets).forEach((a) => {
        items.push({
          ...a,
          categoryLabels: a.categories.map(assetCategoryLabel),
          categoryLabel: a.categories.map(assetCategoryLabel).join(", "),
          taskId: t.id,
          wbs: t.wbs,
          name: t.name,
          status: t.status,
          progress: t.progress,
        });
      });
    });
    const catOrder = { catatan: 0, wag: 1, spreadsheet: 2, gdrive: 3 };
    items.sort(
      (a, b) =>
        Math.min(...a.categories.map((c) => catOrder[c] ?? 9)) -
          Math.min(...b.categories.map((c) => catOrder[c] ?? 9)) ||
        String(a.wbs).localeCompare(String(b.wbs), undefined, { numeric: true })
    );
    return items;
  }

  function assetsByCategory(state) {
    const grouped = {};
    ASSET_CATEGORIES.forEach((c) => {
      grouped[c.id] = [];
    });
    listAssets(state).forEach((a) => {
      a.categories.forEach((cat) => {
        if (!grouped[cat]) grouped[cat] = [];
        // satu evidence bisa muncul di beberapa kategori
        grouped[cat].push(a);
      });
    });
    return grouped;
  }

  function extractAssets(state) {
    return listAssets(state).map((a) => ({
      kind: a.categoryLabel,
      label: a.title,
      url: a.url,
      detail: a.detail,
      taskId: a.taskId,
      wbs: a.wbs,
      name: a.name,
      status: a.status,
      progress: a.progress,
      category: a.category,
      categories: a.categories,
    }));
  }

  window.WP = {
    KEY,
    ASSET_CATEGORIES,
    load,
    save,
    reset,
    exportJson,
    importJson,
    labelDay,
    absDate,
    dayFromAbs,
    taskMap,
    rescheduleFrom,
    stats,
    toast,
    deepClone,
    statusLabel,
    normalizeAssets,
    normalizeCategories,
    assetCategoryLabel,
    listAssets,
    assetsByCategory,
    extractAssets,
    migrateAssetsFromNotes,
  };
})();
