"""Generate a printable PDF of QR code cards, one per station page.

Usage:
    pip install qrcode reportlab pillow
    python3 tools/make_qr_cards.py https://YOUR-USERNAME.github.io/YOUR-REPO/

Station names and floors come from data/content.json, so re-run this after
adding or renaming a station. Output: qr-cards.pdf (US Letter, 6 cards/page).
"""
import json
import sys
from pathlib import Path

import qrcode
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BASE = "https://jordanpcho.github.io/Comms-Final-Project/"
INK, ACCENT, MUTED = HexColor("#1b1440"), HexColor("#6b3fd4"), HexColor("#5c5775")
PRIDE = ["#e40303", "#ff8c00", "#ffed00", "#008026", "#004dff", "#750787"]


def qr_image(url):
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=2, box_size=12)
    q.add_data(url)
    q.make(fit=True)
    return ImageReader(q.make_image(fill_color="#1b1440", back_color="white").get_image())


def fit(c, text, font, size, max_w, min_size=9):
    while size > min_size and c.stringWidth(text, font, size) > max_w:
        size -= 0.5
    return size


def draw_card(c, x, y, w, h, title, subtitle, url, footer, event):
    # dashed cut line
    c.setStrokeColor(HexColor("#bbbbbb"))
    c.setDash(3, 3)
    c.setLineWidth(0.5)
    c.rect(x, y, w, h)
    c.setDash()
    # pride stripe
    sw = w / len(PRIDE)
    for i, col in enumerate(PRIDE):
        c.setFillColor(HexColor(col))
        c.rect(x + i * sw, y + h - 8, sw, 8, stroke=0, fill=1)

    cx = x + w / 2
    c.setFillColor(MUTED)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(cx, y + h - 26, event.upper() + "  ·  VOLUNTEER ASSISTANT")
    c.setFillColor(INK)
    size = fit(c, title, "Helvetica-Bold", 20, w - 30)
    c.setFont("Helvetica-Bold", size)
    c.drawCentredString(cx, y + h - 50, title)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 10.5)
    c.drawCentredString(cx, y + h - 66, subtitle)

    qs = 1.45 * inch
    c.drawImage(qr_image(url), cx - qs / 2, y + 44, qs, qs)

    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 10.5)
    c.drawCentredString(cx, y + 34, "Scan for your tasks, lead & Ask OOBS")
    c.setFillColor(MUTED)
    c.setFont("Helvetica-Oblique", 6.8)
    c.drawCentredString(cx, y + 14, footer)


def main():
    base = (sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASE).rstrip("/") + "/"
    data = json.loads((ROOT / "data" / "content.json").read_text(encoding="utf-8"))
    cards = [(s["name"], s["floor"], f"{base}station.html?id={s['id']}") for s in data["stations"]]
    cards.append(("All stations", "Not sure where you are? Start here.", base))

    out = ROOT / "qr-cards.pdf"
    c = canvas.Canvas(str(out), pagesize=letter)
    c.setTitle(f"{data['event']['name']} — volunteer station QR cards")
    pw, ph = letter
    cols, rows = 2, 3
    margin = 0.5 * inch
    cw, ch = (pw - 2 * margin) / cols, (ph - 2 * margin) / rows
    for i, (title, sub, url) in enumerate(cards):
        if i and i % (cols * rows) == 0:
            c.showPage()
        slot = i % (cols * rows)
        col, row = slot % cols, slot // cols
        x = margin + col * cw
        y = ph - margin - (row + 1) * ch
        draw_card(c, x + 6, y + 6, cw - 12, ch - 12, title, sub, url,
                  data["ui"]["footer"], data["event"]["name"])
    c.save()
    print(f"Wrote {out} ({len(cards)} cards) for {base}")


if __name__ == "__main__":
    main()
