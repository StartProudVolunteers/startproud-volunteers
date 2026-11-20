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
# The note volunteers get when Desk B moves (also used by the Presentation Demo).
DESK_B_NOTE = "Lobby is crowded at the main doors. Desk B is now in Gallery X, next to the coat check, just off the lobby."


html = SRC.read_text(encoding="utf-8")


def sub(old, new, count):
    """Replace exactly `count` occurrences of `old`, or stop with an error.
    count=None replaces however many there are (used for catch-all renames)."""
    global html
    found = html.count(old)
    if count is not None and found != count:
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

# --- Presentation Demo: Charlie's guided tour with Team B's script ---------------
# A step can name `sel` (any CSS selector) instead of a data-tour `target`;
# every visible match glows.
sub('let S=document.querySelector(`[data-tour="${Je[s.step].target}"]`);S&&(S.classList.add("tour-glow"),S.scrollIntoView({block:"center",behavior:"smooth"}))',
    'let S=[...document.querySelectorAll(Je[s.step].sel||`[data-tour="${Je[s.step].target}"]`)].filter(x=>x.offsetParent!==null||getComputedStyle(x).position==="fixed"||x instanceof SVGElement);'
    'S.forEach(x=>x.classList.add("tour-glow"));S[0]&&S[0].scrollIntoView({block:"center",behavior:"smooth"})', 1)
# Only change page when the step is on a different page: changing page jumps to the
# top, so doing it on every step made the view bounce up and back down.
def go(page):
    return '(e.page!=="%s"&&e.go("%s"))' % (page, page)
DASH = 'e.setVolDrawer(null),e.setPortalTask(null),e.setNotifOpen(!1),' + go("dashboard")
PORTAL = 'e.setVolDrawer(null),e.setPortalVol("v01"),e.setNotifOpen(!1),' + go("my-schedule")
MAP = 'e.setVolDrawer(null),e.setPortalTask(null),e.setMapFocus(null),' + go("map")
NOTHING = 'sel:".oobs-no-highlight"'   # matches nothing: no glow on this step
# (title, what glows, caption, what the step opens). The captions are short on purpose:
# the presenters do the talking.
STEPS = [
  # --- Charlie ---
  ('Organizer dashboard', 'sel:".topbar .tb-title, .dash .kpi, .dash .ss.help"',
   "The whole event on one screen", DASH),
  ('Move Desk B', 'target:"scenario",action:"Move Desk B now"',          # Next moves Desk B
   "One tap moves Desk B and tells 4 volunteers", DASH),
  ('Problems and open shifts', 'sel:".dash ~ .ops .card:has(.issues), .dash ~ .ops .card:has(.gaps)"',
   "Problems and empty shifts, fixed in one tap", DASH),
  ("Ava's itinerary", 'sel:".drawer"',
   "Ava's itinerary, set by organizers",
   'e.setPortalTask(null),' + go("directory") + ',e.setVolDrawer("v01")'),
  # --- Pransh ---
  ('Every room, every floor', NOTHING,
   "Every room, on every floor",
   MAP + ',window.oobsMapPick("floors","Ground Floor"),window.oobsMapPick("days","Both days")'),
  ('Gallery X', 'sel:\'.fp-room[aria-label="Gallery X"]\'',
   "Desk B's new home, updated live",
   'e.setVolDrawer(null),e.setPortalTask(null),e.showOnMap("eastFoyer",null),window.oobsMapPick("days","Both days")'),
  ('Right now', 'sel:\'.map-page .toolbar > .seg:not(.floors) button.on, [data-tour="floorplan"]\'',
   "What's happening in every room right now",
   MAP + ',window.oobsMapPick("days","Now")'),
  # --- Jordan ---
  ("Ava's dashboard", 'target:"up-next"',
   "Ava's day, on her phone", 'e.setPortalTask(null),' + PORTAL),
  ('Changes reach her', 'target:"change-banner"',
   "Changes reach her automatically", 'e.setPortalTask(null),' + PORTAL),
  ('Shift instructions', 'target:"sheet-loc"',
   "Directions, tasks and who to call", PORTAL + ',e.setPortalTask("a22")'),
  ('Ask OOBS', NOTHING,
   "Questions? Ask OOBS",
   'e.setPortalTask(null),' + PORTAL + ',setTimeout(()=>window.oobsOpenChat&&window.oobsOpenChat(),250)'),
]
import json as _json
def _step(t):
    title, where, say, enter = t
    extra = ''
    if 'action:' in where:
        extra = ',next:({data:e})=>{e.state.scenarioDone||e.relocateDeskB(' + _json.dumps(DESK_B_NOTE) + ')}'
    # every step first closes the Ask OOBS chat, so Back from the last step works
    return ('{title:' + _json.dumps(title) + ',' + where + ',say:' + _json.dumps(say) +
            ',enter:({ui:e})=>{window.oobsCloseChat&&window.oobsCloseChat();' + enter + '}' + extra + '}')
