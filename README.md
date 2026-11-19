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

The demo has three tabs: **Organizer dashboard**, **Volunteer schedule** and **Hotel map**.
The event clock is hidden, so the demo always shows Fri, Apr 30, 10:30 AM.

The dashboard is where organizers make changes, top to bottom:
1. Three numbers. "Need attention" = open problems + tasks flagged as needing help.
2. **Make a live change**: move Registration Desk B to the East Foyer. Then open
   Volunteer schedule to show Ava's shifts updating.
3. **Problems reported**: one tap to Resolve, or type a new problem and tap Report.
4. **Fill open shifts**: one tap ("Add Avery") puts a free volunteer on a short-staffed shift.
5. **Recent changes**: every edit above shows up here.

Use "Reset demo data" in the sidebar to undo everything before the next run-through.

The script changes a few text strings (Hotel X Toronto, Ava Papanikolaou, tab names),
makes the dashboard page render the Desk B card too, adds a floating
"💬 Ask OOBS" button to the volunteer schedule, and
adds a stylesheet that hides everything not needed for the demo. If Charlie sends a
new version, copy it over `planner/full/index.html` and re-run the script. It
stops with an error if any text it expects has changed.

- "💬 Ask OOBS" (volunteer schedule only) opens our chat in a panel over the planner:
  `chat.html?id=registration&embed=1`, the same answers as `data/content.json`. Close it
  with ×, Escape or a tap outside; the conversation stays until the page reloads.
- The chat's "My schedule" button goes back to `planner/#my-schedule` (`links.plannerSchedule`).
- The demo version saves its data under its own browser-storage keys, so playing with
  `/planner/full/` doesn't change the demo, and it always opens the volunteer view as Ava.
