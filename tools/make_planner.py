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
# Ava uses she/her
sub('R("v01","Ava Papanikolaou","they/them"', 'R("v01","Ava Papanikolaou","she/her"', 1)
sub("Ava only sees their own shifts", "Ava only sees her own shifts", 1)
sub("log in as Ava to see exactly what they see", "log in as Ava to see exactly what she sees", 1)

# --- Renames -------------------------------------------------------------------
sub("Event Command Centre", "Organizer dashboard", 2)
sub('onClick:()=>l.go("operations")},"Open Live Operations")', 'onClick:()=>l.go("dashboard")},"Open dashboard")', 1)
sub("Logged from Live Operations.", "Logged from the organizer dashboard.", 1)
sub("Live Operations", "Live changes", 1)  # the (hidden) tab label
# "Resume" without accents (Charlie's code writes é as \xE9)
sub("R\\xE9sum\\xE9", "Resume", 3)
sub("r\\xE9sum\\xE9", "resume", 3)

# --- Four tabs with plain names (Live changes is folded into the dashboard) ----
sub('label:"My Volunteer Schedule",icon:"phone",badge:"Volunteer view"', 'label:"Volunteer dashboard",icon:"phone"', 1)
sub('label:"Interactive Hotel Map",icon:"map"', 'label:"Hotel map",icon:"map"', 1)
# (AI assistant tab is hidden with CSS below)
sub("Demo scenario: Registration Desk B moves to the East Foyer",
    "Live change: move Desk B to the East Foyer", 1)
sub("The lobby is crowding at the main entrance. Move Desk B once and every affected schedule updates.",
    "The lobby is too crowded. One tap moves the desk and tells every volunteer working there.", 1)
# Plain names for the two one-tap change cards brought onto the dashboard
sub('"Missing volunteer coverage"', '"Fill open shifts"', 1)
sub('"Upcoming and current shifts below their headcount"', '"Tap Add to put a free volunteer on the shift"', 1)
sub('"Unresolved issues"', '"Problems reported"', 1)
sub('placeholder:"Log a new issue\\u2026"', 'placeholder:"Report a new problem\\u2026"', 1)
sub('"Log")', '"Report")', 1)
# The dashboard page renders the dashboard *and* the Live changes page; CSS below
# keeps only the Desk B card from the second one and puts it under the numbers.
sub("ws={dashboard:rt,", "ws={dashboard:OobsDash,", 1)
sub("function Ss(){", "function OobsDash(){return I.default.createElement(I.default.Fragment,null,"
    "I.default.createElement(rt,null),I.default.createElement(Nt,null))}function Ss(){", 1)

# --- Presentation Demo: Charlie's guided tour with new steps for this version -----
# A step can name `sel` (any CSS selector) instead of a data-tour `target`;
# every visible match glows.
sub('let S=document.querySelector(`[data-tour="${Je[s.step].target}"]`);S&&(S.classList.add("tour-glow"),S.scrollIntoView({block:"center",behavior:"smooth"}))',
# Only change page when the step is on a different page: changing page jumps to the
# top, so doing it on every step made the view bounce up and back down.
    'let S=[...document.querySelectorAll(Je[s.step].sel||`[data-tour="${Je[s.step].target}"]`)].filter(x=>x.offsetParent!==null||getComputedStyle(x).position==="fixed");'
    'S.forEach(x=>x.classList.add("tour-glow"));S[0]&&S[0].scrollIntoView({block:"center",behavior:"smooth"})', 1)