NEW_TOUR = 'var Je=[' + ','.join(_step(t) for t in STEPS) + '];function St(){'
_a = html.index('var Je=[{title:"The Organizer dashboard"')
_b = html.index('}}];function St(){', _a) + len('}}];function St(){')
html = html[:_a] + NEW_TOUR + html[_b:]

# --- Hotel X Toronto map -------------------------------------------------------------
# A simple schematic drawn here (not the hotel's floor-plan images). Room IDs are
# Charlie's, so every schedule still works; only names, floors and positions change.
# Cinema, Humber A & B and Library Club Lounge are new rooms.
import json as _j
ROOMS = {
  # Ground floor
  "lobby":     {"name": "Hotel Lobby", "floor": "G", "directions": "Come in through the main hotel entrance off the Lake Shore Blvd driveway. The lobby is straight ahead."},
  "regA":      {"name": "Registration Desk A", "floor": "G", "inside": "Hotel Lobby", "directions": "Left side of the Hotel Lobby, by the Library. Handles surnames A–L."},
  "regB":      {"name": "Registration Desk B", "floor": "G", "inside": "Hotel Lobby", "directions": "Right side of the Hotel Lobby, by Reception. Handles surnames M–Z and walk-ins."},
  "eastFoyer": {"name": "Gallery X", "floor": "G", "directions": "Next to the coat check, just off the lobby."},
  "staff":     {"name": "New Fort Hall", "floor": "G", "directions": "North side of the ground floor, facing Princes' Blvd."},
  "cinema":    {"name": "Cinema", "floor": "G", "directions": "North-west corner of the ground floor, past Gallery X."},
  # Second floor
  "wsA":       {"name": "Riverdale A", "floor": "2", "directions": "Floor 2, north side, past the breakout space."},
  "wsB":       {"name": "Riverdale B", "floor": "2", "directions": "Floor 2, north side, next to Riverdale A."},
  "lounge":    {"name": "Coronation A–C", "floor": "2", "directions": "Floor 2, west wing. Coronation A, B and C open into one room for employer networking."},
  "humber":    {"name": "Humber A & B", "floor": "2", "directions": "Floor 2, west wing, across the breakout space from Coronation. Resume reviews."},
  "ops":       {"name": "Champion's Boardroom", "floor": "2", "directions": "Floor 2, north-east corner. Volunteer HQ: radios and lanyards are issued here."},
  "prefunction": {"name": "Breakout Space", "floor": "2", "directions": "Floor 2, the open area in front of the elevator lobby."},
  "breakRoom": {"name": "Café X", "floor": "2", "directions": "Floor 2, by the coat check. Volunteer breaks: snacks, water and charging."},
  # Third floor
  "ballroom":  {"name": "Victory Ballroom", "floor": "3", "directions": "Floor 3. Turn left from the elevators; the ballroom fills the west side."},
  "reception": {"name": "Princes' Gates Ballroom", "floor": "3", "directions": "Floor 3, north side, past the breakout space."},
  "libraryClub": {"name": "Library Club Lounge", "floor": "3", "directions": "Floor 3, south side, by the terrace. Evening reception."},
  "speakerPrep": {"name": "Bow Tie", "floor": "3", "directions": "Floor 3, beside the Princes' Gates Ballroom. Speaker green room: speakers and staff only."},
  "quiet":     {"name": "Pearl Room", "floor": "3", "directions": "Floor 3, east side. Quiet room: low light, no conversations inside."},
}
def _room(i, r):
    return dict({"id": i}, **r)
