"""
Invoice Generator - Template: BY THE WAY
=========================================
Based on: example_templates/v3/by the way.jpg

Layout:
  - Order No (bold, large, centered) e.g. "302"
  - "TAX INVOICE" (centered)
  - "BY THE WAY" (bold, centered)
  - Address block (centered)
  - MO / GSTIN (centered)
  - Separator (dashed)
  - BillNo / Date / Time (left left right)
  - Table / Covers / Waiter (left)
  - *Food* tag (left)
  - Separator (dashed)
  - Item | Qty | Rate | Amount (table header)
  - Separator (dashed)
  - Item rows
  - Separator (dashed)
  - SubTotal (right)
  - SC % / SGST % / CGST % (right)
  - Total (right)
  - Separator
  - Grand Total (RS) (bold, centered)
  - Separator
  - THANK YOU VISIT AGAIN ! (centered)

Output: by_the_way_invoice.png
"""

from PIL import Image, ImageDraw, ImageFont

# ─────────────────────────────────────────────
#  VARIABLES  — edit these before running
# ─────────────────────────────────────────────

RESTAURANT_NAME = "BY THE WAY"
ADDRESS_LINE1   = "Crest Executive Suites,ITPL main road,"
ADDRESS_LINE2   = "whitefield Banglore"
MOBILE          = "MO -8105374722"
GSTIN           = "GSTIN -29ADOPW2284R1Z8"

BILL_NO         = "8763"
DATE            = "31-07-2026"
TIME            = "08:31 PM"
TABLE           = "H1"
COVERS          = "1"
WAITER          = "waiter"
CATEGORY_TAG    = "*Food*"

# Menu items: list of (name, qty, rate)
ITEMS = []

SC_RATE   = 5.00    # Service Charge %
SGST_RATE = 2.50    # %
CGST_RATE = 2.50    # %

THANK_YOU_MSG = "THANK YOU VISIT AGAIN !"

OUTPUT_FILE = "by_the_way_invoice.png"

# ─────────────────────────────────────────────
#  INTERNAL CALCULATIONS (do not edit below)
# ─────────────────────────────────────────────

def compute_totals(items, sc_rate, sgst_rate, cgst_rate):
    sub_total = sum(qty * rate for _, qty, rate in items)
    sc_amt    = round(sub_total * sc_rate   / 100, 2)
    sgst_amt  = round(sub_total * sgst_rate / 100, 2)
    cgst_amt  = round(sub_total * cgst_rate / 100, 2)
    total     = round(sub_total + sc_amt + sgst_amt + cgst_amt, 2)
    grand     = round(total)
    return sub_total, sc_amt, sgst_amt, cgst_amt, total, grand


def load_fonts(base_size=26):
    reg_path  = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
    bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
    try:
        font_reg   = ImageFont.truetype(reg_path,  base_size)
        font_bold  = ImageFont.truetype(bold_path, base_size)
        font_bold_lg = ImageFont.truetype(bold_path, base_size + 8)
        font_order   = ImageFont.truetype(bold_path, base_size + 16)
    except OSError:
        font_reg = font_bold = font_bold_lg = font_order = ImageFont.load_default()
    return font_reg, font_bold, font_bold_lg, font_order


def draw_text(draw, x, y, text, font, fill=(20, 20, 20)):
    draw.text((x, y), text, font=font, fill=fill)


def measure(text, font):
    bbox = font.getbbox(text)
    return bbox[2] - bbox[0]


def centered(text, font, width):
    return (width - measure(text, font)) // 2


def draw_separator(draw, y, width, margin, dashed=True, color=(20, 20, 20)):
    if dashed:
        seg, gap, x = 8, 6, margin
        while x < width - margin:
            draw.line([(x, y), (min(x + seg, width - margin), y)], fill=color, width=1)
            x += seg + gap
    else:
        draw.line([(margin, y), (width - margin, y)], fill=color, width=2)
    return y + 2


