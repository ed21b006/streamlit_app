"""
Invoice Generator - Template: CALIFORNIA BURRITO
=================================================
Based on: example_templates/v3/california burrito.jpg

Layout:
  - "California Burrito" (bold large, centered)
  - Company / Address / GSTIN / FSSAI (centered)
  - "TAX INVOICE # <no>" (bold, centered)
  - Separator
  - Order ID / Outlet / Date / Time
  - Separator
  - Item | Qty | Price | Total (table)
  - Item rows (with wrap)
  - Separator
  - Sub-total / Discount / Other Charges / CGST / SGST (right)
  - Separator
  - Grand Total (bold, right)
  - Separator
  - Mob / Points / Loyalty text
  - Separator
  - Legal fine print

Output: california_burrito_invoice.png
"""

from PIL import Image, ImageDraw, ImageFont

# ─────────────────────────────────────────────
#  VARIABLES  — edit these before running
# ─────────────────────────────────────────────

BRAND_NAME   = "California Burrito"
COMPANY_NAME = "Burrito Restaurants Pvt.Ltd."
ADDRESS_LINE1= "Nexus Shantiniketan Mall, Whitefield Main Rd,"
ADDRESS_LINE2= "Thigalarapalya, Krishnarajapura, Bengaluru, Karnataka"
ADDRESS_LINE3= "560067"
GSTIN        = "GSTIN:29AAECB8940R1ZT"
FSSAI        = "FSSAI:"

INVOICE_NO   = "57-217552"
ORDER_ID     = "217608"
OUTLET       = "Outlet STN"
DATE         = "18-07-2026"
TIME         = "10:31 PM"
MOBILE       = "8278693542"
POINTS_EARNED= "67"

ITEMS = [
    ("Chicken (Chili Chipotle) Bowl", 2, 279.0),
    ("Chicken (Crispy) Bowl",          2, 279.0),
    ("Paneer (BBQ) Bowl",              2, 279.0),
    ("Bagasse Bowl Big Free",          6,   0.0),
]

DISCOUNT      = 0.00
OTHER_CHARGES = 0.00
CGST_RATE     = 2.5
SGST_RATE     = 2.5

LOYALTY_LINE1 = "100 points = Free Meal!"
LOYALTY_LINE2 = "Check points balance at"
LOYALTY_LINE3 = "order.californiaburrito.in/accounts"
LEGAL_LINE1   = "CIN U5101TN2012PTC190057 HSN 789784"
LEGAL_LINE2   = "*Whether tax is Payable under Reverse Charges(Yes/No): No"
LEGAL_LINE3   = "Computer generated invoice and requires no signature"

OUTPUT_FILE   = "california_burrito_invoice.png"

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def compute_totals(items, discount, other_charges, cgst_rate, sgst_rate):
    sub   = sum(q * p for _, q, p in items)
    tax   = sub - discount + other_charges
    cgst  = round(tax * cgst_rate / 100, 2)
    sgst  = round(tax * sgst_rate / 100, 2)
    grand = round(tax + cgst + sgst, 2)
    return sub, cgst, sgst, grand


def load_fonts(base=24):
    rp = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
    bp = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
    try:
        fr   = ImageFont.truetype(rp, base)
        fb   = ImageFont.truetype(bp, base)
        fbrn = ImageFont.truetype(bp, base + 8)
        fblg = ImageFont.truetype(bp, base + 4)
        fsm  = ImageFont.truetype(rp, base - 4)
    except OSError:
        fr = fb = fbrn = fblg = fsm = ImageFont.load_default()
    return fr, fb, fbrn, fblg, fsm


def dt(draw, x, y, text, font, fill=(20, 20, 20)):
    draw.text((x, y), text, font=font, fill=fill)


def msr(text, font):
    b = font.getbbox(text)
    return b[2] - b[0]


def cx(text, font, W):
    return (W - msr(text, font)) // 2


def sep(draw, y, W, M, dashed=True, thick=False):
    if dashed:
        x = M
        while x < W - M:
            draw.line([(x, y), (min(x+8, W-M), y)], fill=(20,20,20), width=1)
            x += 14
    else:
        draw.line([(M, y), (W-M, y)], fill=(20,20,20), width=2 if thick else 1)
    return y + 2