_a = html.index('_={lobby:{id:"lobby"')
_b = html.index('}}', html.index('ops:{id:"ops"', _a)) + 2
html = html[:_a] + '_={' + ','.join('%s:%s' % (i, _j.dumps(_room(i, r))) for i, r in ROOMS.items()) + '}' + html[_b:]

def R(i, x, y, w, h, lines, sub=None, ly=None):
    r = {"id": i, "x": x, "y": y, "w": w, "h": h, "lines": lines}
    if sub: r["sub"] = sub
    if ly: r["ly"] = ly
    return r
def F(x, y, w, h, label):
    return {"x": x, "y": y, "w": w, "h": h, "label": label}
PLANS = {
  # the first room listed is the one selected when you switch to that floor
  "G": {"rooms": [R("lobby", 250, 215, 510, 345, ["Hotel Lobby"], sub="Accessibility desk by the doors", ly=255),
                  R("cinema", 50, 50, 180, 150, ["Cinema"]),
                  R("eastFoyer", 250, 50, 200, 150, ["Gallery X"]),
                  R("staff", 620, 50, 330, 150, ["New Fort Hall"]),
                  R("regA", 290, 300, 190, 100, ["Registration", "Desk A"]),   # under 200 wide: no "1 now" tag over the label
                  R("regB", 530, 300, 190, 100, ["Registration", "Desk B"])],
        "fixed": [F(470, 50, 130, 150, "Coat Check"), F(50, 215, 180, 345, "Library"),
                  F(780, 215, 170, 150, "Reception"), F(780, 410, 170, 70, "Elevator Lobby"),
                  F(780, 490, 170, 70, "Washrooms")],
        "doors": [{"x": 300, "y": 580, "tx": 315, "ty": 573, "label": "Main entrance · Lake Shore Blvd driveway"},
                  {"x": 440, "y": 20, "tx": 455, "ty": 40, "label": "Princes' Blvd (north side)"}]},
  "2": {"rooms": [R("wsA", 290, 50, 180, 150, ["Riverdale A"], sub="Workshops"),
                  R("humber", 50, 50, 220, 150, ["Humber A & B"], sub="Resume reviews"),
                  R("wsB", 490, 50, 180, 150, ["Riverdale B"], sub="Workshops"),
                  R("ops", 690, 50, 260, 150, ["Champion's", "Boardroom"], sub="Volunteer HQ"),
                  R("prefunction", 290, 215, 380, 150, ["Breakout Space"]),
                  R("breakRoom", 690, 215, 260, 150, ["Café X"], sub="Volunteer breaks"),
                  R("lounge", 50, 410, 580, 150, ["Coronation A · B · C"], sub="Employer networking")],
        "fixed": [F(50, 215, 220, 70, "Coat Check"), F(50, 295, 220, 70, "Breakout Space"),
                  F(650, 410, 150, 150, "Elevator Lobby"), F(820, 410, 130, 150, "Washrooms")],
        "doors": []},
  "3": {"rooms": [R("ballroom", 50, 50, 220, 510, ["Victory", "Ballroom"], sub="Keynote · lunch"),
                  R("reception", 290, 50, 300, 150, ["Princes' Gates", "Ballroom"], sub="Evening reception"),
                  R("speakerPrep", 610, 50, 160, 150, ["Bow Tie"], sub="Green room"),
                  R("quiet", 790, 50, 160, 150, ["Pearl Room"], sub="Quiet room"),
                  R("libraryClub", 290, 410, 660, 150, ["Library Club Lounge"], sub="Evening reception")],
        "fixed": [F(290, 215, 300, 150, "Breakout Space"), F(610, 215, 160, 150, "Elevator Lobby"),
                  F(790, 215, 160, 150, "Washrooms")],
        "doors": []},
}
_a = html.index('Qt={G:{rooms:[')
_b = html.index('doors:[]}}', _a) + len('doors:[]}}')
html = html[:_a] + 'Qt={' + ','.join('%s:%s' % (k if k == "G" else '"%s"' % k, _j.dumps(v)) for k, v in PLANS.items()) + '}' + html[_b:]
# the planner's own floor-plan sketch had a vertical corridor line on floors 2 and 3
sub('e!=="G"&&x.default.createElement("rect",{x:"258",y:"40",width:"4",height:"520",className:"fp-corridor"})', '!1', 1)
# Resume reviews happen in Humber A & B (the one shift that moves rooms). Charlie's sample
# data picks volunteers partly by room, so let it build the schedule first, then move it:
# everyone keeps exactly the same shifts.
sub("function ut(){let e=Bt.map(", "function ut(){let s=oobsSeed(),r=s.assignments.find(a=>a.id===\"a27\");r&&(r.room=\"humber\");return s}function oobsSeed(){let e=Bt.map(", 1)

