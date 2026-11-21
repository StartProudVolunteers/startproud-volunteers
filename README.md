# OOBS Volunteer Assistant (concept demo)

A mobile-first static website for volunteers at **Out on Bay Street** (Hotel X Toronto).
No backend, no build step: plain HTML, CSS and JavaScript.

> Concept demo by Team B, not an official Start Proud tool. All names, phone numbers,
> rooms and times are invented sample data.

## What's in it

| File | What it is |
|---|---|
| `index.html` | Home: header, **Ask anything** box, **⚡ Catch me up**, and three big buttons: *Where do I go?*, *Call my lead*, *An attendee asked me…* |
| `stations.html` | The station list (linked from "Stations" on the home page) |
| `station.html?id=…` | One template for all 5 stations (`registration`, `career-fair`, `victory-ballroom`, `green-room`, `volunteer-hq`) |
| `my-day.html?role=…` | **My day**: pick a role, see a personal timeline and a stacked-floor venue map with your current room highlighted |
| `planner/` | Charlie's planner, simplified for a 2-minute demo (built by `tools/make_planner.py`) |
| `planner/full/` | Charlie's original planner, unchanged, for the appendix |
| `data/content.json` | **Every word in the app.** Edit this, not the code. |
| `assets/app.js` | Renders the JSON, runs the keyword-matching chat |
| `assets/style.css` | Styles (light + dark mode) |
| `tools/make_qr_cards.py` | Builds `qr-cards.pdf`, one QR card per station page |
| `qr-cards.pdf` | Printable cards (US Letter, 6 per page, dashed cut lines) |

## Editing the text (for teammates)

Open `data/content.json` on GitHub, click the ✏️ pencil, edit, then **Commit changes**.
The live site updates in about a minute.

- **Keep answers short**: two short lines on a phone, about 65 characters. Longer answers wrap to a third line.
- **`ui.header`**, **`ui.home`**: the home header and the big-button labels.
- **"My station"**: the phone remembers the last station page a volunteer opened (or the lead they
  picked). "Call my lead" and the home Ask box use it. Before that, "Call my lead" shows a list of leads.
- **`catchUp.lines`**: the 5 lines in "Catch me up". Change `catchUp.updated` too.
- **`stations[].tasks`**: the "What to do here" list.
- **`stations[].lead`**: lead's name, pronouns and phone (the Message button opens a text to it).
- **`stations[].answers`**: the station's Ask OOBS answers.
  - `question`: shown as a tap button when `"suggest": true` (max 3 per station).
  - `keywords`: lowercase words or short phrases. If a typed question contains one, the answer can match.
    The answer with the most keyword hits wins; station answers beat general ones on a tie.
  - `answer`: what the bot says.
- **`globalAnswers`**: answers every station can give (Start Proud, code of conduct, sponsors,
  washrooms, Wi-Fi, lunch, …). Ones with `"suggest": true` appear under "An attendee asked me…" on the home page.
- **Safety answers** (`"escalate": true`: first aid, harassment, feeling unsafe) always win over
  other matches. They show a red "Find the Volunteer Lead at HQ now" card with a call button.
  The name, location and phone number come from **`escalation`**.
- **`links.mapUrl`**: where "See it on the map" goes. It's a placeholder for now. Swap in the
  real map link; `{station}` is replaced with the station id (e.g. `registration`). To send one
  station somewhere else, add `"mapUrl": "https://…"` to that station.
- **`myDay.roles`**: one entry per role (Registration, Career Fair, Ballroom, Green Room, Floater).
  Each `slots` item has 24-hour `start`/`end` (`"09:45"`), a `title`, an optional `note`, and a `room`
  that must match a room `id` under `myDay.floors`. `station` links the role to its station page.
- **`myDay.floors`**: the venue map, top floor first. Each room has a full `name` (timeline),
  a `short` label (map) and a `size` (relative width on the map). The map is a simplified sketch
  drawn by the app; it isn't based on the hotel's real floor plans.
- **`myDay.demoTime`**: the time My day pretends it is outside `eventHours`, so the demo always
  shows something. Volunteers can also change the clock on the page.
- **`ui.fallback`**: the "I'm not sure, message your lead" reply when nothing matches.

