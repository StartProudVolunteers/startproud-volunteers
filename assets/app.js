/* OOBS Volunteer Assistant — concept demo.
 * All words live in data/content.json. This file only renders them. */
(function () {
  "use strict";

  var DATA_URL = "data/content.json";

  function get(obj, path) {
    return path.split(".").reduce(function (o, k) { return o == null ? o : o[k]; }, obj);
  }
  function el(tag, attrs, text) {
    var n = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    if (text != null) n.textContent = text;
    return n;
  }
  function normalize(s) {
    return " " + String(s).toLowerCase()
      .normalize("NFD").replace(/[̀-ͯ]/g, "")   // résumé -> resume
      .replace(/[’']/g, "")                                 // can't -> cant
      .replace(/[^a-z0-9/+\- ]+/g, " ")
      .replace(/\s+/g, " ").trim() + " ";
  }

  /* ---------- keyword matching ---------- */
  // Score = number of keyword hits, longer phrases weigh more.
  // Single words match whole words (or the start of a word, so "harass" matches "harassed").
  function score(question, entry) {
    var q = normalize(question), s = 0;
    (entry.keywords || []).forEach(function (kw) {
      var k = normalize(kw).trim();
      if (!k) return;
      var hit = k.indexOf(" ") > -1 ? q.indexOf(" " + k + " ") > -1 || q.indexOf(" " + k) > -1
                                     : q.indexOf(" " + k) > -1;
      if (hit) s += k.split(" ").length;
    });
    // exact suggested question text always wins
    if (entry.question && normalize(entry.question) === q) s += 100;
    return s;
  }
  // primary answers (your station) get a small bonus over the rest
  function findAnswer(question, primary, others) {
    var pool = (primary || []).map(function (a) { return { a: a, bonus: 0.5 }; })
      .concat((others || []).map(function (a) { return { a: a, bonus: 0 }; }));
    var best = null, bestScore = 0;
    pool.forEach(function (p) {
      var sc = score(question, p.a);
      // safety answers ("escalate": true) always win when they match at all
      if (sc > 0 && p.a.escalate) sc += 1000;
      if (sc > 0 && sc + p.bonus > bestScore) { best = p.a; bestScore = sc + p.bonus; }
    });
    return best;
  }

  /* ---------- shared bits ---------- */
  function fillText(data) {
    document.querySelectorAll("[data-text]").forEach(function (n) {
      var v = get(data, n.getAttribute("data-text"));
      if (v != null) n.textContent = v;
    });
  }
  function byId(id) { return document.getElementById(id); }
  function stationById(data, id) { return data.stations.filter(function (x) { return x.id === id; })[0] || null; }
  // "My station" is remembered on this phone once a volunteer opens a station page or picks a lead.
  function myStation(data) { return stationById(data, store("oobs-station")); }
  function setMyStation(id) { store("oobs-station", id); }

  // Bottom sheet used for Catch me up, the lead picker and attendee questions.
  function makeSheet(closeText) {
    var backdrop = el("div", { "class": "sheet-backdrop", hidden: "" });
    var sheet = el("div", { "class": "sheet", role: "dialog", "aria-modal": "true" });
    var body = el("div");
    var close = el("button", { "class": "btn", type: "button" }, closeText);
    sheet.appendChild(body); sheet.appendChild(close); backdrop.appendChild(sheet);
    document.body.appendChild(backdrop);
    var opener = null;
    function shut() { backdrop.hidden = true; if (opener && opener.focus) opener.focus(); }
    close.addEventListener("click", shut);
    backdrop.addEventListener("click", function (e) { if (e.target === backdrop) shut(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !backdrop.hidden) shut(); });
    return {
      body: body,
      open: function (from) { opener = from || null; backdrop.hidden = false; close.focus(); },
      close: function () { opener = null; backdrop.hidden = true; }
    };
  }

  function setupCatchUp(data) {
    var c = data.catchUp || {};
    var sh = makeSheet(data.ui.catchUpClose);
    sh.body.appendChild(el("h2", null, "⚡ " + (c.title || "")));
    sh.body.appendChild(el("p", { "class": "updated" }, c.updated || ""));
    var ol = el("ol");
    (c.lines || []).slice(0, 5).forEach(function (line) { ol.appendChild(el("li", null, line)); });
    sh.body.appendChild(ol);
    document.querySelectorAll("[data-catchup]").forEach(function (b) {
      b.textContent = "⚡ " + data.ui.catchUpButton;
      b.addEventListener("click", function () { sh.open(b); });
    });
  }

  // Lead picker: "tel" to call, "sms" to message. Picking a row remembers that station.
  var leadSheet = null;
  function pickLead(data, kind, from) {
    var t = data.ui.pickLead;
    if (!leadSheet) leadSheet = makeSheet(data.ui.close);
    var b = leadSheet.body;
    b.innerHTML = "";
    b.appendChild(el("h2", null, t.title));
    b.appendChild(el("p", { "class": "updated" }, t.intro));
    var ul = el("ul", { "class": "lead-list" });
    data.stations.forEach(function (s) {
      var li = el("li");
      var txt = el("span");
      txt.appendChild(el("strong", null, (s.emoji || "") + " " + s.name));
      txt.appendChild(el("small", null, s.lead.name));
      li.appendChild(txt);
      var a = el("a", { "class": "btn btn-small", href: kind + ":" + s.lead.phone },
        (kind === "tel" ? "📞 " + t.call : "💬 " + t.message));
      a.addEventListener("click", function () { setMyStation(s.id); });
      li.appendChild(a);
      ul.appendChild(li);
    });
    b.appendChild(ul);
    leadSheet.open(from);
  }

  // Ask box shared by the home page and station pages.
  // opts.primary(): answers to prefer; opts.others(): the rest; opts.lead(): lead or null.
  function setupChat(data, opts) {
    var log = byId("chat-log"), form = byId("chat-form"), input = byId("chat-input");
    input.placeholder = opts.placeholder || data.ui.askPlaceholder;

    function say(text, who, extra) {
      var b = el("div", { "class": "msg msg-" + who + (extra ? " " + extra : "") }, text);
      log.appendChild(b);
      b.scrollIntoView({ block: "nearest", behavior: "smooth" });
      return b;
    }
    function ask(q) {
      q = String(q).trim();
      if (!q) return;
      say(q, "me");
      var hit = findAnswer(q, opts.primary(), opts.others());
      if (hit && hit.escalate) {
        var esc = data.escalation || {};
        var u = say("", "bot", "msg-urgent");
        u.appendChild(el("strong", { "class": "urgent-head" }, "🚨 " + esc.headline));
        if (esc.where) u.appendChild(el("span", { "class": "urgent-where" }, esc.where + (esc.name ? " · " + esc.name : "")));
        u.appendChild(el("span", { "class": "urgent-body" }, hit.answer));
        u.appendChild(el("a", { "class": "btn btn-urgent", href: "tel:" + (esc.phone || "") }, "📞 " + esc.callButton));
        return;
      }
      if (hit) { say(hit.answer, "bot"); return; }
      var f = say(data.ui.fallback, "bot", "msg-unsure");
      f.appendChild(el("br"));
      var lead = opts.lead();
      if (lead) {
        f.appendChild(el("a", { "class": "btn btn-small", href: "sms:" + lead.phone },
          "💬 " + data.ui.fallbackButton + " " + lead.name));
      } else {
        var pb = el("button", { "class": "btn btn-small", type: "button" }, "💬 " + data.ui.messageYourLead);
        pb.addEventListener("click", function () { pickLead(data, "sms", pb); });
        f.appendChild(pb);
      }
    }
    form.addEventListener("submit", function (e) { e.preventDefault(); ask(input.value); input.value = ""; });

    var sugg = byId("suggestions");
    if (sugg && opts.suggested) {
      opts.suggested.slice(0, 3).forEach(function (a) {   // max 3 suggested questions
        var chip = el("button", { "class": "chip", type: "button" }, a.question);
        chip.addEventListener("click", function () { ask(a.question); });
        sugg.appendChild(chip);
      });
    }
    return { ask: ask, input: input };
  }

  /* ---------- home ---------- */
  function bigButton(tag, attrs, emoji, label, sub) {
    var n = el(tag, attrs);
    n.classList.add("big-btn");
    n.appendChild(el("span", { "class": "big-emoji", "aria-hidden": "true" }, emoji));
    var t = el("span", { "class": "big-text" });
    t.appendChild(el("strong", null, label));
    if (sub) t.appendChild(el("small", null, sub));
    n.appendChild(t);
    return n;
  }
  function renderHome(data) {
    var h = data.ui.home, mine = myStation(data);
    var chat = setupChat(data, {
      placeholder: h.askPlaceholder,
      primary: function () { var m = myStation(data); return m ? m.answers : []; },
      others: function () {
        var m = myStation(data);
        return data.globalAnswers.concat.apply(data.globalAnswers,
          data.stations.filter(function (s) { return s !== m; }).map(function (s) { return s.answers || []; }));
      },
      lead: function () { var m = myStation(data); return m ? m.lead : null; }
    });

    var box = byId("big-buttons");
    var role = mine && data.myDay.roles.filter(function (r) { return r.station === mine.id; })[0];
    box.appendChild(bigButton("a", { href: "my-day.html" + (role ? "?role=" + encodeURIComponent(role.id) : "") },
      "🧭", h.where.label, h.where.sub));

    var call;
    if (mine) {
      call = bigButton("a", { href: "tel:" + mine.lead.phone }, "📞", h.call.label, mine.lead.name + " · " + mine.name);
    } else {
      call = bigButton("button", { type: "button" }, "📞", h.call.label, h.call.subUnknown);
      call.addEventListener("click", function () { pickLead(data, "tel", call); });
    }
    box.appendChild(call);

    var att = bigButton("button", { type: "button" }, "🙋", h.attendee.label, h.attendee.sub);
    var attSheet = makeSheet(data.ui.close);
    attSheet.body.appendChild(el("h2", null, "🙋 " + h.attendee.label));
    attSheet.body.appendChild(el("p", { "class": "updated" }, h.attendee.intro));
    var row = el("div", { "class": "sheet-chips" });
    data.globalAnswers.filter(function (a) { return a.suggest; }).forEach(function (a) {
      var c = el("button", { "class": "chip", type: "button" }, a.question);
      c.addEventListener("click", function () { attSheet.close(); chat.ask(a.question); });
      row.appendChild(c);
    });
    attSheet.body.appendChild(row);
    att.addEventListener("click", function () { attSheet.open(att); });
    box.appendChild(att);
  }

  /* ---------- stations list ---------- */
  function renderStations(data) {
    var list = byId("station-list");
    data.stations.forEach(function (s) {
      var li = el("li");
      var a = el("a", { "class": "station-link", href: "station.html?id=" + encodeURIComponent(s.id) });
      a.appendChild(el("span", { "class": "emoji", "aria-hidden": "true" }, s.emoji || "📍"));
      var txt = el("span");
      txt.appendChild(el("strong", null, s.name));
      txt.appendChild(el("small", null, s.floor));
      a.appendChild(txt);
      a.appendChild(el("span", { "class": "chev", "aria-hidden": "true" }, "›"));
      li.appendChild(a);
      list.appendChild(li);
    });
  }

  /* ---------- station ---------- */
  function renderStation(data) {
    var s = stationById(data, new URLSearchParams(location.search).get("id"));
    if (!s) { location.replace("stations.html"); return; }
    setMyStation(s.id);

    document.title = s.name + " · " + data.ui.header;
    byId("st-emoji").textContent = s.emoji || "📍";
    byId("st-name").textContent = s.name;
    byId("st-floor").textContent = s.floor;
    byId("st-shift").textContent = s.shift || "—";
    byId("st-lead").textContent = s.lead.name;
    byId("st-pronouns").textContent = s.lead.pronouns ? "(" + s.lead.pronouns + ")" : "";
    var msg = byId("st-lead-msg");
    msg.href = "sms:" + s.lead.phone;
    msg.textContent = "💬 " + data.ui.fallbackButton + " " + s.lead.name.split(" ")[0];

    // "See it on the map": per-station mapUrl, else the shared placeholder template
    var mapUrl = s.mapUrl || ((data.links && data.links.mapUrl) || "").replace("{station}", encodeURIComponent(s.id));
    var mapBtn = byId("st-map");
    if (mapUrl) { mapBtn.href = mapUrl; mapBtn.textContent = "🗺️ " + data.ui.mapButton + " ↗"; } else mapBtn.hidden = true;

    var tasks = byId("st-tasks");
    s.tasks.forEach(function (t) { tasks.appendChild(el("li", null, t)); });

    setupChat(data, {
      primary: function () { return s.answers; },
      others: function () { return data.globalAnswers; },
      lead: function () { return s.lead; },
      suggested: (s.answers || []).filter(function (a) { return a.suggest; })
    });
  }

  /* ---------- my day ---------- */
  function toMin(t) { var p = String(t).split(":"); return (+p[0]) * 60 + (+p[1]); }
  function fmt(t) {
    var m = typeof t === "number" ? t : toMin(t), h = Math.floor(m / 60), mm = m % 60;
    return ((h + 11) % 12 + 1) + ":" + (mm < 10 ? "0" : "") + mm + " " + (h < 12 ? "AM" : "PM");
  }
  function store(k, v) {
    try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; }
  }
  var SVG = "http://www.w3.org/2000/svg";
  function svg(tag, attrs, text) {
    var n = document.createElementNS(SVG, tag);
    Object.keys(attrs || {}).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    if (text != null) n.textContent = text;
    return n;
  }

  // Stacked-floor sketch: top floor first, each floor a slab split into rooms by 'size'.
  function drawMap(md, activeRoom) {
    var W = 340, slabH = 58, gap = 16, labelW = 50, depth = 7;
    var H = md.floors.length * (slabH + gap) + depth;
    var root = svg("svg", { viewBox: "0 0 " + W + " " + H, "class": "venue-map", role: "img" });
    var activeFloor = null;
    md.floors.forEach(function (f) { f.rooms.forEach(function (r) { if (r.id === activeRoom) activeFloor = f; }); });
    root.setAttribute("aria-label", activeFloor
      ? "Venue map. Highlighted: " + activeFloor.name + ", " + roomById(md, activeRoom).name
      : "Venue map");

    md.floors.forEach(function (f, i) {
      var y = depth + i * (slabH + gap), x0 = labelW, w = W - labelW - depth - 2;
      var on = f === activeFloor;
      var g = svg("g", { "class": "floor" + (on ? " is-active" : "") });
      // slab "thickness" to read as stacked floors
      g.appendChild(svg("rect", { "class": "slab-side", x: x0 + depth, y: y - depth, width: w, height: slabH, rx: 4 }));
      g.appendChild(svg("rect", { "class": "slab", x: x0, y: y, width: w, height: slabH, rx: 4 }));
      g.appendChild(svg("text", { "class": "floor-label", x: labelW - 8, y: y + slabH / 2 + 4, "text-anchor": "end" },
        f.id === "G" ? "G" : f.id));
      var total = f.rooms.reduce(function (a, r) { return a + (r.size || 1); }, 0), pad = 5, rx = x0 + pad;
      var inner = w - pad * 2 - pad * (f.rooms.length - 1);
      f.rooms.forEach(function (r) {
        var rw = inner * (r.size || 1) / total, hit = r.id === activeRoom;
        var rg = svg("g", { "class": "room" + (hit ? " is-active" : "") });
        rg.appendChild(svg("rect", { x: rx, y: y + pad, width: rw, height: slabH - pad * 2, rx: 3 }));
        var words = r.short.split(" "), lines = [""];
        // wrap label to fit the room box (approx 6.1px per char at 11px)
        words.forEach(function (wd) {
          var cur = lines[lines.length - 1];
          if ((cur + " " + wd).trim().length * 6.1 > rw - 8 && cur) lines.push(wd);
          else lines[lines.length - 1] = (cur + " " + wd).trim();
        });
        lines.forEach(function (ln, li) {
          rg.appendChild(svg("text", { x: rx + rw / 2, y: y + slabH / 2 + 4 + (li - (lines.length - 1) / 2) * 12,
            "text-anchor": "middle" }, ln));
        });
        if (hit) rg.appendChild(svg("circle", { "class": "pin", cx: rx + rw - 8, cy: y + pad + 8, r: 4 }));
        g.appendChild(rg);
        rx += rw + pad;
      });
      root.appendChild(g);
    });
    var holder = document.getElementById("map");
    holder.innerHTML = "";
    holder.appendChild(root);
  }
  function roomById(md, id) {
    var found = null;
    md.floors.forEach(function (f) { f.rooms.forEach(function (r) { if (r.id === id) found = { name: r.name, floor: f.name }; }); });
    return found || { name: id, floor: "" };
  }

  function renderMyDay(data) {
    var md = data.myDay;
    var params = new URLSearchParams(location.search);
    var fromStation = md.roles.filter(function (r) { return r.station === store("oobs-station"); })[0];
    var roleId = params.get("role") || store("oobs-role") || (fromStation && fromStation.id) || md.roles[0].id;
    if (!md.roles.some(function (r) { return r.id === roleId; })) roleId = md.roles[0].id;
    var picked = null;           // slot index the user tapped (overrides "now" on the map)
    var manualClock = null;      // minutes, when the user set the clock

    var clockIn = document.getElementById("clock-input");
    var badge = document.getElementById("clock-badge");
    var realBtn = document.getElementById("clock-real");

    function nowMin() {
      if (manualClock != null) return { m: manualClock, demo: true };
      var d = new Date(), m = d.getHours() * 60 + d.getMinutes();
      if (m < toMin(md.eventHours.start) || m > toMin(md.eventHours.end)) return { m: toMin(md.demoTime), demo: true };
      return { m: m, demo: false };
    }

    var chips = document.getElementById("role-chips");
    md.roles.forEach(function (r) {
      var b = el("button", { "class": "chip role-chip", type: "button", "data-role": r.id }, (r.emoji || "") + " " + r.name);
      b.addEventListener("click", function () {
        roleId = r.id; picked = null; store("oobs-role", r.id); if (r.station) setMyStation(r.station);
        history.replaceState(null, "", "?role=" + encodeURIComponent(r.id));
        render();
      });
      chips.appendChild(b);
    });
    clockIn.addEventListener("change", function () {
      if (!clockIn.value) return;
      manualClock = toMin(clockIn.value); picked = null; render();
    });
    realBtn.addEventListener("click", function () { manualClock = null; picked = null; render(); });

    function render() {
      var role = md.roles.filter(function (r) { return r.id === roleId; })[0];
      var t = nowMin();
      chips.querySelectorAll(".role-chip").forEach(function (c) {
        c.setAttribute("aria-pressed", String(c.getAttribute("data-role") === roleId));
      });
      var hh = Math.floor(t.m / 60), mm = t.m % 60;
      clockIn.value = (hh < 10 ? "0" : "") + hh + ":" + (mm < 10 ? "0" : "") + mm;
      badge.hidden = !t.demo;
      realBtn.hidden = manualClock == null;

      var slots = role.slots, cur = -1, nxt = -1;
      slots.forEach(function (s, i) {
        if (t.m >= toMin(s.start) && t.m < toMin(s.end)) cur = i;
        if (nxt < 0 && toMin(s.start) > t.m) nxt = i;
      });

      // Now card
      var card = document.getElementById("now-card");
      card.innerHTML = "";
      var focus = cur >= 0 ? cur : nxt;
      if (cur >= 0) {
        var s = slots[cur], loc = roomById(md, s.room);
        card.appendChild(el("p", { "class": "now-label" }, md.now + " · " + fmt(s.start) + "–" + fmt(s.end)));
        card.appendChild(el("p", { "class": "now-title" }, s.title));
        card.appendChild(el("p", { "class": "now-where" }, "📍 " + loc.floor + " · " + loc.name));
        if (nxt >= 0) card.appendChild(el("p", { "class": "now-next" },
          md.upNext + ": " + slots[nxt].title + " at " + fmt(slots[nxt].start)));
      } else if (nxt >= 0) {
        var n = slots[nxt], nl = roomById(md, n.room);
        var lead = t.m < toMin(slots[0].start) ? md.beforeStart : md.between;
        card.appendChild(el("p", { "class": "now-label" }, md.next));
        card.appendChild(el("p", { "class": "now-title" }, lead + " " + fmt(n.start) + ": " + n.title));
        card.appendChild(el("p", { "class": "now-where" }, "📍 " + nl.floor + " · " + nl.name));
      } else {
        card.appendChild(el("p", { "class": "now-title" }, md.allDone));
      }

      // Timeline
      document.getElementById("tl-title").textContent = (role.emoji || "") + " " + role.name;
      var tl = document.getElementById("timeline");
      tl.innerHTML = "";
      slots.forEach(function (s, i) {
        var loc = roomById(md, s.room);
        var state = i === cur ? "is-now" : (toMin(s.end) <= t.m ? "is-past" : "");
        var li = el("li", { "class": "slot " + state + (picked === i ? " is-picked" : "") });
        var btn = el("button", { type: "button", "aria-pressed": String(picked === i) });
        btn.appendChild(el("span", { "class": "slot-time" }, fmt(s.start) + " – " + fmt(s.end)));
        var body = el("span", { "class": "slot-body" });
        body.appendChild(el("strong", null, s.title + (i === cur ? "  · " + md.now : "")));
        body.appendChild(el("span", { "class": "slot-where" }, loc.floor + " · " + loc.name));
        if (s.note) body.appendChild(el("span", { "class": "slot-note" }, s.note));
        btn.appendChild(body);
        btn.addEventListener("click", function () { picked = picked === i ? null : i; render(); });
        li.appendChild(btn);
        tl.appendChild(li);
      });

      // Map: tapped slot, else current, else next
      var show = picked != null ? picked : focus;
      var room = show >= 0 ? slots[show].room : null;
      drawMap(md, room);
      var cap = document.getElementById("map-caption");
      if (room) {
        var rl = roomById(md, room);
        cap.textContent = (show === cur ? md.now : fmt(slots[show].start)) + ": " + rl.floor + " · " + rl.name;
      } else cap.textContent = "";

      var sl = document.getElementById("station-link");
      var st = data.stations.filter(function (x) { return x.id === role.station; })[0];
      sl.hidden = !st;
      if (st) { sl.href = "station.html?id=" + st.id; sl.textContent = (st.emoji || "") + " " + st.name + " station page →"; }
    }
    render();
    setInterval(function () { if (manualClock == null) render(); }, 60000);
  }

  /* ---------- nav ---------- */
  function addMyDayLinks(data, stationId) {
    var role = stationId && data.myDay.roles.filter(function (r) { return r.station === stationId; })[0];
    document.querySelectorAll("[data-myday]").forEach(function (a) {
      a.href = "my-day.html" + (role ? "?role=" + encodeURIComponent(role.id) : "");
      a.textContent = "🗓️ " + data.ui.myDay;   // only small top-bar links use data-myday
    });
  }

  /* ---------- boot ---------- */
  fetch(DATA_URL, { cache: "no-cache" })
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(function (data) {
      fillText(data);
      setupCatchUp(data);
      var page = document.body.getAttribute("data-page");
      if (page === "home") renderHome(data);
      if (page === "stations") renderStations(data);
      if (page === "station") renderStation(data);
      if (page === "myday") renderMyDay(data);
      addMyDayLinks(data, page === "station" ? new URLSearchParams(location.search).get("id") : null);
    })
    .catch(function (err) {
      var main = document.querySelector("main");
      main.innerHTML = "";
      main.appendChild(el("p", { "class": "error" },
        "Couldn't load data/content.json (" + err.message + "). If you opened this file directly, run a local server " +
        "(python3 -m http.server) — or check the JSON for a missing comma or quote."));
    });

  // exposed for quick testing in the console
  window.OOBS = { findAnswer: findAnswer, normalize: normalize };
})();