sub('"Elevators, stairs, accessible washrooms"', '"Hotel spaces: coat check, lobbies, washrooms"', 1)

# "Who to contact": the table lives in data/content.json and is read while the page runs
# (components and helpers are in the script added after #root below).
sub("I.default.createElement(rt,null),I.default.createElement(Nt,null))",
    "I.default.createElement(rt,null),I.default.createElement(Nt,null),I.default.createElement(window.OobsContacts,null))", 1)
# Volunteer "I need help" form: ask the issue type, confirm "Sent to: <owner>"
sub('onSubmit:E=>{E.preventDefault(),l(n.id,f,e.name),S(!1),u.toast(`${v.name} and Operations can now see your request`)}},'
    'a.default.createElement("label",{htmlFor:"help-note"}',
    'onSubmit:E=>{E.preventDefault();let oS=window.oobsSentTo((document.getElementById("oobs-help-type")||{}).value);'
    'l(n.id,oS?`[${oS.issue}] ${f}`.trim():f,e.name),S(!1),u.toast(oS?oS.text:`${v.name} and Operations can now see your request`)}},'
    'a.default.createElement(window.OobsIssueType,null),a.default.createElement("label",{htmlFor:"help-note"}', 1)
# Hotel map: "View the official floor plan" link next to the floor / day buttons
sub('onClick:()=>m(v)},q)))),x.default.createElement("div",{className:"map-layout"}',
    'onClick:()=>m(v)},q))),x.default.createElement(window.OobsFloorPlanLink,null)),x.default.createElement("div",{className:"map-layout"}', 1)

# Desk B now moves from the Hotel Lobby to Gallery X
sub("Live change: move Desk B to the East Foyer", "Live change: move Desk B to Gallery X", 1)
sub("Registration Desk B has moved to the East Foyer", "Registration Desk B has moved to Gallery X", 1)
sub("now in the East Foyer, ground floor", "now in Gallery X, next to the coat check, just off the lobby", 1)
sub("from the Main Lobby to the East Foyer", "from the Hotel Lobby to Gallery X", 1)
sub("Desk B relocated to East Foyer (lobby crowding)", "Desk B relocated to Gallery X (lobby crowding)", 1)
sub("Moved to the East Foyer; signage needs updating.", "Moved to Gallery X; signage needs updating.", 1)
sub("Main Lobby, east side \\xB7 Ground floor", "Hotel Lobby \\xB7 Ground floor", 1)
sub('"To"),o.default.createElement("strong",null,"East Foyer")', '"To"),o.default.createElement("strong",null,"Gallery X")', 1)
sub("Glass doors at the east end of the lobby \\xB7 Ground floor", "Next to the coat check, just off the lobby \\xB7 Ground floor", 1)
sub("Desk B is now in the East Foyer.", "Desk B is now in Gallery X.", 1)
sub("See East Foyer on the map", "See Gallery X on the map", 1)
sub('"Lobby is crowded at the main doors. Use the glass doors at the east end of the lobby."', _j.dumps(DESK_B_NOTE), 1)
sub("Optional note, e.g. Use the glass doors at the east end", "Optional note, e.g. Gallery X is next to the coat check", 1)

