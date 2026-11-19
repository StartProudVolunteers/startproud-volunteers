"""Build the simplified demo planner from Charlie's original.

    python3 tools/make_planner.py

Reads   planner/full/index.html  (Charlie's original, never edited)
Writes  planner/index.html       (Team B's 2-minute demo version)

Charlie's app is compiled React, so the demo version mostly *hides* things
with an extra stylesheet. Only a few text strings in his code are changed,
plus one inserted button. Every edit checks that it matched the expected
number of times, so if Charlie sends a new build this script fails loudly
instead of silently skipping a change.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "planner" / "full" / "index.html"
OUT = ROOT / "planner" / "index.html"

# Where the planner's buttons go on our site (relative to /planner/).
ASK_OOBS_URL = "../station.html?id=registration#ask"

html = SRC.read_text(encoding="utf-8")


def sub(old, new, count):
    """Replace exactly `count` occurrences of `old`, or stop with an error."""
    global html
    found = html.count(old)
    if found != count:
        raise SystemExit(f"Expected {count}x {old!r}, found {found}. Has the original changed?")
    html = html.replace(old, new)


# --- Venue: the team picked Hotel X Toronto ---------------------------------
sub("Harbour Grand Conference Hotel", "Hotel X Toronto", 2)
sub("under the Harbour Grand clock", "under the lobby clock", 1)
sub("floor plan of the Harbour Grand", "floor plan of Hotel X Toronto", 1)
sub('" \\xB7 HARBOUR GRAND"', '" \\xB7 HOTEL X TORONTO"', 1)  # map footer label
# Remove the Bay St. / Front St. entrance labels from the map...
sub('label:"Bay St. entrance"', 'label:""', 1)
sub('label:"Front St. entrance"', 'label:""', 1)
# ...and the same street names in directions and scenario text.
sub("Bay St. revolving doors", "main revolving doors", 3)
sub("blocking the Bay St. entrance", "blocking the main entrance", 1)
sub("crowded at the Bay St. doors", "crowded at the main doors", 2)
sub("crowding at the Bay St. entrance", "crowding at the main entrance", 1)
sub(", opposite the Front St. entrance", "", 1)

# --- Main volunteer is Ava Papanikolaou ---------------------------------------
sub("Alex Morgan", "Ava Papanikolaou", 2)
sub("Alex", "Ava", 7)  # the remaining first-name mentions

# --- Renames -------------------------------------------------------------------
sub("Event Command Centre", "Organizer dashboard", 2)
sub("Live Operations", "Live changes", 3)

# --- Own browser storage, so the full version's saved data never leaks in ------
sub('"start-proud-volunteeros-v1"', '"oobs-planner-demo-v1"', 1)
sub('"start-proud-volunteeros-ui-v1"', '"oobs-planner-demo-ui-v1"', 1)

# --- "Ask OOBS" button right under the Up next card -----------------------------
sub('a.default.createElement("div",{className:"p-contact"}',
    'a.default.createElement("a",{className:"btn primary ask-oobs",href:"' + ASK_OOBS_URL + '"},'
    '"\\u{1F4AC} Ask OOBS"),a.default.createElement("div",{className:"p-contact"}', 1)

# --- Force the light theme ---------------------------------------------------------
sub("<!doctype html><html>", '<!doctype html><html data-theme="light">', 1)

# --- Helper: tag the current view, and always open the volunteer view as Ava ----
HELPER = """<script>/* Team B demo helper */(function(){var d=document.documentElement;
function v(){d.setAttribute('data-view',(location.hash||'#dashboard').slice(1)||'dashboard')}
v();addEventListener('hashchange',v);
try{var k='oobs-planner-demo-ui-v1',u=JSON.parse(localStorage.getItem(k)||'{}');u.portalVol='v01';localStorage.setItem(k,JSON.stringify(u))}catch(e){}})();</script>
"""
sub("<title>Start Proud VolunteerOS (Copy)</title>",
    "<title>Start Proud VolunteerOS (Copy)</title>\n" + HELPER, 1)

DEMO_CSS = """<style>/* ===== Team B 2-minute demo: hides parts of Charlie's planner. Full version: /planner/full/ ===== */
/* Presentation Demo buttons and guided tour (we click through by hand) */
.demo-btn, .demo-top, .tour { display: none !important; }

/* Sidebar: Organizer dashboard, volunteer view, hotel map, Live changes, AI assistant only */
.nav-item[href="#directory"], .nav-item[href="#assignments"] { display: none !important; }

/* Organizer dashboard: headline, three numbers, Needs attention, Recent changes */
.dash { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px 14px; }
.dash > .hero, .dash > .grid-2 { grid-column: 1 / -1; }
.dash .hero .eyebrow, .dash .hero .hero-sub, .dash .hero .hero-actions { display: none; }
.dash > .kpis, .dash > .status-strip { display: contents; }
.dash .kpis > :nth-child(2), .dash .kpis > :nth-child(3) { display: none; }
.dash .status-strip > :not(.help) { display: none; }
.dash .ss.help { flex-direction: column-reverse; align-items: flex-start; justify-content: flex-end; gap: 4px;
  border-radius: var(--r); padding: 16px 18px 16px 22px; box-shadow: var(--shadow); }
.dash .ss.help span { font-size: 12px; font-weight: 700; letter-spacing: .03em; color: var(--muted); }
.dash .ss.help strong { font-size: 34px; font-weight: 750; line-height: 1.05; }
.dash .grid-2 > .card:not(:has(.att-list)):not(:has(.feed)) { display: none; }
@media (max-width: 560px) {
  .dash { gap: 14px 8px; }
  .dash .kpi, .dash .ss.help { padding: 12px 10px 12px 14px; }
  .dash .kpi-v, .dash .ss.help strong { font-size: 26px; }
  .dash .kpi-s { display: none; }
}

/* Volunteer view: no sidebar, event clock or login simulator; small link back */
html[data-view="my-schedule"] .sidebar, html[data-view="my-schedule"] .menu-btn,
html[data-view="my-schedule"] .scrim, html[data-view="my-schedule"] .clock,
html[data-view="my-schedule"] .sim-bar { display: none !important; }
html[data-view="my-schedule"] .shell { grid-template-columns: minmax(0, 1fr); }
html[data-view="my-schedule"] .topbar { padding-right: 170px; }
.oobs-org-link { display: none; }
html[data-view="my-schedule"] .oobs-org-link {
  display: inline-flex; align-items: center; gap: 6px; position: fixed; z-index: 31;
  top: calc(env(safe-area-inset-top, 0px) + 14px); right: max(16px, env(safe-area-inset-right, 0px));
  padding: 6px 12px; border-radius: 99px; border: 1px solid var(--border-2); background: var(--surface);
  color: var(--accent-ink); font: 600 13px var(--f-body); text-decoration: none; }
@media (max-width: 900px) { html[data-view="my-schedule"] .oobs-org-link { top: calc(env(safe-area-inset-top, 0px) + 12px); } }

/* Ask OOBS button under the Up next card */
.ask-oobs { min-height: 56px; font-size: 17px; font-weight: 700; border-radius: 14px; text-decoration: none; gap: 10px; }
</style>
<div id="root"></div>
<a class="oobs-org-link" href="#dashboard">← Organizer view</a>"""
sub('<div id="root"></div>', DEMO_CSS, 1)

OUT.write_text(html, encoding="utf-8")
print(f"Wrote {OUT.relative_to(ROOT)}")