def generate_invoice():
    sub_total, sc_amt, sgst_amt, cgst_amt, total, grand = compute_totals(
        ITEMS, SC_RATE, SGST_RATE, CGST_RATE
    )

    W      = 760
    MARGIN = 28
    PAD    = 10
    line_h = 36
    line_hb = 44

    font_reg, font_bold, font_bold_lg, font_order = load_fonts(26)

    est_height = 800 + len(ITEMS) * line_h
    img  = Image.new("RGB", (W, est_height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    y    = 28

    # ── ORDER NUMBER (large bold centered) ──
    # draw_text(draw, centered(ORDER_NO, font_order, W), y, ORDER_NO, font_order)
    y += line_hb + 10

    # ── TAX INVOICE + RESTAURANT NAME ──
    draw_text(draw, centered("TAX INVOICE", font_bold, W), y, "TAX INVOICE", font_bold)
    y += line_hb
    draw_text(draw, centered(RESTAURANT_NAME, font_bold, W), y, RESTAURANT_NAME, font_bold)
    y += line_hb + PAD

    # ── ADDRESS ──
    for line in [ADDRESS_LINE1, ADDRESS_LINE2, MOBILE, GSTIN]:
        if line:
            draw_text(draw, centered(line, font_reg, W), y, line, font_reg)
            y += line_h

    y += PAD
    y = draw_separator(draw, y, W, MARGIN, dashed=True) + PAD

    # ── BILL INFO ──
    bill_str = f"BillNo : {BILL_NO}"
    date_str = f"Date : {DATE} {TIME}"
    draw_text(draw, MARGIN, y, bill_str, font_reg)
    draw_text(draw, W - MARGIN - measure(date_str, font_reg), y, date_str, font_reg)
    y += line_h

    table_str  = f"Table : {TABLE}  Covers : {COVERS}  Waiter : {WAITER}"
    draw_text(draw, MARGIN, y, table_str, font_reg)
    y += line_h

    if CATEGORY_TAG:
        draw_text(draw, MARGIN, y, CATEGORY_TAG, font_reg)
        y += line_h

    y += PAD
    y = draw_separator(draw, y, W, MARGIN, dashed=True) + PAD

    # ── TABLE HEADER ──
    col_item = MARGIN
    col_qty  = W - MARGIN - 290
    col_rate = W - MARGIN - 165
    col_amt  = W - MARGIN - 10

    draw_text(draw, col_item,                            y, "Item",   font_reg)
    draw_text(draw, col_qty  - measure("Qty",  font_reg)//2, y, "Qty",   font_reg)
    draw_text(draw, col_rate - measure("Rate", font_reg),    y, "Rate",  font_reg)
    draw_text(draw, col_amt  - measure("Amount", font_reg),  y, "Amount",font_reg)
    y += line_h

    y = draw_separator(draw, y, W, MARGIN, dashed=True) + PAD

    # ── ITEMS ──
    for name, qty, rate in ITEMS:
        amount   = qty * rate
        qty_str  = str(qty)
        rate_str = f"{rate:.1f}"
        amt_str  = f"{amount:.2f}"
        draw_text(draw, col_item,                                  y, name,     font_reg)
        draw_text(draw, col_qty  - measure(qty_str,  font_reg)//2, y, qty_str,  font_reg)
        draw_text(draw, col_rate - measure(rate_str, font_reg),    y, rate_str, font_reg)
        draw_text(draw, col_amt  - measure(amt_str,  font_reg),    y, amt_str,  font_reg)
        y += line_h

    y += PAD
    y = draw_separator(draw, y, W, MARGIN, dashed=True) + PAD

    # ── TOTALS (right-aligned label + value) ──
    def draw_right_row(label, value, fnt=font_reg):
        nonlocal y
        lbl_w = measure(label + "  ", fnt)
        val_w = measure(value, fnt)
        full_w = lbl_w + val_w
        draw_text(draw, col_amt - full_w,         y, label, fnt)
        draw_text(draw, col_amt - measure(value, fnt), y, value, fnt)
        y += line_h

    draw_right_row("SubTotal :",          f"{sub_total:.2f}")
    draw_right_row(f"SC {SC_RATE:.2f}% :",  f"{sc_amt:.2f}")
    draw_right_row(f"SGST {SGST_RATE:.2f}% :", f"{sgst_amt:.2f}")
    draw_right_row(f"CGST {CGST_RATE:.2f}% :", f"{cgst_amt:.2f}")
    draw_right_row("Total :",             f"{total:.2f}")

    y += PAD
    y = draw_separator(draw, y, W, MARGIN, dashed=False) + PAD

    # ── GRAND TOTAL (bold, centered) ──
    grand_str = f"Grand Total (RS) :  {grand}"
    draw_text(draw, centered(grand_str, font_bold_lg, W), y, grand_str, font_bold_lg)
    y += line_hb + PAD

    y = draw_separator(draw, y, W, MARGIN, dashed=False) + PAD

    # ── THANK YOU ──
    draw_text(draw, centered(THANK_YOU_MSG, font_reg, W), y, THANK_YOU_MSG, font_reg)
    y += line_h + 30

    img = img.crop((0, 0, W, y))
    img.save(OUTPUT_FILE)
    print(f"✅  Invoice saved → {OUTPUT_FILE}  ({W}×{y} px)")


if __name__ == "__main__":
    generate_invoice()
