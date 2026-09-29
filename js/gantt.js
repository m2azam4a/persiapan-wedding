/*! Interactive Gantt: drag move, resize handles, deps, date edit, group collapse */
(function () {
  const DAY_W = 14;
  const ROW_H = 44;
  const LABEL_W = 320;
  const HEADER_H = 42;
  const BAR_H = 20;

  function clamp(v, lo, hi) {
    return Math.max(lo, Math.min(hi, v));
  }

  function wbsMajor(t) {
    return String(t.wbs || "").split(".")[0] || "?";
  }

  function initGantt(root) {
    let state = WP.load();
    window.__WP_STATE = state;
    const dayMin = state.settings.dayMin;
    const dayMax = state.settings.dayMax;
    const days = [];
    for (let d = dayMin; d <= dayMax; d++) days.push(d);

    const collapsed = new Set(
      Array.isArray(state.settings.collapsedWbs) ? state.settings.collapsedWbs.map(String) : []
    );

    const ui = {
      filterPhase: "ALL",
      filterStatus: "ALL",
      cpOnly: !!state.settings.showCriticalOnly,
      selectedId: null,
      showDeps: state.settings.showDeps !== false,
    };

    root.innerHTML = `
      <div class="hub-banner">
        <strong>Ini satu-satunya halaman untuk mengubah progres.</strong>
        Di sini Anda bisa ubah status, persen selesai, geser jadwal (tarik batang), dan tulis catatan.
        Halaman Beranda, Vendor, dan Harian hanya menampilkan ringkasan.
        Tombol <strong>?</strong> = penjelasan mudah tiap pekerjaan.
        Tombol <strong>▾ / ▸</strong> di kiri kelompok (1.x, 2.x, …) = lipat/buka agar tampilan lebih ringkas.
      </div>
      <div class="gantt-toolbar">
        <select id="g-phase"></select>
        <select id="g-status">
          <option value="ALL">Semua status</option>
          <option value="todo">Belum mulai</option>
          <option value="doing">Sedang dikerjakan</option>
          <option value="done">Selesai</option>
          <option value="blocked">Terhambat</option>
        </select>
        <label class="small"><input type="checkbox" id="g-cp" ${ui.cpOnly ? "checked" : ""}/> Hanya yang jangan sampai telat</label>
        <label class="small"><input type="checkbox" id="g-deps" ${ui.showDeps ? "checked" : ""}/> Tampilkan garis keterhubungan</label>
        <label class="small"><input type="checkbox" id="g-auto" ${state.settings.autoReschedule ? "checked" : ""}/> Geser otomatis pekerjaan berikutnya</label>
        <button class="btn" type="button" id="g-collapse-all">Lipat semua</button>
        <button class="btn" type="button" id="g-expand-all">Buka semua</button>
        <button class="btn" type="button" id="g-today">Lompat ke hari-H</button>
        <div class="legend">
          <span><i class="bar"></i>Biasa</span>
          <span><i class="cp"></i>Jangan telat</span>
          <span><i class="group"></i>Kelompok (dilipat)</span>
          <span><i class="sel"></i>Dipilih</span>
          <span><i class="pred"></i>1 langkah sebelumnya</span>
          <span><i class="succ"></i>1 langkah selanjutnya</span>
          <span><i class="hari"></i>Hari pernikahan</span>
        </div>
      </div>
      <div class="gantt-wrap" id="gantt-wrap">
        <div id="gantt-inner" style="position:relative"></div>
      </div>
      <aside class="side-panel" id="side" hidden></aside>
    `;

    const phaseSel = root.querySelector("#g-phase");
    phaseSel.innerHTML =
      `<option value="ALL">Semua fase</option>` +
      Object.entries(state.phases)
        .map(([k, v]) => `<option value="${k}">${k} — ${v}</option>`)
        .join("");

    phaseSel.onchange = () => {
      ui.filterPhase = phaseSel.value;
      render();
    };
    root.querySelector("#g-status").onchange = (e) => {
      ui.filterStatus = e.target.value;
      render();
    };
    root.querySelector("#g-cp").onchange = (e) => {
      ui.cpOnly = e.target.checked;
      state.settings.showCriticalOnly = ui.cpOnly;
      persist();
      render();
    };
    root.querySelector("#g-deps").onchange = (e) => {
      ui.showDeps = e.target.checked;
      state.settings.showDeps = ui.showDeps;
      persist();
      drawDeps();
    };
    root.querySelector("#g-auto").onchange = (e) => {
      state.settings.autoReschedule = e.target.checked;
      persist();
      WP.toast(e.target.checked ? "Geser otomatis: NYALA" : "Geser otomatis: MATI");
    };
    root.querySelector("#g-today").onclick = () => {
      const wrap = root.querySelector("#gantt-wrap");
      const hariIndex = days.indexOf(0);
      wrap.scrollLeft = LABEL_W + Math.max(0, hariIndex * DAY_W - wrap.clientWidth / 3);
    };
    root.querySelector("#g-collapse-all").onclick = () => {
      buildGroups(filtered()).forEach((g) => collapsed.add(g.major));
      persistCollapsed();
      render();
      WP.toast("Semua kelompok dilipat");
    };
    root.querySelector("#g-expand-all").onclick = () => {
      collapsed.clear();
      persistCollapsed();
      render();
      WP.toast("Semua kelompok dibuka");
    };

    function persist() {
      WP.save(state);
      window.__WP_STATE = state;
    }

    function persistCollapsed() {
      state.settings.collapsedWbs = Array.from(collapsed);
      persist();
    }

    function filtered() {
      return state.tasks.filter((t) => {
        if (ui.filterPhase !== "ALL" && t.phase !== ui.filterPhase) return false;
        if (ui.filterStatus !== "ALL" && t.status !== ui.filterStatus) return false;
        if (ui.cpOnly && !t.cp) return false;
        return true;
      });
    }

    function groupStats(tasks) {
      const n = tasks.length || 1;
      const done = tasks.filter((t) => t.status === "done").length;
      const progress = Math.round(tasks.reduce((s, t) => s + (Number(t.progress) || 0), 0) / n);
      const start = Math.min(...tasks.map((t) => t.start));
      const end = Math.max(...tasks.map((t) => t.end));
      const cp = tasks.some((t) => t.cp);
      return { done, total: tasks.length, progress, start, end, cp };
    }

    function buildGroups(list) {
      const order = [];
      const map = new Map();
      list.forEach((t) => {
        const major = wbsMajor(t);
        if (!map.has(major)) {
          map.set(major, {
            major,
            phase: t.phase,
            name: state.phases[t.phase] || t.phase,
            tasks: [],
          });
          order.push(major);
        }
        map.get(major).tasks.push(t);
      });
      return order.map((m) => map.get(m));
    }

    /** Baris yang tampil: header kelompok + task anak (jika tidak dilipat). */
    function buildRows(list) {
      const rows = [];
      buildGroups(list).forEach((g) => {
        const isCollapsed = collapsed.has(g.major);
        const stats = groupStats(g.tasks);
        rows.push({
          kind: "group",
          id: `group-${g.major}`,
          major: g.major,
          phase: g.phase,
          name: g.name,
          collapsed: isCollapsed,
          tasks: g.tasks,
          stats,
        });
        if (!isCollapsed) {
          g.tasks.forEach((t) => rows.push({ kind: "task", id: t.id, task: t }));
        }
      });
      return rows;
    }

    function xForDay(d) {
      return (d - dayMin) * DAY_W;
    }

    function barStyleRange(start, end) {
      const left = (start - dayMin) * DAY_W;
      const width = Math.max(DAY_W, (end - start) * DAY_W);
      return `left:${left}px;width:${width}px`;
    }

    function barStyle(t) {
      return barStyleRange(t.start, t.end);
    }

    function clearHighlight() {
      root.querySelectorAll("tr.row-selected, tr.row-pred, tr.row-succ").forEach((el) => {
        el.classList.remove("row-selected", "row-pred", "row-succ");
      });
      root.querySelectorAll(".bar.selected, .bar.hl-pred, .bar.hl-succ").forEach((el) => {
        el.classList.remove("selected", "hl-pred", "hl-succ");
      });
    }

    function relatedIds(t) {
      const preds = (t.deps || []).slice();
      const succs = state.tasks.filter((x) => (x.deps || []).includes(t.id)).map((x) => x.id);
      return { preds, succs };
    }

    function ensureGroupOpen(t) {
      const major = wbsMajor(t);
      if (collapsed.has(major)) {
        collapsed.delete(major);
        persistCollapsed();
        return true;
      }
      return false;
    }

    function markSelected(t) {
      if (!t) return;
      ui.selectedId = t.id;
      clearHighlight();

      const { preds, succs } = relatedIds(t);

      preds.forEach((id) => {
        const row = root.querySelector(`tr[data-id="${id}"]`);
        const bar = root.querySelector(`.bar[data-id="${id}"]`);
        if (row) row.classList.add("row-pred");
        if (bar) bar.classList.add("hl-pred");
      });

      succs.forEach((id) => {
        const row = root.querySelector(`tr[data-id="${id}"]`);
        const bar = root.querySelector(`.bar[data-id="${id}"]`);
        if (row) row.classList.add("row-succ");
        if (bar) bar.classList.add("hl-succ");
      });

      const row = root.querySelector(`tr[data-id="${t.id}"]`);
      const bar = root.querySelector(`.bar[data-id="${t.id}"]`);
      if (row) {
        row.classList.remove("row-pred", "row-succ");
        row.classList.add("row-selected");
      }
      if (bar) {
        bar.classList.remove("hl-pred", "hl-succ");
        bar.classList.add("selected");
      }
    }

    function focusOnTask(t, opts) {
      if (!t) return;
      const instant = !!(opts && opts.instant);
      if (ensureGroupOpen(t)) {
        render();
      }
      openSide(t);
      markSelected(t);

      const wrap = root.querySelector("#gantt-wrap");
      const row = root.querySelector(`tr[data-id="${t.id}"]`);
      if (!wrap || !row) return;

      const rowTop = row.offsetTop;
      const barLeft = LABEL_W + (t.start - dayMin) * DAY_W;
      const barWidth = Math.max(DAY_W, (t.end - t.start) * DAY_W);
      const targetX = Math.max(0, barLeft + barWidth / 2 - wrap.clientWidth / 2);
      const targetY = Math.max(0, rowTop - wrap.clientHeight / 3);

      wrap.scrollTo({
        left: targetX,
        top: targetY,
        behavior: instant ? "auto" : "smooth",
      });
    }

    function openSide(t) {
      ui.selectedId = t.id;
      const side = root.querySelector("#side");
      side.hidden = false;
      const startAbs = WP.absDate(state.settings, t.start) || "";
      const endAbs = WP.absDate(state.settings, t.end) || "";
      const preds = (t.deps || [])
        .map((id) => state.tasks.find((x) => x.id === id))
        .filter(Boolean);
      const succs = state.tasks.filter((x) => (x.deps || []).includes(t.id));
      side.innerHTML = `
        <button class="btn btn-ghost close" type="button" id="side-close">Tutup</button>
        <div class="row" style="align-items:flex-start;gap:8px;margin-bottom:6px">
          <h3 style="margin:0;flex:1">${t.wbs} · ${t.id}</h3>
          <button type="button" class="btn-info" id="s-help" title="Penjelasan pekerjaan">?</button>
        </div>
        <p style="margin:0 0 10px;font-size:13px">${t.name}</p>
        ${t.cp ? '<span class="pill cp">Jangan sampai telat</span>' : ""}
        <div style="height:10px"></div>
        <button class="btn" type="button" id="s-help2" style="width:100%;margin-bottom:10px">Apa artinya pekerjaan ini?</button>
        <div class="grid" style="gap:8px">
          <label class="field">Status
            <select id="s-status">
              <option value="todo">Belum mulai</option>
              <option value="doing">Sedang dikerjakan</option>
              <option value="done">Selesai</option>
              <option value="blocked">Terhambat</option>
            </select>
          </label>
          <label class="field">Berapa persen selesai?
            <input type="number" id="s-prog" min="0" max="100" value="${t.progress}" />
          </label>
          <label class="field">Mulai (hari sebelum/sesudah H, contoh -30)
            <input type="number" id="s-start" min="${dayMin}" max="${dayMax}" value="${t.start}" />
          </label>
          <label class="field">Selesai (hari, angka lebih besar dari mulai)
            <input type="number" id="s-end" min="${dayMin + 1}" max="${dayMax + 1}" value="${t.end}" />
          </label>
          <label class="field">Tanggal mulai di kalender
            <input type="date" id="s-start-abs" value="${startAbs}" ${state.settings.weddingDate ? "" : "disabled"} />
          </label>
          <label class="field">Tanggal selesai di kalender
            <input type="date" id="s-end-abs" value="${endAbs}" ${state.settings.weddingDate ? "" : "disabled"} />
          </label>
          <label class="field">Catatan
            <textarea id="s-notes" rows="3">${t.notes || ""}</textarea>
          </label>
        </div>
        <div style="height:10px"></div>
        <div class="small muted">Harus selesai dulu: ${
          preds.length
            ? preds.map((p) => `<button type="button" class="btn btn-ghost jump-rel" data-id="${p.id}" style="padding:2px 6px">${p.id}</button>`).join(" ")
            : "—"
        }</div>
        <div class="small muted">Pekerjaan berikutnya: ${
          succs.length
            ? succs.map((p) => `<button type="button" class="btn btn-ghost jump-rel" data-id="${p.id}" style="padding:2px 6px">${p.id}</button>`).join(" ")
            : "—"
        }</div>
        <div class="row" style="gap:8px;margin-top:8px;flex-wrap:wrap">
          <span class="pill" style="background:#ffedd5;border-color:#fdba74">Dipilih</span>
          <span class="pill" style="background:#e0f2fe;border-color:#7dd3fc;color:#0369a1">Sebelumnya</span>
          <span class="pill" style="background:#dcfce7;border-color:#86efac;color:#15803d">Selanjutnya</span>
        </div>
        <div class="small muted" style="margin-top:8px">${t.owner} · ${t.vendor} · ${state.phases[t.phase] || t.phase}</div>
        <div style="height:10px"></div>
        <button class="btn btn-primary" type="button" id="s-apply">Simpan perubahan</button>
      `;
      side.querySelector("#s-status").value = t.status;
      const openHelp = () => WPModal.openDefinition(t.id);
      side.querySelector("#s-help").onclick = openHelp;
      side.querySelector("#s-help2").onclick = openHelp;
      side.querySelector("#side-close").onclick = () => {
        side.hidden = true;
        ui.selectedId = null;
        clearHighlight();
      };
      side.querySelectorAll(".jump-rel").forEach((btn) => {
        btn.onclick = () => {
          const rel = state.tasks.find((x) => x.id === btn.dataset.id);
          if (rel) focusOnTask(rel);
        };
      });
      side.querySelector("#s-apply").onclick = () => {
        const task = state.tasks.find((x) => x.id === t.id);
        let start = Number(side.querySelector("#s-start").value);
        let end = Number(side.querySelector("#s-end").value);
        const sa = side.querySelector("#s-start-abs").value;
        const ea = side.querySelector("#s-end-abs").value;
        if (sa && state.settings.weddingDate) start = WP.dayFromAbs(state.settings, sa);
        if (ea && state.settings.weddingDate) end = WP.dayFromAbs(state.settings, ea);
        start = clamp(start, dayMin, dayMax);
        end = clamp(end, start + 1, dayMax + 1);
        task.start = start;
        task.end = end;
        task.status = side.querySelector("#s-status").value;
        task.progress = clamp(Number(side.querySelector("#s-prog").value) || 0, 0, 100);
        task.notes = side.querySelector("#s-notes").value;
        if (task.status === "done") task.progress = 100;
        state.tasks = WP.rescheduleFrom(state.tasks, task.id, state.settings);
        persist();
        render();
        const updated = state.tasks.find((x) => x.id === t.id);
        openSide(updated);
        markSelected(updated);
        WP.toast("Perubahan disimpan");
      };
    }

    function bindDrag(bar, t) {
      const onDown = (e) => {
        if (e.button !== 0) return;
        const handle = e.target.closest(".handle");
        const mode = handle ? (handle.classList.contains("left") ? "left" : "right") : "move";
        e.preventDefault();
        e.stopPropagation();
        openSide(t);
        markSelected(t);
        const startX = e.clientX;
        const origStart = t.start;
        const origEnd = t.end;
        const dur = origEnd - origStart;

        const onMove = (ev) => {
          const dx = Math.round((ev.clientX - startX) / DAY_W);
          let ns = origStart;
          let ne = origEnd;
          if (mode === "move") {
            ns = clamp(origStart + dx, dayMin, dayMax);
            ne = ns + dur;
            if (ne > dayMax + 1) {
              ne = dayMax + 1;
              ns = ne - dur;
            }
          } else if (mode === "left") {
            ns = clamp(origStart + dx, dayMin, origEnd - 1);
            ne = origEnd;
          } else {
            ns = origStart;
            ne = clamp(origEnd + dx, origStart + 1, dayMax + 1);
          }
          bar.style.left = (ns - dayMin) * DAY_W + "px";
          bar.style.width = Math.max(DAY_W, (ne - ns) * DAY_W) + "px";
          bar.dataset.tmpStart = ns;
          bar.dataset.tmpEnd = ne;
          bar.querySelector(".bar-label").textContent = WP.labelDay(ns) + "→" + WP.labelDay(ne);
        };

        const onUp = () => {
          document.removeEventListener("pointermove", onMove);
          document.removeEventListener("pointerup", onUp);
          const ns = Number(bar.dataset.tmpStart);
          const ne = Number(bar.dataset.tmpEnd);
          if (!Number.isFinite(ns) || !Number.isFinite(ne)) return;
          const task = state.tasks.find((x) => x.id === t.id);
          task.start = ns;
          task.end = ne;
          state.tasks = WP.rescheduleFrom(state.tasks, task.id, state.settings);
          persist();
          render();
          openSide(state.tasks.find((x) => x.id === t.id));
          WP.toast("Jadwal digeser");
        };

        document.addEventListener("pointermove", onMove);
        document.addEventListener("pointerup", onUp);
      };
      bar.addEventListener("pointerdown", onDown);
    }

    function drawDeps() {
      const svg = root.querySelector("#dep-layer");
      if (!svg) return;
      while (svg.lastChild && svg.lastChild.tagName !== "defs") svg.removeChild(svg.lastChild);
      if (!ui.showDeps) return;
      const list = filtered();
      const visibleTaskIds = new Set(
        buildRows(list).filter((r) => r.kind === "task").map((r) => r.id)
      );
      const layer = root.querySelector("#bars-layer");

      list.forEach((t) => {
        if (!visibleTaskIds.has(t.id)) return;
        (t.deps || []).forEach((depId) => {
          if (!visibleTaskIds.has(depId)) return;
          const pred = state.tasks.find((x) => x.id === depId);
          if (!pred) return;

          const barPred = layer && layer.querySelector(`.bar[data-id="${depId}"]`);
          const barSucc = layer && layer.querySelector(`.bar[data-id="${t.id}"]`);
          if (!barPred || !barSucc) return;
          const y1 = parseFloat(barPred.style.top) + BAR_H / 2;
          const y2 = parseFloat(barSucc.style.top) + BAR_H / 2;
          const x1 = xForDay(pred.end);
          const x2 = xForDay(t.start);
          const mid = (x1 + x2) / 2;
          const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
          const d =
            x2 >= x1
              ? `M ${x1} ${y1} C ${mid} ${y1}, ${mid} ${y2}, ${x2} ${y2}`
              : `M ${x1} ${y1} C ${x1 + 24} ${y1}, ${x2 - 24} ${y2}, ${x2} ${y2}`;
          path.setAttribute("d", d);
          if (t.cp && pred.cp) path.classList.add("cp");
          svg.appendChild(path);
        });
      });
    }

    function syncBarPositions(rows) {
      const layer = root.querySelector("#bars-layer");
      const thead = root.querySelector(".gantt-table thead");
      if (!layer) return;
      const headerH = thead ? thead.offsetHeight : HEADER_H;
      layer.style.top = headerH + "px";

      let maxBottom = 0;
      rows.forEach((row) => {
        const tr = root.querySelector(`tr[data-id="${row.id}"]`);
        const bar = layer.querySelector(`.bar[data-id="${row.id}"]`);
        if (!tr || !bar) return;
        const top = tr.offsetTop - headerH;
        const h = tr.offsetHeight || ROW_H;
        const barTop = top + Math.max(0, (h - BAR_H) / 2);
        bar.style.top = barTop + "px";
        maxBottom = Math.max(maxBottom, top + h);
      });

      if (maxBottom > 0) {
        layer.style.height = maxBottom + "px";
        const svg = root.querySelector("#dep-layer");
        if (svg) {
          svg.setAttribute("height", String(maxBottom));
          svg.style.height = maxBottom + "px";
        }
      }
      drawDeps();
    }

    function toggleGroup(major) {
      if (collapsed.has(major)) collapsed.delete(major);
      else collapsed.add(major);
      persistCollapsed();
      render();
    }

    function render() {
      const list = filtered();
      const rows = buildRows(list);
      const inner = root.querySelector("#gantt-inner");
      const totalW = LABEL_W + days.length * DAY_W;

      const headDays = days
        .map((d) => {
          const lab = d === 0 ? "H" : d % 5 === 0 || d === dayMin || d === dayMax ? WP.labelDay(d) : "";
          return `<th class="day-h ${d === 0 ? "hari" : ""}">${lab}</th>`;
        })
        .join("");

      const body = rows
        .map((row) => {
          const cells = days
            .map((d) => `<td class="day-cell ${d === 0 ? "hari" : ""}"></td>`)
            .join("");

          if (row.kind === "group") {
            const s = row.stats;
            const chev = row.collapsed ? "▸" : "▾";
            return `
            <tr data-id="${row.id}" data-kind="group" data-major="${row.major}" class="gantt-group-row ${row.collapsed ? "is-collapsed" : "is-open"}">
              <td class="meta-cell sticky-left">
                <div class="row group-meta" style="gap:8px;align-items:flex-start;flex-wrap:nowrap">
                  <button type="button" class="btn-collapse" data-major="${row.major}" title="${row.collapsed ? "Buka detail" : "Lipat"}" aria-expanded="${!row.collapsed}">${chev}</button>
                  <div style="min-width:0;flex:1">
                    <div class="title" title="${row.name}">${row.major}.x · ${row.name}</div>
                    <div class="sub">
                      <span class="pill">${s.done}/${s.total} selesai</span>
                      <span>${s.progress}%</span>
                      <span class="muted">${WP.labelDay(s.start)} → ${WP.labelDay(s.end)}</span>
                    </div>
                    <div class="group-progress-track" aria-hidden="true">
                      <span style="width:${s.progress}%"></span>
                    </div>
                  </div>
                </div>
              </td>
              ${cells}
            </tr>`;
          }

          const t = row.task;
          return `
          <tr data-id="${t.id}" data-kind="task" class="gantt-task-row">
            <td class="meta-cell sticky-left">
              <div class="row" style="gap:6px;align-items:flex-start;flex-wrap:nowrap">
                <div style="min-width:0;flex:1;padding-left:28px">
                  <div class="title" title="${t.name}">${t.wbs} ${t.name}</div>
                  <div class="sub">
                    <span class="pill ${t.status}">${WP.statusLabel(t.status)}</span>
                    ${t.cp ? '<span class="pill cp">Jangan telat</span>' : ""}
                    <span>${t.progress}%</span>
                    <span>${t.vendor}</span>
                  </div>
                </div>
                <button type="button" class="btn-info btn-def" data-id="${t.id}" title="Penjelasan">?</button>
              </div>
            </td>
            ${cells}
          </tr>`;
        })
        .join("");

      const chartW = days.length * DAY_W;
      const chartH = rows.length * ROW_H;
      inner.innerHTML = `
        <table class="gantt-table" style="width:${totalW}px">
          <thead>
            <tr>
              <th class="meta-cell sticky-left">Pekerjaan</th>
              ${headDays}
            </tr>
          </thead>
          <tbody>${body}</tbody>
        </table>
        <div id="bars-layer" style="position:absolute;left:${LABEL_W}px;top:42px;width:${chartW}px;height:${chartH}px;pointer-events:none;z-index:4">
          <svg class="dep-svg" id="dep-layer" width="${chartW}" height="${chartH}" style="position:absolute;inset:0;width:100%;height:100%">
            <defs>
              <marker id="arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
                <path d="M0,0 L6,3 L0,6 Z" fill="#a8a29e" />
              </marker>
            </defs>
          </svg>
        </div>
      `;

      const layer = inner.querySelector("#bars-layer");
      rows.forEach((row, i) => {
        if (row.kind === "group") {
          // Saat terbuka: bar kelompok tipis sebagai rentang; saat dilipat: bar penuh + isi progress
          const s = row.stats;
          const bar = document.createElement("div");
          bar.className = `bar group-bar ${s.cp ? "cp" : ""} ${s.progress >= 100 ? "done" : ""} ${row.collapsed ? "collapsed" : "open"}`;
          bar.dataset.id = row.id;
          bar.dataset.major = row.major;
          bar.style.cssText =
            barStyleRange(s.start, s.end) +
            `;top:${i * ROW_H + (ROW_H - BAR_H) / 2}px;height:${BAR_H}px;pointer-events:auto`;
          bar.innerHTML = `
            <span class="bar-fill" style="width:${s.progress}%"></span>
            <span class="bar-label">${WP.labelDay(s.start)}→${WP.labelDay(s.end)} · ${s.progress}%</span>
          `;
          bar.title = `${row.major}.x · ${row.name}\n${s.done}/${s.total} selesai · ${s.progress}%`;
          bar.onclick = () => toggleGroup(row.major);
          layer.appendChild(bar);
          return;
        }

        const t = row.task;
        const bar = document.createElement("div");
        const isSel = t.id === ui.selectedId;
        bar.className = `bar ${t.cp ? "cp" : ""} ${t.status === "done" ? "done" : ""} ${isSel ? "selected" : ""}`;
        bar.dataset.id = t.id;
        bar.style.cssText =
          barStyle(t) + `;top:${i * ROW_H + (ROW_H - BAR_H) / 2}px;height:${BAR_H}px;pointer-events:auto`;
        bar.innerHTML = `<span class="handle left"></span><span class="bar-label">${WP.labelDay(t.start)}→${WP.labelDay(t.end)}</span><span class="handle right"></span>`;
        bar.title = t.name;
        bar.onclick = (e) => {
          if (e.target.closest(".handle")) return;
          focusOnTask(t);
        };
        bindDrag(bar, t);
        layer.appendChild(bar);
      });

      inner.querySelectorAll(".btn-collapse").forEach((btn) => {
        btn.onclick = (e) => {
          e.stopPropagation();
          toggleGroup(btn.dataset.major);
        };
      });

      inner.querySelectorAll("tr[data-kind='group'] .meta-cell").forEach((cell) => {
        cell.onclick = (e) => {
          if (e.target.closest(".btn-collapse")) return;
          const tr = cell.closest("tr");
          if (tr) toggleGroup(tr.dataset.major);
        };
      });

      inner.querySelectorAll("tr[data-kind='task']").forEach((tr) => {
        tr.querySelector(".meta-cell").onclick = (e) => {
          if (e.target.closest(".btn-def")) return;
          const t = state.tasks.find((x) => x.id === tr.dataset.id);
          if (t) focusOnTask(t);
        };
      });
      inner.querySelectorAll(".btn-def").forEach((btn) => {
        btn.onclick = (e) => {
          e.stopPropagation();
          WPModal.openDefinition(btn.dataset.id);
        };
      });

      requestAnimationFrame(() => {
        syncBarPositions(rows);
        if (ui.selectedId) {
          const t = state.tasks.find((x) => x.id === ui.selectedId);
          if (t && !collapsed.has(wbsMajor(t))) {
            openSide(t);
            markSelected(t);
          }
        }
      });
    }

    render();
    const params = new URLSearchParams(location.search);
    const focusId = params.get("task");
    if (focusId) {
      const t = state.tasks.find((x) => x.id === focusId);
      if (t) {
        ui.filterPhase = "ALL";
        ui.filterStatus = "ALL";
        ui.cpOnly = false;
        phaseSel.value = "ALL";
        root.querySelector("#g-status").value = "ALL";
        root.querySelector("#g-cp").checked = false;
        collapsed.delete(wbsMajor(t));
        persistCollapsed();
        render();
        setTimeout(() => focusOnTask(t), 60);
      }
    } else {
      setTimeout(() => root.querySelector("#g-today").click(), 50);
    }

    return {
      reload() {
        state = WP.load();
        window.__WP_STATE = state;
        collapsed.clear();
        (state.settings.collapsedWbs || []).forEach((m) => collapsed.add(String(m)));
        render();
      },
    };
  }

  window.WPGantt = { initGantt };
})();
