"""
Invoice Generator - Template: TOIT BREWPUB
===========================================
Based on: example_templates/v3/toit.jpg

Layout:
  - "TOIT" (bold large, centered)
  - "Brewpub" (centered)
  - Address block (centered)
  - GSTIN (centered)
  - CIN (centered)
  - Separator
  - Table / Bill No / Date / Time / Covers (2-col block)
  - Separator
  - ITEM | QTY | RATE | AMOUNT (bold table header)
  - Separator
  - Item rows
  - Separator
  - Net Amount (right)
  - SC / CGST / SGST rows (right)
  - Separator (thick)
  - Total ₹ (bold, right)
  - Separator (thick)
  - "Service charges are at our discretion" note
  - Thank you message (centered)

Output: toit_brewpub_invoice.png
"""

from PIL import Image, ImageDraw, ImageFont

# ─────────────────────────────────────────────
#  VARIABLES  — edit these before running
# ─────────────────────────────────────────────

RESTAURANT_NAME = "TOIT"
SUB_BRAND       = "Brewpub"
ADDRESS_LINE1   = "298, 100 ft Road, Indiranagar,"
ADDRESS_LINE2   = "Bengaluru - 560038"
PHONE           = "Tel: 80 6571 6161"
GSTIN           = "GSTIN: 29AABCT2454D1ZB"
CIN             = "CIN: U55101KA2011PTC100003"

TABLE_NO   = "C12"
BILL_NO    = "6021"
DATE       = "31/07/2026"
TIME       = "09:15 PM"
COVERS     = "3"
CASHIER    = "Server"

ITEMS = [
    ("Bira White (500 ml)",      2, 390.00),
    ("Garlic Bread",             1, 190.00),
    ("Firecracker Chicken Wings",1, 470.00),
    ("Toit Signature Pizza",     1, 530.00),
]

SC_RATE   = 10.0   # Service Charge %
CGST_RATE = 2.5
SGST_RATE = 2.5

THANK_YOU   = "Thank You! Please Visit Again."
OUTPUT_FILE = "toit_brewpub_invoice.png"

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def load_fonts(base=26):
    rp = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
    bp = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
    try:
        fr   = ImageFont.truetype(rp, base)
        fb   = ImageFont.truetype(bp, base)
        fblg = ImageFont.truetype(bp, base + 8)
        fbhd = ImageFont.truetype(bp, base + 4)
    except OSError:
        fr = fb = fblg = fbhd = ImageFont.load_default()
    return fr, fb, fblg, fbhd


def dt(draw, x, y, text, font, fill=(20, 20, 20)):
    draw.text((x, y), text, font=font, fill=fill)


def msr(text, font):
    b = font.getbbox(text)
    return b[2] - b[0]


def cx(text, font, W):
    return (W - msr(text, font)) // 2


def sep(draw, y, W, M, thick=False):
    draw.line([(M, y), (W-M, y)], fill=(20, 20, 20), width=2 if thick else 1)
    return y + (4 if thick else 2)


def generate_invoice():
    net_amount = sum(q * r for _, q, r in ITEMS)
    sc_amt     = round(net_amount * SC_RATE / 100, 2)
    cgst_base  = net_amount + sc_amt
    cgst_amt   = round(cgst_base * CGST_RATE / 100, 2)
    sgst_amt   = round(cgst_base * SGST_RATE / 100, 2)
    total      = round(net_amount + sc_amt + cgst_amt + sgst_amt, 2)

    W, M, P = 760, 28, 10
    lh, lhb = 36, 44
    fr, fb, fblg, fbhd = load_fonts(26)

    H = 850 + len(ITEMS) * lh
    img  = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    y    = 28

    # header
    dt(draw, cx(RESTAURANT_NAME, fblg, W), y, RESTAURANT_NAME, fblg); y += lhb
    dt(draw, cx(SUB_BRAND, fb, W), y, SUB_BRAND, fb); y += lh
    for ln in [ADDRESS_LINE1, ADDRESS_LINE2, PHONE, GSTIN, CIN]:
        dt(draw, cx(ln, fr, W), y, ln, fr); y += lh
    y += P; y = sep(draw, y, W, M) + P

    # bill info
    dt(draw, M, y, f"Table: {TABLE_NO}", fr)
    dt(draw, W-M-msr(f"Bill No.: {BILL_NO}", fr), y, f"Bill No.: {BILL_NO}", fr); y += lh
    dt(draw, M, y, f"Date: {DATE}", fr)
    dt(draw, W-M-msr(f"Time: {TIME}", fr), y, f"Time: {TIME}", fr); y += lh
    dt(draw, M, y, f"Covers: {COVERS}", fr)
    dt(draw, W-M-msr(f"Cashier: {CASHIER}", fr), y, f"Cashier: {CASHIER}", fr); y += lh + P
    y = sep(draw, y, W, M) + P

    # table header (bold)
    ci = M; cq = W-M-290; cr = W-M-165; ca = W-M-10
    dt(draw, ci, y, "ITEM", fb)
    dt(draw, cq - msr("QTY", fb)//2, y, "QTY", fb)
    dt(draw, cr - msr("RATE", fb),   y, "RATE", fb)
    dt(draw, ca - msr("AMOUNT", fb), y, "AMOUNT", fb); y += lh
    y = sep(draw, y, W, M) + P

    # items
    for name, qty, rate in ITEMS:
        amount = qty * rate
        qs = str(qty); rs = f"{rate:.2f}"; as_ = f"{amount:.2f}"
        dt(draw, ci, y, name, fr)
        dt(draw, cq - msr(qs,  fr)//2, y, qs,  fr)
        dt(draw, cr - msr(rs,  fr),    y, rs,  fr)
        dt(draw, ca - msr(as_, fr),    y, as_, fr); y += lh

    y += P; y = sep(draw, y, W, M) + P

    # totals
    def rrow(lbl, val, fnt=fr):
        nonlocal y
        dt(draw, cr - msr(lbl, fnt), y, lbl, fnt)
        dt(draw, ca - msr(val, fnt), y, val, fnt); y += lh

    rrow("Net Amount",          f"{net_amount:.2f}")
    rrow(f"SC @ {SC_RATE}%",   f"{sc_amt:.2f}")
    rrow(f"CGST {CGST_RATE}%", f"{cgst_amt:.2f}")
    rrow(f"SGST {SGST_RATE}%", f"{sgst_amt:.2f}")

    y += P; y = sep(draw, y, W, M, thick=True) + P

    # total
    gl = "Total"; gv = f"\u20b9{total:.2f}"
    gs = f"{gl}  {gv}"
    dt(draw, W-M-msr(gs, fblg), y, gl, fblg)
    dt(draw, W-M-msr(gv, fblg), y, gv, fblg); y += lhb + P
    y = sep(draw, y, W, M, thick=True) + P

    # dt(draw, M, y, FOOTER_NOTE, fr); y += lh + P
    dt(draw, cx(THANK_YOU, fr, W), y, THANK_YOU, fr); y += lh + 30

    img = img.crop((0, 0, W, y))
    img.save(OUTPUT_FILE)
    print(f"✅  Invoice saved → {OUTPUT_FILE}  ({W}×{y} px)")


if __name__ == "__main__":
    generate_invoice()