# Old room names in Charlie's shift instructions, issues and notifications
for old, new in [
  ("Enter through the Staff Entrance and", "Enter through the main hotel entrance and"),
  ("move them to the Staff Entrance", "move them to the loading dock"),
  ("orientation in the Volunteer Break Room (Suite 305, 3rd floor)", "orientation in Café X (2nd floor)"),
  ("orientation in the Volunteer Break Room", "orientation in Café X"),
  ("the Volunteer Break Room on Floor 3", "Café X on Floor 2"),
  ("the Operations Command Centre", "Champion's Boardroom (Volunteer HQ)"),
  ("Direct guests to the escalator for the 9:00 AM keynote", "Direct guests to the elevators for the 9:00 AM keynote on Floor 3"),
  ("Stand at the top of the escalator with the floor map", "Stand in the second-floor Breakout Space with the floor map"),
  ("at the top of the escalator on Floor 2", "in the second-floor Breakout Space"),
  ("Accessibility Desk (west side of the Main Lobby)", "Accessibility Desk (in the Hotel Lobby, by the main doors)"),
  ("the Speaker Preparation Room (Suite 302)", "the Bow Tie green room (Floor 3)"),
  ("main ballroom doors on Floor 2", "Victory Ballroom doors on Floor 3"),
  ("keynote on Floor 2", "keynote on Floor 3"),
  ("Grand Ballroom", "Victory Ballroom"),
  ("Workshop Room A (Room 204)", "Riverdale A"), ("Workshop Room B (Room 206)", "Riverdale B"),
  ("Workshop Rooms A and B and the Networking Lounge", "Riverdale A and B and the Coronation rooms"),
  ("the Employer Networking Lounge", "Coronation A–C"),
  ("the Networking Lounge", "the Coronation rooms"),
  ("the Quiet Room (Suite 308) on Floor 3", "the Pearl Room (quiet room) on Floor 3"),
  ("the Quiet Room (Suite 308)", "the Pearl Room (quiet room)"),
  ("Deliver the Quiet Room supply kit to Suite 308", "Deliver the quiet room supply kit to the Pearl Room"),
  ("from the elevators to Suite 308", "from the elevators to the Pearl Room"),
  ("the coat check and the Quiet Room on Floor 3", "the coat check and the Pearl Room (quiet room) on Floor 3"),
  ("Quiet Room", "Pearl Room"),
  ("in the Reception Area", "in the Princes' Gates Ballroom"),
  ("at the Reception Area welcome table", "at the Princes' Gates Ballroom welcome table"),
  ("Main Lobby", "Hotel Lobby"),
  ("East Foyer", "Gallery X"),
]:
    sub(old, new, None)

# --- Own browser storage, so the full version's saved data never leaks in ------
sub('"start-proud-volunteeros-v1"', '"oobs-planner-demo-v1"', 1)
sub('"start-proud-volunteeros-ui-v1"', '"oobs-planner-demo-ui-v1"', 1)

# --- Force the light theme ---------------------------------------------------------
sub("<!doctype html><html>", '<!doctype html><html data-theme="light">', 1)

# --- Helper: tag the current view, and always open the volunteer view as Ava ----
HELPER = """<script>/* Team B demo helper */(function(){var d=document.documentElement;
function v(){d.setAttribute('data-view',(location.hash||'#dashboard').slice(1)||'dashboard')}
v();addEventListener('hashchange',v);
/* Shared text from ../data/content.json (Who to contact table, official floor plan link) */
fetch('../data/content.json',{cache:'no-cache'}).then(function(r){return r.json()}).then(function(j){window.OOBS_DATA=j;dispatchEvent(new Event('oobs-data'));}).catch(function(){});
/* Presentation Demo: press the hotel map's own floor / day buttons (they are internal to Charlie's code) */
window.oobsMapPick=function(group,label){setTimeout(function(){
var seg=document.querySelector('.map-page .toolbar > .seg'+(group==='floors'?'.floors':':not(.floors)'));if(!seg)return;
var b=[].slice.call(seg.querySelectorAll('button')).filter(function(x){return group==='floors'?x.textContent.indexOf(label)>-1:x.textContent.trim()===label;})[0];
if(b&&!b.classList.contains('on'))b.click();},150);};
/* Presentation Demo: clicker keys. Right arrow, Page Down, Space = Next; Left arrow, Page Up = Back. */
function typing(a){if(!a)return false;var t=a.tagName;return a.isContentEditable||t==='TEXTAREA'||t==='SELECT'||(t==='INPUT'&&!/^(button|submit|reset|checkbox|radio|range|color|file)$/i.test(a.type));}
function key(e){return e.key===' '||e.key==='Spacebar'?'next':{ArrowRight:'next',PageDown:'next',ArrowLeft:'back',PageUp:'back'}[e.key];}
addEventListener('keydown',function(e){var tour=document.querySelector('.tour'),k=key(e);
if(!tour||!k||e.altKey||e.ctrlKey||e.metaKey||typing(document.activeElement))return;
e.preventDefault();e.stopPropagation();if(e.repeat)return;
var nav=tour.querySelectorAll('.tour-nav .btn'),b=k==='next'?nav[nav.length-1]:nav[0];if(b&&!b.disabled)b.click();},true);
/* stop Space also "pressing" whichever button has focus (that would skip a step) */
addEventListener('keyup',function(e){if(document.querySelector('.tour')&&key(e)==='next'&&!typing(document.activeElement))e.preventDefault();},true);
try{var k='oobs-planner-demo-ui-v1',u=JSON.parse(localStorage.getItem(k)||'{}');u.portalVol='v01';localStorage.setItem(k,JSON.stringify(u))}catch(e){}})();</script>
"""
sub("<title>Start Proud VolunteerOS (Copy)</title>",
    "<title>Start Proud VolunteerOS (Copy)</title>\n" + HELPER, 1)

