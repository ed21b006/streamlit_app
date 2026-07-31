"""
Invoice Generator - Template: SEA-INN RESTAURANT (Rajugari Dhaba)
==================================================================
Based on: example_templates/v2/images-3.jpeg

Layout:
  - Restaurant name (bold, centered)
  - Sub-title "(RAJUGARI DHABA)" (centered)
  - Location / TIN / Phone (centered)
  - Dotted separator with "...CASH/BILL..." label
  - Bill No / 0 / 0 / Date header row
  - Separator
  - DESCRIPTION | QTY | RATE | AMOUNT table header
  - Separator
  - Item rows
  - Separator
  - CASH (left) | Amount (right)
  - "THANQ VISIT AGAIN" (centered)
  - Time (left)
  - Footer row (bill copy ref + 0)

Output: sea_inn_restaurant_invoice.png
"""

from PIL import Image, ImageDraw, ImageFont

# ─────────────────────────────────────────────
#  VARIABLES  — edit these before running
# ─────────────────────────────────────────────

RESTAURANT_NAME = "SEA-INN RESTAURANT"
SUB_TITLE       = "(RAJUGARI DHABA)"
LOCATION        = "RUSHIKONDA.  VIZAG"
TIN             = "TIN:37626587282"
PHONE           = "PH:9966527667"

BILL_NO         = "000073"
DATE            = "16-02-2018"

# Menu items: list of (description, qty, rate)
# Note: rate and qty are integers in this template
ITEMS = [
    ("MUTN.BIRYANI",    1, 220.00),
    ("PRAWN FRY",       1, 210.00),
    ("LIVER FRY",       1, 140.00),
    ("RICE.SMBR.CURD",  2,  60.00),
    ("COOLDRINK",       3,  20.00),
    ("TIN COOL DRINK",  1,  40.00),
]

PAYMENT_MODE  = "CASH"              # "CASH" / "UPI" / "CARD"
FOOTER_NOTE   = "THANQ VISIT AGAIN"
TIME          = "14:17:31"
COPY_REF      = "C 1"               # bottom-left footer ref (e.g. "C 1")

OUTPUT_FILE = "sea_inn_restaurant_invoice.png"

# ─────────────────────────────────────────────
#  INTERNAL CALCULATIONS (do not edit below)
# ─────────────────────────────────────────────

def compute_total(items):
    return sum(qty * rate for _, qty, rate in items)


def load_fonts(base_size=26):
    regular_path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
    bold_path    = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
    try:
        font_reg     = ImageFont.truetype(regular_path, base_size)
        font_bold    = ImageFont.truetype(bold_path,    base_size)
        font_bold_hdr = ImageFont.truetype(bold_path,  base_size + 4)
    except OSError:
        font_reg = font_bold = font_bold_hdr = ImageFont.load_default()
    return font_reg, font_bold, font_bold_hdr


def draw_text(draw, x, y, text, font, fill=(20, 20, 20)):
    draw.text((x, y), text, font=font, fill=fill)


def measure(text, font):
    bbox = font.getbbox(text)
    return bbox[2] - bbox[0]


def centered(text, font, width):
    return (width - measure(text, font)) // 2


def draw_separator(draw, y, width, margin, dashed=False, color=(20, 20, 20)):
    if dashed:
        seg, gap, x = 6, 4, margin
        while x < width - margin:
            draw.line([(x, y), (min(x + seg, width - margin), y)], fill=color, width=1)
            x += seg + gap
    else:
        draw.line([(margin, y), (width - margin, y)], fill=color, width=1)
    return y + 2


def generate_invoice():
    total_amount = compute_total(ITEMS)

    W      = 800
    MARGIN = 24
    PAD    = 10
    line_h = 34
    line_hb = 40

    font_reg, font_bold, font_bold_hdr = load_fonts(24)

    est_height = 700 + len(ITEMS) * line_h
    img  = Image.new("RGB", (W, est_height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    y    = 28

    # ── HEADER ──
    draw_text(draw, centered(RESTAURANT_NAME, font_bold_hdr, W), y, RESTAURANT_NAME, font_bold_hdr)
    y += line_hb + 4

    draw_text(draw, centered(SUB_TITLE, font_reg, W), y, SUB_TITLE, font_reg)
    y += line_h

    draw_text(draw, centered(LOCATION, font_reg, W), y, LOCATION, font_reg)
    y += line_h

    tin_phone = f"{TIN};{PHONE}"
    draw_text(draw, centered(tin_phone, font_reg, W), y, tin_phone, font_reg)
    y += line_h + PAD

    # ── CASH/BILL dotted separator ──
    cash_bill_label = "....CASH/BILL...."
    draw_text(draw, centered(cash_bill_label, font_bold, W), y, cash_bill_label, font_bold)
    y += line_hb + PAD

    # ── BILL HEADER ROW ──
    draw_text(draw, MARGIN, y, f"NO {BILL_NO}", font_reg)
    draw_text(draw, W//2 - measure("0", font_reg)//2, y, "0", font_reg)
    draw_text(draw, W - MARGIN - measure(DATE, font_reg), y, DATE, font_reg)
    y += line_h + PAD

    y = draw_separator(draw, y, W, MARGIN) + PAD

    # ── ITEMS TABLE HEADER ──
    col_desc   = MARGIN
    col_qty    = W - MARGIN - 270
    col_rate   = W - MARGIN - 155
    col_amount = W - MARGIN - 10

    draw_text(draw, col_desc,                                        y, "DESCRIPTION", font_reg)
    draw_text(draw, col_qty    - measure("QTY",    font_reg)//2,     y, "QTY",         font_reg)
    draw_text(draw, col_rate   - measure("RATE",   font_reg)//2,     y, "RATE",        font_reg)
    draw_text(draw, col_amount - measure("AMOUNT", font_reg),        y, "AMOUNT",      font_reg)
    y += line_h

    y = draw_separator(draw, y, W, MARGIN) + PAD

    # ── ITEMS ──
    for desc, qty, rate in ITEMS:
        amount   = qty * rate
        qty_str  = str(qty)
        rate_str = f"{rate:.2f}"
        amt_str  = f"{amount:.2f}"
        draw_text(draw, col_desc,                                        y, desc,     font_reg)
        draw_text(draw, col_qty    - measure(qty_str,  font_reg)//2,     y, qty_str,  font_reg)
        draw_text(draw, col_rate   - measure(rate_str, font_reg)//2,     y, rate_str, font_reg)
        draw_text(draw, col_amount - measure(amt_str,  font_reg),        y, amt_str,  font_reg)
        y += line_h

    y += PAD
    y = draw_separator(draw, y, W, MARGIN) + PAD

    # ── PAYMENT MODE / TOTAL ──
    total_str = f"{total_amount:.2f}"
    draw_text(draw, MARGIN, y, PAYMENT_MODE, font_bold)
    draw_text(draw, W - MARGIN - measure(total_str, font_bold), y, total_str, font_bold)
    y += line_hb + PAD

    # ── FOOTER NOTE ──
    draw_text(draw, centered(FOOTER_NOTE, font_bold, W), y, FOOTER_NOTE, font_bold)
    y += line_hb + PAD

    # ── TIME / COPY REF ──
    draw_text(draw, MARGIN, y, TIME, font_reg)
    y += line_h + 20

    img = img.crop((0, 0, W, y))
    img.save(OUTPUT_FILE)
    print(f"✅  Invoice saved → {OUTPUT_FILE}  ({W}×{y} px)")


if __name__ == "__main__":
    generate_invoice()
