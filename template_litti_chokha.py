"""
Invoice Generator - Template: LITTI CHOKHA
===========================================
Based on: example_templates/v3/litti chokha.jpg

Layout:
  - "Litti Chokha.Com - ITPL Main Road" (bold, centered)
  - Mob / Email (centered)
  - Solid separator
  - Name: (left)
  - Solid separator
  - Date (left) | Dine In: X (bold, right)
  - Time (left)
  - Cashier (left) | Bill No. (right)
  - Token No. (bold, left)
  - Solid separator
  - Item | Qty. | Price | Amount (table header)
  - Separator
  - Item rows (description wraps left; qty/price/amount on last line)
  - Separator
  - Total Qty / Sub Total (left/right)
  - Separator (thick)
  - Grand Total ₹ (bold, right)
  - Separator (thick)
  - Thank you message (centered)

Output: litti_chokha_invoice.png
"""

from PIL import Image, ImageDraw, ImageFont

# ─────────────────────────────────────────────
#  VARIABLES  — edit these before running
# ─────────────────────────────────────────────

RESTAURANT_NAME = "Litti Chokha.Com - ITPL Main Road"
MOBILE          = "Mob.- 8867042299"
EMAIL           = "Email- officelittichokha@gmail.com"

CUSTOMER_NAME   = ""
DATE            = "26/07/26"
TIME            = "20:04"
ORDER_TYPE      = "Dine In: 1"   # e.g. "Dine In: 1" or "Pick Up"
CASHIER         = "biller"
BILL_NO         = "42422"
TOKEN_NO        = "103"

ITEMS = [
    ("Chicken Litti (Regular (2pc Litti & 2Pc Champaran Chicken))", 1, 280.00),
]

THANK_YOU_MSG = "Thank You. Please Visit Again"
OUTPUT_FILE   = "litti_chokha_invoice.png"

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def load_fonts(base=28):
    rp = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
    bp = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
    try:
        fr   = ImageFont.truetype(rp, base)
        fb   = ImageFont.truetype(bp, base)
        fblg = ImageFont.truetype(bp, base + 6)
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
    sub_total  = sum(q * p for _, q, p in ITEMS)
    total_qty  = sum(q for _, q, _ in ITEMS)
    grand_total = sub_total

    W, M, P = 760, 28, 10
    lh, lhb = 36, 44
    fr, fb, fblg, fbhd = load_fonts(26)

    H = 700 + len(ITEMS) * lh * 4
    img  = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    y    = 30

    # header
    dt(draw, cx(RESTAURANT_NAME, fbhd, W), y, RESTAURANT_NAME, fbhd); y += lhb
    dt(draw, cx(MOBILE, fr, W), y, MOBILE, fr); y += lh
    dt(draw, cx(EMAIL,  fr, W), y, EMAIL,  fr); y += lh + P
    y = sep(draw, y, W, M) + P

    # customer name
    dt(draw, M, y, f"Name: {CUSTOMER_NAME}", fr); y += lh + P
    y = sep(draw, y, W, M) + P

    # bill info
    dt(draw, M, y, f"Date: {DATE}", fr)
    dt(draw, W-M-msr(ORDER_TYPE, fb), y, ORDER_TYPE, fb); y += lh
    dt(draw, M, y, TIME, fr); y += lh
    dt(draw, M, y, f"Cashier: {CASHIER}", fr)
    dt(draw, W-M-msr(f"Bill No.: {BILL_NO}", fr), y, f"Bill No.: {BILL_NO}", fr); y += lh
    dt(draw, M, y, f"Token No.: {TOKEN_NO}", fb); y += lhb + P
    y = sep(draw, y, W, M) + P

    # table header
    ci = M; cq = W-M-290; cp = W-M-160; ca = W-M-10
    dt(draw, ci, y, "Item", fr)
    dt(draw, cq - msr("Qty.", fr)//2, y, "Qty.", fr)
    dt(draw, cp - msr("Price", fr),   y, "Price", fr)
    dt(draw, ca - msr("Amount", fr),  y, "Amount", fr); y += lh
    y = sep(draw, y, W, M) + P

    # items
    for name, qty, price in ITEMS:
        amount = qty * price
        qs = str(qty); ps = f"{price:.2f}"; as_ = f"{amount:.2f}"
        dls = wrap(name, fr, cq - ci - 12)
        for dl in dls[:-1]:
            dt(draw, ci, y, dl, fr); y += lh
        dt(draw, ci, y, dls[-1], fr)
        dt(draw, cq - msr(qs,  fr)//2, y, qs, fr)
        dt(draw, cp - msr(ps,  fr),    y, ps, fr)
        dt(draw, ca - msr(as_, fr),    y, as_, fr); y += lh

    y += P; y = sep(draw, y, W, M) + P

    # totals
    tq_str  = f"Total Qty: {total_qty}"
    sub_str = f"{sub_total:.2f}"
    dt(draw, M, y, tq_str, fr)
    sub_lbl = "Sub Total"
    dt(draw, cp - msr(sub_lbl, fr), y, sub_lbl, fr)
    dt(draw, ca - msr(sub_str, fr), y, sub_str, fr); y += lh + P
    y = sep(draw, y, W, M, thick=True) + P

    # grand total
    gl = "Grand Total"; gv = f"\u20b9{grand_total:.2f}"
    gs = f"{gl}  {gv}"
    dt(draw, W-M-msr(gs,  fblg), y, gl, fblg)
    dt(draw, W-M-msr(gv,  fblg), y, gv, fblg); y += lhb + P
    y = sep(draw, y, W, M, thick=True) + P

    # thank you
    dt(draw, cx(THANK_YOU_MSG, fr, W), y, THANK_YOU_MSG, fr); y += lh + 30

    img = img.crop((0, 0, W, y))
    img.save(OUTPUT_FILE)
    print(f"✅  Invoice saved → {OUTPUT_FILE}  ({W}×{y} px)")


if __name__ == "__main__":
    generate_invoice()
