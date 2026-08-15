"""
Invoice Generator - Template: VB BAKERY
========================================
Based on: example_templates/v3/vb bakery.jpg

Layout:
  - "VB BAKERY" (bold large, centered)
  - "Vaidika Brahmin Bakery" or tag line (centered)
  - Address block (centered)
  - Separator
  - Invoice No / Date (left/right)
  - Time / Cashier (left/right)
  - Separator
  - Item | Qty | Price | Total (table header)
  - Separator
  - Item rows
  - Separator
  - Sub Total (right)
  - CGST / SGST (right, if applicable)
  - Separator (thick)
  - Grand Total ₹ (bold, right)
  - Separator (thick)
  - "Thanks for your purchase!" (centered)

Output: vb_bakery_invoice.png
"""

from PIL import Image, ImageDraw, ImageFont

# ─────────────────────────────────────────────
#  VARIABLES  — edit these before running
# ─────────────────────────────────────────────

BAKERY_NAME   = "VB BAKERY"
BRAND_NAME    = "Vaidika Brahmin Bakery"
ADDRESS_LINE1 = "15, Gandhi Nagar, Bengaluru"
ADDRESS_LINE2 = "Karnataka - 560009"

INVOICE_NO    = "INV-0921"
DATE          = "31/07/2026"
TIME          = "10:30 AM"
CASHIER       = "biller"

ITEMS = []

CGST_RATE = 2.5
SGST_RATE = 2.5

THANK_YOU_MSG = "Thanks for your purchase! Visit again."
OUTPUT_FILE   = "vb_bakery_invoice.png"

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
    sub_total = sum(q * p for _, q, p in ITEMS)
    cgst_amt  = round(sub_total * CGST_RATE / 100, 2)
    sgst_amt  = round(sub_total * SGST_RATE / 100, 2)
    grand     = round(sub_total + cgst_amt + sgst_amt, 2)

    W, M, P = 760, 28, 10
    lh, lhb = 36, 44
    fr, fb, fblg, fbhd = load_fonts(26)

    H = 750 + len(ITEMS) * lh
    img  = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    y    = 28

    # header
    dt(draw, cx(BAKERY_NAME, fbhd, W), y, BAKERY_NAME, fbhd); y += lhb
    dt(draw, cx(BRAND_NAME, fr, W), y, BRAND_NAME, fr); y += lh
    for ln in [ADDRESS_LINE1, ADDRESS_LINE2]:
        dt(draw, cx(ln, fr, W), y, ln, fr); y += lh
    y += P; y = sep(draw, y, W, M) + P

    # invoice info
    dt(draw, M, y, f"Invoice No.: {INVOICE_NO}", fr)
    dt(draw, W-M-msr(f"Date: {DATE}", fr), y, f"Date: {DATE}", fr); y += lh
    dt(draw, M, y, f"Time: {TIME}", fr)
    dt(draw, W-M-msr(f"Cashier: {CASHIER}", fr), y, f"Cashier: {CASHIER}", fr); y += lh + P
    y = sep(draw, y, W, M) + P

    # table header
    ci = M; cq = W-M-290; cp = W-M-165; ca = W-M-10
    dt(draw, ci, y, "Item", fr)
    dt(draw, cq - msr("Qty", fr)//2, y, "Qty", fr)
    dt(draw, cp - msr("Price", fr),  y, "Price", fr)
    dt(draw, ca - msr("Total", fr),  y, "Total", fr); y += lh
    y = sep(draw, y, W, M) + P

    # items
    for name, qty, price in ITEMS:
        total_item = qty * price
        qs = str(qty); ps = f"{price:.2f}"; ts = f"{total_item:.2f}"
        dt(draw, ci, y, name, fr)
        dt(draw, cq - msr(qs, fr)//2, y, qs, fr)
        dt(draw, cp - msr(ps, fr),    y, ps, fr)
        dt(draw, ca - msr(ts, fr),    y, ts, fr); y += lh

    y += P; y = sep(draw, y, W, M) + P

    # totals
    sub_lbl = "Sub Total"; sub_val = f"{sub_total:.2f}"
    dt(draw, cp - msr(sub_lbl, fr), y, sub_lbl, fr)
    dt(draw, ca - msr(sub_val, fr), y, sub_val, fr); y += lh

    cgst_lbl = f"CGST {CGST_RATE}%"; cgst_val = f"{cgst_amt:.2f}"
    dt(draw, cp - msr(cgst_lbl, fr), y, cgst_lbl, fr)
    dt(draw, ca - msr(cgst_val, fr), y, cgst_val, fr); y += lh

    sgst_lbl = f"SGST {SGST_RATE}%"; sgst_val = f"{sgst_amt:.2f}"
    dt(draw, cp - msr(sgst_lbl, fr), y, sgst_lbl, fr)
    dt(draw, ca - msr(sgst_val, fr), y, sgst_val, fr); y += lh + P
    y = sep(draw, y, W, M, thick=True) + P

    # grand total
    gl = "Grand Total"; gv = f"\u20b9{grand:.2f}"
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
