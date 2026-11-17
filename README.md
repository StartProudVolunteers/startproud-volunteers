# OOBS Volunteer Assistant (concept demo)

A mobile-first static website for volunteers at **Out on Bay Street** (Hotel X Toronto).
No backend, no build step: plain HTML, CSS and JavaScript.

> Concept demo by Team B, not an official Start Proud tool. All names, phone numbers,
> rooms and times are invented sample data.

## What's in it

| File | What it is |
|---|---|
| `index.html` | Home page: event header, **Catch me up**, list of stations |
| `station.html?id=…` | One template for all 5 stations (`registration`, `career-fair`, `victory-ballroom`, `green-room`, `volunteer-hq`) |
| `data/content.json` | **Every word in the app.** Edit this, not the code. |
| `assets/app.js` | Renders the JSON, runs the keyword-matching chat |
| `assets/style.css` | Styles (light + dark mode) |
| `tools/make_qr_cards.py` | Builds `qr-cards.pdf`, one QR card per station page |
| `qr-cards.pdf` | Printable cards (US Letter, 6 per page, dashed cut lines) |

## Editing the text (for teammates)

Open `data/content.json` on GitHub, click the ✏️ pencil, edit, then **Commit changes**.
The live site updates in about a minute.

- **`catchUp.lines`**: the 5 lines in "Catch me up". Change `catchUp.updated` too.
- **`stations[].tasks`**: the "What to do here" list.
- **`stations[].lead`**: lead's name, pronouns and phone (the Message button opens a text to it).
- **`stations[].answers`**: the station's Ask OOBS answers.
  - `question`: shown as a tap button when `"suggest": true`.
  - `keywords`: lowercase words or short phrases. If a typed question contains one, the answer can match.
    The answer with the most keyword hits wins; station answers beat general ones on a tie.
  - `answer`: what the bot says.
- **`globalAnswers`**: answers every station can give (washrooms, Wi-Fi, lunch, first aid, …).
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

The committed `qr-cards.pdf` points at `https://jordanpcho.github.io/Comms-Final-Project/`.
If your live URL is different (check step 3 above), rebuild it:

```bash
pip install qrcode reportlab pillow
python3 tools/make_qr_cards.py https://<username>.github.io/<repo>/
```

Print at **100% / Actual size** (not "Fit to page") on card stock, cut on the dashed lines.
Scan one with a phone before printing a batch.