DEMO_CSS = """<style>/* ===== Team B 2-minute demo: hides parts of Charlie's planner. Full version: /planner/full/ ===== */
/* Presentation Demo: Charlie's guided tour (Team B's steps). Start it from the dashboard. */
html[data-view="my-schedule"] .demo-top { display: none !important; }
.oobs-ask-fab.tour-glow { position: fixed !important; z-index: 45 !important; }
/* Tour glow on a floor-plan room: outline doesn't draw on SVG, so glow the room's border */
.fp-room.tour-glow rect { stroke: #2BC9BF !important; stroke-width: 7px !important; }
/* When the tour opens Ask OOBS, keep the tour card off the chat's text box */
@media (min-width: 861px) { html:has(.oobs-chat:not([hidden])) .tour { right: auto; left: max(20px, env(safe-area-inset-left, 0px)); } }
@media (max-width: 860px) { html:has(.oobs-chat:not([hidden])) .tour { bottom: auto; top: max(12px, env(safe-area-inset-top, 0px)); } }
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
.content > .oobs-contacts { grid-column: 1 / -1; order: 5; }
.dash > .grid-2 { grid-column: 1 / -1; order: 6; grid-template-columns: minmax(0, 1fr); }
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

/* "Who to contact" card */
.oobs-contacts-wrap { overflow-x: auto; }
.oobs-contacts-tbl { width: 100%; border-collapse: collapse; font-size: 13.5px; }
.oobs-contacts-tbl th { text-align: left; font-size: 11.5px; letter-spacing: .05em; text-transform: uppercase; color: var(--muted); padding: 0 10px 8px; border-bottom: 1px solid var(--border); }
.oobs-contacts-tbl td { padding: 10px; border-bottom: 1px solid var(--border); vertical-align: top; }
.oobs-contacts-tbl td strong { display: block; font-weight: 650; }
.oobs-contacts-tbl td span { color: var(--muted); }
.oobs-contacts-tbl td em { display: block; font-style: normal; color: var(--crit); font-weight: 650; }
.oobs-contacts-tbl td.issue { font-weight: 600; }
.oobs-contacts-tbl tr.urgent td { background: var(--crit-soft); }
.oobs-contacts-tbl tr:last-child td { border-bottom: 0; }
@media (max-width: 560px) {
  .oobs-contacts-tbl thead { display: none; }
  .oobs-contacts-tbl, .oobs-contacts-tbl tbody, .oobs-contacts-tbl tr, .oobs-contacts-tbl td { display: block; width: 100%; }
  .oobs-contacts-tbl tr { border-bottom: 1px solid var(--border); padding: 8px 0; }
  .oobs-contacts-tbl tr.urgent { background: var(--crit-soft); border-radius: 10px; padding: 8px; }
  .oobs-contacts-tbl td { border: 0; padding: 2px 0; background: none !important; }
  .oobs-contacts-tbl td:nth-child(2)::before { content: "First: "; color: var(--muted); }
  .oobs-contacts-tbl td:nth-child(3)::before { content: "Then: "; color: var(--muted); }
  .oobs-contacts-tbl td:nth-child(n+2) strong, .oobs-contacts-tbl td:nth-child(n+2) span { display: inline; }
  .oobs-contacts-tbl td:nth-child(n+2) span::before { content: " · "; }
}
/* "I need help" form: issue type */
.oobs-issue-type { display: flex; flex-direction: column; gap: 6px; font-weight: 600; margin-bottom: 4px; }
.oobs-issue-type select { font: inherit; font-weight: 500; padding: 9px 10px; border-radius: 9px; border: 1px solid var(--border-2); background: var(--surface); color: var(--fg); }
/* Hotel map: official floor plan link */
.map-page .toolbar { flex-wrap: wrap; }
.oobs-official { margin-left: auto; text-decoration: none; }
</style>
<div id="root"></div>
<script>/* Team B: small React components used inside Charlie's planner */(function(){
function useData(){var R=window.React,s=R.useState(window.OOBS_DATA||null);
R.useEffect(function(){function f(){s[1](window.OOBS_DATA)}addEventListener('oobs-data',f);f();return function(){removeEventListener('oobs-data',f)}},[]);return s[0];}
function who(p){return p.role+(p.name?' ('+p.name+')':'')+(p.note?' '+p.note:'');}
window.oobsSentTo=function(id){var c=window.OOBS_DATA&&window.OOBS_DATA.contacts;if(!c||!id)return null;
var t=c.types.filter(function(x){return x.id===id})[0];if(!t)return null;
return {issue:t.issue,text:(c.sentTo||'Sent to')+': '+who(t.owner)+(t.urgent&&c.urgentNote?'. '+c.urgentNote:'')};};
window.OobsContacts=function(){var R=window.React,h=R.createElement,d=useData(),c=d&&d.contacts;if(!c)return null;
var col=c.columns||['Issue type','First contact','Escalates to'];
function cell(p){return h('td',null,h('strong',null,p.role),p.name?h('span',null,p.name):null,p.note?h('em',null,p.note):null);}
return h('section',{className:'card oobs-contacts','data-tour':'contacts'},
 h('header',{className:'card-h'},h('div',null,h('h3',null,c.title),h('p',{className:'sub'},c.intro))),
 h('div',{className:'oobs-contacts-wrap'},h('table',{className:'oobs-contacts-tbl'},
  h('thead',null,h('tr',null,col.map(function(x){return h('th',{key:x},x)}))),
  h('tbody',null,c.types.map(function(t){return h('tr',{key:t.id,className:t.urgent?'urgent':''},
   h('td',{className:'issue'},t.issue),cell(t.owner),cell(t.escalatesTo));})))));};
window.OobsIssueType=function(){var R=window.React,h=R.createElement,d=useData(),c=d&&d.contacts;if(!c)return null;
return h('label',{className:'oobs-issue-type',htmlFor:'oobs-help-type'},h('span',null,c.question),
 h('select',{id:'oobs-help-type',required:true,defaultValue:''},h('option',{value:'',disabled:true},c.choose),
  c.types.map(function(t){return h('option',{key:t.id,value:t.id},t.issue)})));};
window.OobsFloorPlanLink=function(){var R=window.React,h=R.createElement,d=useData(),u=d&&d.links&&d.links.officialFloorPlan;if(!u)return null;
return h('a',{className:'btn sm oobs-official',href:u,target:'_blank',rel:'noopener'},(d.ui&&d.ui.officialFloorPlan)||'View the official floor plan',' ↗');};
})();</script>
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
window.oobsOpenChat=open;window.oobsCloseChat=function(){box.hidden=true;};
fab.addEventListener('click',open);close.addEventListener('click',shut);
box.querySelector('.oobs-chat-backdrop').addEventListener('click',shut);
addEventListener('keydown',function(e){if(e.key==='Escape')shut();});
addEventListener('message',function(e){if(e.origin===location.origin&&e.data&&e.data.oobs==='close-chat')shut();});
addEventListener('hashchange',function(){box.hidden=true;});})();</script>""".replace("CHAT_URL", CHAT_URL)
sub('<div id="root"></div>', DEMO_CSS, 1)

OUT.write_text(html, encoding="utf-8")
print(f"Wrote {OUT.relative_to(ROOT)}")