Rules of JSON: keep the double quotes, put a comma between items but **not** after the last
one in a list. If the page shows "Couldn't load data/content.json", paste the file into
https://jsonlint.com to find the typo.

To add a station, copy a whole `{ "id": … }` block in `stations`, give it a new `id`, and
re-run the QR script. No HTML changes needed.

## Run it locally

The page loads the JSON with `fetch`, which browsers block on `file://`. Use a tiny server:

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

## Deploy to GitHub Pages

1. **Get the files onto `main`.** Open a pull request from the working branch into `main`
   and merge it (or, if the repo has no `main` yet, create it from this branch on GitHub:
   *Code → branch dropdown → View all branches → New branch*, source = this branch).
2. **Turn on Pages.** Repo **Settings → Pages**. Under *Build and deployment*:
   *Source* = **Deploy from a branch**, *Branch* = **main**, folder = **/ (root)** → **Save**.
3. **Wait ~1 minute**, refresh the Settings → Pages screen. It shows
   *"Your site is live at https://&lt;username&gt;.github.io/&lt;repo&gt;/"*.
   Progress is visible under the **Actions** tab ("pages build and deployment").
4. **Check on a phone.** Open the URL, tap a station, try Ask OOBS and Catch me up.
5. **Private repo?** Pages on a private repo needs a paid GitHub plan. On a free account,
   make the repo public (Settings → General → Danger Zone → Change visibility).

The empty `.nojekyll` file tells GitHub to serve the files as-is.

## Regenerate the QR cards

The committed `qr-cards.pdf` points at `https://jordanpcho.github.io/startproud-volunteers-/`.
If your live URL is different (check step 3 above), rebuild it:

```bash
pip install qrcode reportlab pillow
python3 tools/make_qr_cards.py https://<username>.github.io/<repo>/
```

Print at **100% / Actual size** (not "Fit to page") on card stock, cut on the dashed lines.
Scan one with a phone before printing a batch.

## Charlie's planner

`planner/full/index.html` is Charlie's file exactly as he sent it. **Don't edit
`planner/index.html` by hand**: it's generated from the original by

```bash
python3 tools/make_planner.py
```

The demo has four tabs: **Organizer dashboard**, **Volunteer Directory** (as Charlie
built it, minus the "Joined" dates that overlapped long names), **Volunteer dashboard** and **Hotel map**.
The event clock is hidden, so the demo always shows Fri, Apr 30, 10:30 AM.

The dashboard is where organizers make changes, top to bottom:
1. Three numbers. "Need attention" = open problems + tasks flagged as needing help.
2. **Live change**: one button moves Registration Desk B from the Hotel Lobby to Gallery X
   (next to the coat check, just off the lobby) and tells
   every volunteer working there.
3. **Problems reported**: one tap to Resolve, or type a new problem and tap Report.
4. **Fill open shifts**: one tap ("Add Avery") puts a free volunteer on a short-staffed shift.
5. **Recent changes**: every edit above shows up here.

### Hotel X map

The planner's hotel map is a simple schematic of Hotel X Toronto drawn by
`tools/make_planner.py` (`ROOMS` and `PLANS`). It is not the hotel's floor-plan
images and not to scale. Charlie's room IDs are kept, so every shift still works;
only names, floors and positions changed:

| Floor | Rooms |
|---|---|
| Ground | Hotel Lobby (Registration Desks A and B, accessibility desk), Gallery X, New Fort Hall, Cinema; Coat Check, Library, Reception, Elevator Lobby, Washrooms |
| Second | Riverdale A and B (workshops), Coronation A–C (employer networking), Humber A & B (resume reviews), Champion's Boardroom (Volunteer HQ), Breakout Space, Café X (volunteer breaks); Coat Check, Elevator Lobby, Washrooms |
| Third | Victory Ballroom (keynote, lunch), Princes' Gates Ballroom and Library Club Lounge (evening reception), Bow Tie (speaker green room), Pearl Room (quiet room); Breakout Space, Elevator Lobby, Washrooms |

"View the official floor plan" on the map uses `links.officialFloorPlan` in
`data/content.json`. **It points at hotelxtoronto.com for now: paste the hotel's PDF link there.**

### Urgent request

