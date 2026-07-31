"""
Invoice Generator - Template: THINDI CAFE
==========================================
Based on: example_templates/v3/thindi cafe.jpg

Layout:
  - "THINDI CAFE" (bold large, centered)
  - Address (centered)
  - Separator
  - Bill No / Date / Time / Cashier (2-col)
  - "Delivery" / "Dine In" label (left)
  - Separator
  - Item | Qty. | Price | Amount (table header)
  - Separator
  - Item rows
  - Separator
  - Sub Total (right)
  - Delivery Charge (right, if any)
  - Discount (right, if any)
  - Separator (thick)
  - Grand Total ₹ (bold, right)
  - Separator (thick)
  - Thank you message (centered)

Output: thindi_cafe_invoice.png
"""

from PIL import Image, ImageDraw, ImageFont

# ─────────────────────────────────────────────
#  VARIABLES  — edit these before running
# ─────────────────────────────────────────────

CAFE_NAME     = "THINDI CAFE"
ADDRESS_LINE1 = "JP Nagar, Bengaluru - 560078"

BILL_NO       = "3210"
DATE          = "31/07/2026"
TIME          = "07:30 PM"
CASHIER       = "biller"
ORDER_TYPE    = "Dine In"

ITEMS = [
    ("Masala Dosa",        2,  70.00),
    ("Filter Coffee",      3,  30.00),
    ("Idli (2 pcs)",       2,  50.00),
    ("Onion Pakoda",       1,  80.00),
]

DELIVERY_CHARGE = 0.00
DISCOUNT        = 0.00

THANK_YOU_MSG   = "Thank you! Come again."
OUTPUT_FILE     = "thindi_cafe_invoice.png"

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
    sub_total   = sum(q * p for _, q, p in ITEMS)
    grand_total = round(sub_total + DELIVERY_CHARGE - DISCOUNT, 2)

    W, M, P = 760, 28, 10
    lh, lhb = 36, 44
    fr, fb, fblg, fbhd = load_fonts(26)

    H = 700 + len(ITEMS) * lh
    img  = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    y    = 28

    # header
    dt(draw, cx(CAFE_NAME, fbhd, W), y, CAFE_NAME, fbhd); y += lhb
    for ln in [ADDRESS_LINE1]:
        dt(draw, cx(ln, fr, W), y, ln, fr); y += lh
    y += P; y = sep(draw, y, W, M) + P

    # bill info
    dt(draw, M, y, f"Bill No.: {BILL_NO}", fr)
    dt(draw, W-M-msr(f"Date: {DATE}", fr), y, f"Date: {DATE}", fr); y += lh
    dt(draw, M, y, f"Time: {TIME}", fr)
    dt(draw, W-M-msr(f"Cashier: {CASHIER}", fr), y, f"Cashier: {CASHIER}", fr); y += lh
    dt(draw, M, y, ORDER_TYPE, fr); y += lh + P
    y = sep(draw, y, W, M) + P

    # table header
    ci = M; cq = W-M-285; cp = W-M-165; ca = W-M-10
    dt(draw, ci, y, "Item", fr)
    dt(draw, cq - msr("Qty.", fr)//2, y, "Qty.", fr)
    dt(draw, cp - msr("Price", fr),   y, "Price", fr)
    dt(draw, ca - msr("Amount", fr),  y, "Amount", fr); y += lh
    y = sep(draw, y, W, M) + P

    # items
    for name, qty, price in ITEMS:
        amount = qty * price
        qs = str(qty); ps = f"{price:.2f}"; as_ = f"{amount:.2f}"
        dt(draw, ci, y, name, fr)
        dt(draw, cq - msr(qs,  fr)//2, y, qs,  fr)
        dt(draw, cp - msr(ps,  fr),    y, ps,  fr)
        dt(draw, ca - msr(as_, fr),    y, as_, fr); y += lh

    y += P; y = sep(draw, y, W, M) + P

    # sub total / extras
    sub_lbl = "Sub Total"; sub_val = f"{sub_total:.2f}"
    dt(draw, cp - msr(sub_lbl, fr), y, sub_lbl, fr)
    dt(draw, ca - msr(sub_val, fr), y, sub_val, fr); y += lh

    if DELIVERY_CHARGE:
        dl = "Delivery Charge"; dv = f"{DELIVERY_CHARGE:.2f}"
        dt(draw, cp - msr(dl, fr), y, dl, fr)
        dt(draw, ca - msr(dv, fr), y, dv, fr); y += lh

    if DISCOUNT:
        disl = "Discount"; disv = f"({DISCOUNT:.2f})"
        dt(draw, cp - msr(disl, fr), y, disl, fr)
        dt(draw, ca - msr(disv, fr), y, disv, fr); y += lh

    y += P; y = sep(draw, y, W, M, thick=True) + P

    # grand total
    gl = "Grand Total"; gv = f"\u20b9{grand_total:.2f}"
    gs = f"{gl}  {gv}"
    dt(draw, W-M-msr(gs, fblg), y, gl, fblg)
    dt(draw, W-M-msr(gv, fblg), y, gv, fblg); y += lhb + P
    y = sep(draw, y, W, M, thick=True) + P

    dt(draw, cx(THANK_YOU_MSG, fr, W), y, THANK_YOU_MSG, fr); y += lh + 30

    img = img.crop((0, 0, W, y))
    img.save(OUTPUT_FILE)
    print(f"✅  Invoice saved → {OUTPUT_FILE}  ({W}×{y} px)")


if __name__ == "__main__":
    generate_invoice()
