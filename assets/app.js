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
  function findAnswer(question, station, globals) {
    var pool = (station.answers || []).map(function (a) { return { a: a, bonus: 0.5 }; })
      .concat((globals || []).map(function (a) { return { a: a, bonus: 0 }; }));
    var best = null, bestScore = 0;
    pool.forEach(function (p) {
      var sc = score(question, p.a);
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
  function leadLink(lead) {
    // sms: opens the phone's messaging app with the lead's (sample) number.
    return "sms:" + (lead && lead.phone ? lead.phone : "");
  }

  function setupCatchUp(data) {
    var c = data.catchUp || {};
    var backdrop = el("div", { "class": "sheet-backdrop", hidden: "" });
    var sheet = el("div", { "class": "sheet", role: "dialog", "aria-modal": "true", "aria-labelledby": "cu-title" });
    sheet.appendChild(el("h2", { id: "cu-title" }, "⚡ " + (c.title || "")));
    sheet.appendChild(el("p", { "class": "updated" }, c.updated || ""));
    var ol = el("ol");
    (c.lines || []).slice(0, 5).forEach(function (line) { ol.appendChild(el("li", null, line)); });
    sheet.appendChild(ol);
    var close = el("button", { "class": "btn", type: "button" }, data.ui.catchUpClose);
    sheet.appendChild(close);
    backdrop.appendChild(sheet);
    document.body.appendChild(backdrop);

    var opener = null;
    function open(e) { opener = e.currentTarget; backdrop.hidden = false; close.focus(); }
    function shut() { backdrop.hidden = true; if (opener) opener.focus(); }
    close.addEventListener("click", shut);
    backdrop.addEventListener("click", function (e) { if (e.target === backdrop) shut(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !backdrop.hidden) shut(); });

    document.querySelectorAll("[data-catchup]").forEach(function (b) {
      b.textContent = "⚡ " + data.ui.catchUpButton;
      b.addEventListener("click", open);
    });
  }

  /* ---------- home ---------- */
  function renderHome(data) {
    var list = document.getElementById("station-list");
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
    var id = new URLSearchParams(location.search).get("id");
    var s = data.stations.filter(function (x) { return x.id === id; })[0];
    if (!s) { location.replace("index.html"); return; }

    document.title = s.name + " · " + data.event.shortName + " Volunteer";
    document.getElementById("st-emoji").textContent = s.emoji || "📍";
    document.getElementById("st-name").textContent = s.name;
    document.getElementById("st-floor").textContent = s.floor;
    document.getElementById("st-shift").textContent = s.shift || "—";
    document.getElementById("st-lead").textContent = s.lead.name;
    document.getElementById("st-pronouns").textContent = s.lead.pronouns ? "(" + s.lead.pronouns + ")" : "";
    var msg = document.getElementById("st-lead-msg");
    msg.href = leadLink(s.lead);
    msg.querySelector("span").textContent = data.ui.fallbackButton + " " + s.lead.name.split(" ")[0];

    var tasks = document.getElementById("st-tasks");
    s.tasks.forEach(function (t) { tasks.appendChild(el("li", null, t)); });

    // chat
    var log = document.getElementById("chat-log");
    var form = document.getElementById("chat-form");
    var input = document.getElementById("chat-input");
    input.placeholder = data.ui.askPlaceholder;

    function say(text, who, extra) {
      var b = el("div", { "class": "msg msg-" + who + (extra ? " " + extra : "") }, text);
      log.appendChild(b);
      b.scrollIntoView({ block: "nearest", behavior: "smooth" });
      return b;
    }
    function ask(q) {
      q = q.trim();
      if (!q) return;
      say(q, "me");
      var hit = findAnswer(q, s, data.globalAnswers);
      if (hit) { say(hit.answer, "bot"); return; }
      {
        var b = say(data.ui.fallback, "bot", "msg-unsure");
        b.appendChild(el("br"));
        var a = el("a", { "class": "btn btn-small", href: leadLink(s.lead) },
          "💬 " + data.ui.fallbackButton + " " + s.lead.name);
        b.appendChild(a);
      }
    }
    form.addEventListener("submit", function (e) { e.preventDefault(); ask(input.value); input.value = ""; });

    var sugg = document.getElementById("suggestions");
    var suggested = (s.answers || []).filter(function (a) { return a.suggest; });
    suggested.forEach(function (a) {
      var chip = el("button", { "class": "chip", type: "button" }, a.question);
      chip.addEventListener("click", function () { ask(a.question); });
      sugg.appendChild(chip);
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
      if (page === "station") renderStation(data);
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