On the Organizer dashboard, **⚠ Urgent request** opens a short form: room, how many
volunteers and a message. It suggests volunteers who are not on a shift right now,
nearest floor first (based on where their last or next shift is), and ticks the first
few. **Send by text and email** logs each delivery under "Simulated: no real texts or
emails are sent". Nothing leaves the browser.

Each recipient's Volunteer dashboard shows a red urgent banner and a phone-style text
with **On my way** and **Can't make it**. The organizer's card counts replies live
("2 of 2 on the way"). To show this in a demo, use **Open their phone** next to a name,
reply, then **← Organizer view**. Ava is on shift at 10:30, so she isn't suggested.
Reset demo data (or starting the tour) clears the request.

### Who to contact

`contacts` in `data/content.json` is one table (issue type, first contact, who it
escalates to) used in three places, read live, so no rebuild is needed after editing:

- the **Who to contact** card on the Organizer dashboard
- the volunteer **I need help** form (open a shift on the Volunteer dashboard): it asks
  "What kind of problem is it?" and confirms **Sent to: <owner>**
- the chatbot: one "Who do I contact about ...?" answer per row. Safety or medical
  shows the red "find the Volunteer Lead" card.

Role titles are real job titles; every name is invented.

### Presentation Demo

Click **Presentation Demo** (top right of the Organizer dashboard, or in the sidebar).
It's Charlie's guided tour with our 12-step script. Each step opens the right page,
makes the part being discussed glow and shows a short caption; the presenters do the
talking. It resets the demo data when it starts, so every run begins fresh.

**Clicker / keyboard:** Right arrow, Page Down or Space = next step; Left arrow or
Page Up = back. These keys are ignored while someone is typing in a text box, and
keep working after you tap inside the Ask OOBS chat.

| # | Presenter | Step | Caption | What happens |
|---|---|---|---|---|
| 1 | Charlie | Organizer dashboard | The whole event on one screen | Title and three numbers glow |
| 2 | Charlie | Move Desk B | One tap moves Desk B and tells 4 volunteers | The Next button reads **Move Desk B now** and really moves it |
| 3 | Charlie | Urgent request | Need people now? Text them in one tap | The Urgent request form opens |
| 4 | Charlie | Ava's itinerary | Ava's itinerary, set by organizers | Volunteer Directory with Ava's profile open |
| 5 | Charlie | Volunteer Directory | Everyone in one place: search, filter, update | Ava's profile closes; the search and filter bar glows (about 10 seconds, nothing to click) |
| 6 | Pransh | Every room, every floor | Every room, on every floor | Hotel map, Ground Floor, nothing highlighted |
| 7 | Pransh | Gallery X | Desk B's new home, updated live | Gallery X glows |
| 8 | Pransh | Right now | What's happening in every room right now | Map switches to its "Now" filter |
| 9 | Jordan | Ava's dashboard | Ava's day, on her phone | Up next glows |
| 10 | Jordan | Changes reach her | Changes reach her automatically | The "Desk B has moved" note glows |
| 11 | Jordan | Shift instructions | Directions, tasks and who to call | Her shift details open |
| 12 | Jordan | Ask OOBS | Questions? Ask OOBS | The chat opens with "Try asking: Who do I tell about a sponsor complaint?"; the tour card moves aside so the text box stays clear |

To change a step, edit `STEPS` in `tools/make_planner.py` and re-run it.

The script changes a few text strings (Hotel X Toronto, Ava Papanikolaou, tab names),
makes the dashboard page render the Desk B card too, replaces the tour steps, adds a floating
"💬 Ask OOBS" button to the volunteer dashboard, and
adds a stylesheet that hides everything not needed for the demo. If Charlie sends a
new version, copy it over `planner/full/index.html` and re-run the script. It
stops with an error if any text it expects has changed.

- "💬 Ask OOBS" (volunteer schedule only) opens our chat in a panel over the planner:
  `chat.html?id=registration&embed=1`, the same answers as `data/content.json`. Close it
  with ×, Escape or a tap outside; the conversation stays until the page reloads.
- The chat's "My schedule" button goes back to `planner/#my-schedule` (`links.plannerSchedule`).
- The demo version saves its data under its own browser-storage keys, so playing with
  `/planner/full/` doesn't change the demo, and it always opens the volunteer view as Ava.