def wrap(text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if msr(t, font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [text]


def generate_invoice():
    sub, cgst, sgst, grand = compute_totals(ITEMS, DISCOUNT, OTHER_CHARGES, CGST_RATE, SGST_RATE)

    W, M, P = 760, 28, 10
    lh, lhb = 34, 42
    fr, fb, fbrn, fblg, fsm = load_fonts(24)

    H = 1100 + len(ITEMS) * lh
    img  = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    y    = 28

    # header
    dt(draw, cx(BRAND_NAME, fbrn, W), y, BRAND_NAME, fbrn); y += lhb
    for ln in [COMPANY_NAME, ADDRESS_LINE1, ADDRESS_LINE2, ADDRESS_LINE3, GSTIN, FSSAI]:
        if ln:
            dt(draw, cx(ln, fr, W), y, ln, fr); y += lh
    inv = f"TAX INVOICE # {INVOICE_NO}"
    dt(draw, cx(inv, fblg, W), y, inv, fblg); y += lhb + P
    y = sep(draw, y, W, M, dashed=True) + P

    # order info
    dt(draw, M, y, f"Order ID: {ORDER_ID}", fr)
    dt(draw, W-M-msr(OUTLET, fr), y, OUTLET, fr); y += lh
    dt(draw, M, y, f"Date: {DATE}", fr)
    dt(draw, W-M-msr(f"Time: {TIME}", fr), y, f"Time: {TIME}", fr); y += lh + P
    y = sep(draw, y, W, M, dashed=True) + P

    # table header
    ci = M; cq = W-M-290; cp = W-M-165; ca = W-M-10
    dt(draw, ci, y, "Item", fb)
    dt(draw, cq - msr("Qty", fb)//2, y, "Qty", fb)
    dt(draw, cp - msr("Price", fb),  y, "Price", fb)
    dt(draw, ca - msr("Total", fb),  y, "Total", fb); y += lh
    y = sep(draw, y, W, M, dashed=True) + P

    # items
    for name, qty, price in ITEMS:
        tot = qty * price
        qs  = str(qty); ps = f"{price:.1f}"; ts = f"{tot:.1f}"
        dls = wrap(name, fr, cq - ci - 12)
        for dl in dls[:-1]:
            dt(draw, ci, y, dl, fr); y += lh
        dt(draw, ci, y, dls[-1], fr)
        dt(draw, cq - msr(qs, fr)//2, y, qs, fr)
        dt(draw, cp - msr(ps, fr),    y, ps, fr)
        dt(draw, ca - msr(ts, fr),    y, ts, fr); y += lh

    y += P; y = sep(draw, y, W, M, dashed=True) + P

    # totals
    def rrow(lbl, val, fnt=fr):
        nonlocal y
        full = lbl + "  " + val
        dt(draw, ca - msr(full, fnt), y, lbl, fnt)
        dt(draw, ca - msr(val, fnt),  y, val, fnt); y += lh

    dt(draw, ca - msr(f"{sub:.2f}", fr), y, f"{sub:.2f}", fr); y += lh
    rrow("Discount",          f"{DISCOUNT:.2f}")
    rrow("Other Charges",     f"{OTHER_CHARGES:.2f}")
    rrow(f"CGST @ {CGST_RATE}%", f"{cgst:.2f}")
    rrow(f"SGST @ {SGST_RATE}%", f"{sgst:.2f}")
    y += P; y = sep(draw, y, W, M, dashed=True) + P

    # grand total
    gl = "Grand Total"; gv = f"{grand:.2f}"
    fg = f"{gl}  {gv}"
    dt(draw, ca - msr(fg, fblg), y, gl, fblg)
    dt(draw, ca - msr(gv, fblg), y, gv, fblg); y += lhb + P
    y = sep(draw, y, W, M, dashed=True) + P

    # loyalty
    dt(draw, M, y, f"Mob: {MOBILE}", fr)
    dt(draw, W-M-msr(f"Points earned: {POINTS_EARNED}", fr), y, f"Points earned: {POINTS_EARNED}", fr); y += lh
    for ln in [LOYALTY_LINE1, LOYALTY_LINE2, LOYALTY_LINE3]:
        dt(draw, cx(ln, fr, W), y, ln, fr); y += lh
    y += P; y = sep(draw, y, W, M, dashed=True) + P

    # legal
    for ln in [LEGAL_LINE1, LEGAL_LINE2, LEGAL_LINE3]:
        dt(draw, cx(ln, fsm, W), y, ln, fsm); y += lh - 4
    y += 30

    img = img.crop((0, 0, W, y))
    img.save(OUTPUT_FILE)
    print(f"✅  Invoice saved → {OUTPUT_FILE}  ({W}×{y} px)")


if __name__ == "__main__":
    generate_invoice()
