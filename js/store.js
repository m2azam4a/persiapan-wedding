/* Shared persistence + helpers for Wedding Planner HTML */
(function () {
  const KEY = "wedding-planner-html-v1";

  function deepClone(o) {
    return JSON.parse(JSON.stringify(o));
  }

  function mergeTasks(defaults, saved) {
    const map = new Map((saved || []).map((t) => [t.id, t]));
    return defaults.map((d) => {
      const s = map.get(d.id);
      if (!s) return deepClone(d);
      return {
        ...deepClone(d),
        start: Number.isFinite(s.start) ? s.start : d.start,
        end: Number.isFinite(s.end) ? s.end : d.end,
        status: s.status || d.status,
        progress: Number.isFinite(s.progress) ? s.progress : d.progress,
        notes: typeof s.notes === "string" ? s.notes : d.notes,
        deps: Array.isArray(s.deps) ? s.deps : d.deps,
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
        tasks: state.tasks,
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

  /** FS auto-reschedule: push successors so start >= pred.end */
  function rescheduleFrom(tasks, rootId, settings) {
    if (!settings.autoReschedule) return tasks;
    const byId = taskMap(tasks);
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
    return { total, done, doing, blocked, cp, dailyTotal: dailyItems.length, dailyDone };
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

  /** Ambil aset monitoring dari catatan pekerjaan (link Drive/Sheet, grup WA, dll). */
  function extractAssets(state) {
    const urlRe = /https?:\/\/[^\s<>"')\]]+/gi;
    const items = [];
    const seen = new Set();

    function push(item) {
      const key = `${item.taskId}|${item.kind}|${item.url || item.label}`;
      if (seen.has(key)) return;
      seen.add(key);
      items.push(item);
    }

    function kindFromUrl(url) {
      const u = url.toLowerCase();
      if (u.includes("docs.google.com/spreadsheets") || u.includes(".xlsx") || u.includes(".xls")) {
        return "Excel / Google Sheet";
      }
      if (u.includes("docs.google.com/document")) return "Google Docs";
      if (u.includes("drive.google.com")) return "Folder / file Google Drive";
      if (u.includes("chat.whatsapp.com") || u.includes("wa.me")) return "Grup / chat WhatsApp";
      return "Link";
    }

    function labelFromUrl(url, kind) {
      if (kind === "Excel / Google Sheet") return "Sheet monitoring (Google Sheets)";
      if (kind === "Folder / file Google Drive") return "Folder dokumentasi Google Drive";
      if (kind === "Google Docs") return "Dokumen Google Docs";
      return kind;
    }

    (state.tasks || []).forEach((t) => {
      const notes = (t.notes || "").trim();
      if (!notes) return;
      const before = items.length;

      const urls = notes.match(urlRe) || [];
      urls.forEach((url) => {
        const clean = url.replace(/[.,;]+$/, "");
        const kind = kindFromUrl(clean);
        push({
          kind,
          label: labelFromUrl(clean, kind),
          url: clean,
          detail: "",
          taskId: t.id,
          wbs: t.wbs,
          name: t.name,
          status: t.status,
          progress: t.progress,
        });
      });

      notes.split(/\r?\n/).forEach((line) => {
        const L = line.trim();
        if (!L) return;
        if (/https?:\/\//i.test(L)) return;

        const wa = L.match(/^(WA\s*Grup[^:]*|Grup\s*WA[^:]*)\s*[:：]\s*(.+)$/i);
        if (wa) {
          push({
            kind: "Grup WhatsApp",
            label: wa[1].trim(),
            url: "",
            detail: wa[2].trim(),
            taskId: t.id,
            wbs: t.wbs,
            name: t.name,
            status: t.status,
            progress: t.progress,
          });
          return;
        }

        if (/buku panduan|excel|spreadsheet|sheet master|decision log|catatan log/i.test(L)) {
          push({
            kind: "Dokumen / catatan",
            label: L.length > 90 ? L.slice(0, 87) + "…" : L,
            url: "",
            detail: "",
            taskId: t.id,
            wbs: t.wbs,
            name: t.name,
            status: t.status,
            progress: t.progress,
          });
        }
      });

      // Catatan penting tanpa link/WA (mis. scope) — hanya jika belum ada aset dari task ini
      if (items.length === before) {
        const first = notes.split(/\r?\n/).map((x) => x.trim()).filter(Boolean)[0] || notes;
        push({
          kind: "Catatan di pekerjaan",
          label: first.length > 90 ? first.slice(0, 87) + "…" : first,
          url: "",
          detail: notes.length > first.length ? "Ada detail di catatan Jadwal" : "",
          taskId: t.id,
          wbs: t.wbs,
          name: t.name,
          status: t.status,
          progress: t.progress,
        });
      }
    });

    const order = { done: 0, doing: 1, blocked: 2, todo: 3 };
    items.sort((a, b) => (order[a.status] ?? 9) - (order[b.status] ?? 9) || String(a.wbs).localeCompare(String(b.wbs), undefined, { numeric: true }));
    return items;
  }

  window.WP = {
    KEY,
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
    extractAssets,
  };
})();