DASH = 'e.setVolDrawer(null),e.setPortalTask(null),e.setNotifOpen(!1),(e.page!=="dashboard"&&e.go("dashboard"))'
PORTAL = 'e.setVolDrawer(null),e.setPortalVol("v01"),e.setNotifOpen(!1),(e.page!=="my-schedule"&&e.go("my-schedule"))'
STEPS = [
  # Organizer dashboard
  ('Organizer dashboard', 'sel:".topbar .tb-title"',
   "This is the organizer's view of Out on Bay Street 2027 at Hotel X Toronto: everything happening across the event, on one screen.", DASH),
  ('Three numbers at a glance', 'sel:".dash .kpi, .dash .ss.help"',
   "How many volunteers we have, how many are on shift right now, and how many things need attention: open problems plus tasks flagged as needing help.", DASH),
  ('Make a live change', 'target:"scenario",action:"Move Desk B now"',
   "The lobby is too crowded, so we move Registration Desk B to the East Foyer. One tap, and every volunteer working there is told automatically.", DASH),
  ('Fix problems in one tap', 'sel:".dash ~ .ops .card:has(.issues)"',
   "Problems volunteers report land here. Tap Resolve when one is fixed, or type a new one and tap Report.", DASH),
  ('Fill open shifts', 'sel:".dash ~ .ops .card:has(.gaps)"',
   "Shifts that are short-staffed, each with a free volunteer suggested. One tap adds them and updates their schedule.", DASH),
  ('Every change is logged', 'sel:".dash .card:has(.feed)"',
   "Every edit, including the Desk B move we just made, is logged here, so the whole team works from one version of the truth.", DASH),
  # Volunteer Directory
  ('Volunteer Directory', 'sel:\'html[data-view="directory"] .content > .page > .toolbar\'',
   "All 30 volunteers in one place. Search by name or skill, filter by team, volunteer type, onboarding or experience, and switch between cards and a table.",
   'e.setVolDrawer(null),e.setPortalTask(null),(e.page!=="directory"&&e.go("directory"))'),
  ("A volunteer's profile", 'sel:".drawer"',
   "Tap anyone to see their profile: role, supervisor, onboarding, skills and every shift. View as this volunteer opens their own dashboard.",
   '(e.page!=="directory"&&e.go("directory")),e.setVolDrawer("v01")'),
  # Volunteer dashboard
  ('Volunteer dashboard', 'target:"up-next"',
   "Now the volunteer's point of view. Ava is a first-time volunteer who signed up 48 hours before the event. Up next tells her exactly where to be right now.",
   'e.setPortalTask(null),' + PORTAL),
  ('Her schedule updated itself', 'target:"change-banner"',
   "Because we moved Desk B, Ava's shifts already show the East Foyer, with a note explaining why. Nobody had to phone or email her.",
   'e.setPortalTask(null),' + PORTAL),
  ('Only her own shifts', 'target:"p-list"',
   "Ava sees only her own shifts, each with a time, room, floor and status.",
   'e.setPortalTask(null),' + PORTAL),
  ('One tap for full instructions', 'target:"sheet-loc"',
   "Opening a shift shows directions, her tasks, her teammates, and her supervisor with their radio channel.",
   PORTAL + ',e.setPortalTask("a22")'),
  ('Ask OOBS', 'sel:".oobs-ask-fab"',
   "Questions? Ask OOBS opens our volunteer chatbot right here: where Desk B moved, washrooms, lunch, or who to call in an emergency.",
   'e.setPortalTask(null),' + PORTAL),
  # Hotel map
  ('Hotel map', 'target:"floorplan"',
   "Finally, the hotel map: every room on every floor. Any shift can be highlighted, here the East Foyer, where Desk B now sits.",
   'e.setVolDrawer(null),e.setPortalTask(null),e.showOnMap("eastFoyer",null)'),
]
import json as _json
def _step(t):
    title, where, say, enter = t
    extra = ''
    if 'action:' in where:
        extra = ',next:({data:e})=>{e.state.scenarioDone||e.relocateDeskB("Lobby is crowded at the main doors. Use the glass doors at the east end of the lobby.")}'
    return '{title:' + _json.dumps(title) + ',' + where + ',say:' + _json.dumps(say) + ',enter:({ui:e})=>{' + enter + '}' + extra + '}'
NEW_TOUR = 'var Je=[' + ','.join(_step(t) for t in STEPS) + '];function St(){'
_a = html.index('var Je=[{title:"The Organizer dashboard"')
_b = html.index('}}];function St(){', _a) + len('}}];function St(){')
html = html[:_a] + NEW_TOUR + html[_b:]

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
/* Presentation Demo: Charlie's guided tour (Team B's steps). Start it from the dashboard. */
html[data-view="my-schedule"] .demo-top { display: none !important; }
.oobs-ask-fab.tour-glow { position: fixed !important; z-index: 45 !important; }
html:has(.tour) .oobs-ask-fab { bottom: auto !important; top: calc(env(safe-area-inset-top, 0px) + 80px) !important; }
/* Event clock: hidden on every tab. The demo stays at Fri, Apr 30, 10:30 AM. */
.topbar .clock { display: none !important; }

/* Four tabs: Organizer dashboard, Volunteer Directory (as Charlie built it), Volunteer dashboard, Hotel map */
.nav-item[href="#assignments"], .nav-item[href="#operations"],
.nav-item[href="#assistant"] { display: none !important; }
.ai-badge { display: none !important; }
/* Volunteer Directory cards: hide the "Joined [date]" label (it overlapped long names) */
.vc-joined { display: none !important; }

/* Organizer dashboard, top to bottom: three numbers, the live change,
   Problems reported + Fill open shifts (one-tap changes), Recent changes.
   Parts of both pages are laid out on one grid. */
html[data-view="dashboard"] .content { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px 14px; align-content: start; }
.dash, .dash ~ .ops, .dash > .kpis, .dash > .status-strip { display: contents; }
/* The big purple "Every volunteer knows where to be..." banner: removed */
.dash > .hero { display: none !important; }
.dash .kpi, .dash .ss.help { order: 2; }
/* Live change card, simplified: what moves where, and one button */
.dash ~ .ops > .scenario { grid-column: 1 / -1; order: 3; }
.dash ~ .ops .scenario .scn-aff, .dash ~ .ops .scenario .scn-list,
.dash ~ .ops .scenario .fld, .dash ~ .ops .scenario .hint { display: none; }
.dash ~ .ops .scn-loc.from strong { text-decoration: none; }
.dash ~ .ops > .grid-2 { grid-column: 1 / -1; order: 4; }
.dash > .grid-2 { grid-column: 1 / -1; order: 5; grid-template-columns: minmax(0, 1fr); }
.dash ~ .ops > :not(.grid-2):not(.scenario) { display: none; }
.dash ~ .ops > .grid-2 > .card:not(:has(.issues)):not(:has(.gaps)) { display: none; }
.dash .hero .eyebrow, .dash .hero .hero-sub, .dash .hero .hero-actions { display: none; }
.dash .kpis > :nth-child(2), .dash .kpis > :nth-child(3) { display: none; }
.dash .status-strip > :not(.help) { display: none; }
.dash > .grid-2 > .card:not(:has(.feed)) { display: none; }
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
