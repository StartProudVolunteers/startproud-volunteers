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

# Chat shown inside the planner's volunteer view (relative to /planner/).
CHAT_URL = "../chat.html?id=registration&embed=1"


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

# --- Four tabs with plain names (Live changes is folded into the dashboard) ----
sub('label:"My Volunteer Schedule",icon:"phone",badge:"Volunteer view"', 'label:"Volunteer schedule",icon:"phone"', 1)
sub('label:"Interactive Hotel Map",icon:"map"', 'label:"Hotel map",icon:"map"', 1)
sub('label:"AI Logistics Assistant",icon:"spark"', 'label:"AI assistant",icon:"spark"', 1)
sub("Demo scenario: Registration Desk B moves to the East Foyer",
    "Make a live change: move Registration Desk B to the East Foyer", 1)
# The dashboard page renders the dashboard *and* the Live changes page; CSS below
# keeps only the Desk B card from the second one and puts it under the numbers.
sub("ws={dashboard:rt,", "ws={dashboard:OobsDash,", 1)
sub("function Ss(){", "function OobsDash(){return I.default.createElement(I.default.Fragment,null,"
    "I.default.createElement(rt,null),I.default.createElement(Nt,null))}function Ss(){", 1)

# --- Own browser storage, so the full version's saved data never leaks in ------
sub('"start-proud-volunteeros-v1"', '"oobs-planner-demo-v1"', 1)
sub('"start-proud-volunteeros-ui-v1"', '"oobs-planner-demo-ui-v1"', 1)

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
/* Event clock: hidden on every tab. The demo stays at Fri, Apr 30, 10:30 AM. */
.topbar .clock { display: none !important; }

/* Four tabs: Organizer dashboard, Volunteer schedule, Hotel map, AI assistant */
.nav-item[href="#directory"], .nav-item[href="#assignments"], .nav-item[href="#operations"] { display: none !important; }

/* Organizer dashboard, top to bottom: headline, three numbers, the Desk B live change,
   Needs attention + Recent changes. Both pages' parts are laid out on one grid. */
html[data-view="dashboard"] .content { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px 14px; align-content: start; }
.dash, .dash ~ .ops, .dash > .kpis, .dash > .status-strip { display: contents; }
.dash > .hero { grid-column: 1 / -1; order: 1; }
.dash .kpi, .dash .ss.help { order: 2; }
.dash ~ .ops > .scenario { grid-column: 1 / -1; order: 3; }
.dash > .grid-2 { grid-column: 1 / -1; order: 4; }
.dash ~ .ops > :not(.scenario) { display: none; }
.dash .hero .eyebrow, .dash .hero .hero-sub, .dash .hero .hero-actions { display: none; }
.dash .kpis > :nth-child(2), .dash .kpis > :nth-child(3) { display: none; }
.dash .status-strip > :not(.help) { display: none; }
.dash .grid-2 > .card:not(:has(.att-list)):not(:has(.feed)) { display: none; }
/* No buttons that jump to pages outside the four tabs */
.dash .kpi, .dash .ss { pointer-events: none; }
.dash .card-h .btn { display: none; }
.dash .ss.help { flex-direction: column-reverse; align-items: flex-start; justify-content: flex-end; gap: 4px;
  border-radius: var(--r); padding: 16px 18px 16px 22px; box-shadow: var(--shadow); }
.dash .ss.help span { font-size: 12px; font-weight: 700; letter-spacing: .03em; color: var(--muted); }
.dash .ss.help strong { font-size: 34px; font-weight: 750; line-height: 1.05; }
@media (max-width: 560px) {
  html[data-view="dashboard"] .content { gap: 14px 8px; }
  .dash .kpi, .dash .ss.help { padding: 12px 10px 12px 14px; }
  .dash .kpi-v, .dash .ss.help strong { font-size: 26px; }
  .dash .kpi-s { display: none; }
  .dash ~ .ops .scn-done p { display: block; }
  .dash ~ .ops .scn-done p svg { vertical-align: -3px; margin-right: 4px; }
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


/* Ask OOBS: small floating button on the volunteer view; the chat slides in over the page */
.oobs-ask-fab { display: none; }
html[data-view="my-schedule"] .oobs-ask-fab {
  display: inline-flex; align-items: center; gap: 8px; position: fixed; z-index: 45;
  right: max(16px, env(safe-area-inset-right, 0px)); bottom: max(16px, env(safe-area-inset-bottom, 0px));
  padding: 12px 18px; border: 0; border-radius: 99px; cursor: pointer;
  background: var(--accent); color: #fff; font: 700 15px var(--f-body); box-shadow: var(--shadow-lg); }
.oobs-chat { position: fixed; inset: 0; z-index: 60; }
.oobs-chat-backdrop { position: absolute; inset: 0; background: rgba(17, 10, 30, .4); }
.oobs-chat-panel { position: absolute; top: 0; right: 0; bottom: 0; width: min(420px, 100%);
  background: var(--surface); display: flex; flex-direction: column; box-shadow: var(--shadow-lg);
  padding-top: env(safe-area-inset-top, 0px); }
.oobs-chat-panel header { display: flex; align-items: center; justify-content: space-between; gap: 8px;
  padding: 12px 12px 12px 18px; border-bottom: 1px solid var(--border); font: 700 17px var(--f-display); }
.oobs-chat-close { width: 40px; height: 40px; border: 0; border-radius: 99px; background: var(--surface-2);
  color: var(--fg); font-size: 22px; line-height: 1; cursor: pointer; }
.oobs-chat-panel iframe { flex: 1; width: 100%; border: 0; background: var(--surface); }
@media (max-width: 600px) {
  .oobs-chat-panel { top: auto; height: 88%; width: 100%; border-radius: 18px 18px 0 0; padding-top: 0; }
  html[data-view="my-schedule"] .oobs-ask-fab { padding: 10px 15px; font-size: 14px; }
}
</style>
<div id="root"></div>
<a class="oobs-org-link" href="#dashboard">← Organizer view</a>
<button class="oobs-ask-fab" type="button" aria-haspopup="dialog">💬 Ask OOBS</button>
<div class="oobs-chat" hidden>
  <div class="oobs-chat-backdrop"></div>
  <section class="oobs-chat-panel" role="dialog" aria-modal="true" aria-label="Ask OOBS">
    <header>💬 Ask OOBS<button class="oobs-chat-close" type="button" aria-label="Close chat">×</button></header>
    <iframe title="Ask OOBS chat"></iframe>
  </section>
</div>
<script>/* Team B: open the Ask OOBS chat in a panel instead of leaving the planner */(function(){
var fab=document.querySelector('.oobs-ask-fab'),box=document.querySelector('.oobs-chat'),
frame=box.querySelector('iframe'),close=box.querySelector('.oobs-chat-close');
function open(){if(!frame.src)frame.src="CHAT_URL";box.hidden=false;close.focus();}
function shut(){if(box.hidden)return;box.hidden=true;fab.focus();}
fab.addEventListener('click',open);close.addEventListener('click',shut);
box.querySelector('.oobs-chat-backdrop').addEventListener('click',shut);
addEventListener('keydown',function(e){if(e.key==='Escape')shut();});
addEventListener('message',function(e){if(e.origin===location.origin&&e.data&&e.data.oobs==='close-chat')shut();});
addEventListener('hashchange',function(){box.hidden=true;});})();</script>""".replace("CHAT_URL", CHAT_URL)
sub('<div id="root"></div>', DEMO_CSS, 1)

OUT.write_text(html, encoding="utf-8")
print(f"Wrote {OUT.relative_to(ROOT)}")
