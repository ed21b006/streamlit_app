"""
Invoice Generator - Template: SHRI SAGAR (C.T.R)
==================================================
Based on: example_templates/v2/bill.jpg

Layout:
  - Restaurant name (bold, centered)
  - Address (centered, multi-line)
  - TIN No (centered)
  - Separator
  - Date / Bill No (left/right)
  - Table No / Waiter No (left/right)
  - Separator
  - Ordered Items header: Ordered Items | Qty | Rate | Amount
  - Separator
  - Item rows
  - Separator
  - Total Items (left)
  - Sub Total (right)
  - Grand Total (right)
  - Separator
  - THANK YOU ,VISIT AGAIN (centered)
  - Separator

Output: shri_sagar_ctr_invoice.png
"""

from PIL import Image, ImageDraw, ImageFont

# ─────────────────────────────────────────────
#  VARIABLES  — edit these before running
# ─────────────────────────────────────────────

RESTAURANT_NAME = "SHRI SAGAR(C.T.R)"
ADDRESS_LINE1   = "7TH CROSS,3RD MAIN,MARGOSA ROAD"
ADDRESS_LINE2   = "MALLESHWARAM,BENGALURU-560003"
TIN_NO          = "TIN NO:29910111595"

DATE            = "02/10/2018"
BILL_NO         = "222"
TABLE_NO        = "8"
WAITER_NO       = "12"

# Menu items: list of (name, qty, rate)
ITEMS = []

FOOTER_MSG = "THANK YOU ,VISIT AGAIN"

OUTPUT_FILE = "shri_sagar_ctr_invoice.png"

# ─────────────────────────────────────────────
#  INTERNAL CALCULATIONS (do not edit below)
# ─────────────────────────────────────────────

def compute_totals(items):
    sub_total   = sum(qty * rate for _, qty, rate in items)
    total_items = sum(qty for _, qty, _ in items)
    grand_total = sub_total
    return total_items, sub_total, grand_total


def load_fonts(base_size=26):
    regular_path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
    bold_path    = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
    try:
        font_reg  = ImageFont.truetype(regular_path, base_size)
        font_bold = ImageFont.truetype(bold_path,    base_size)
        font_bold_lg = ImageFont.truetype(bold_path, base_size + 4)
    except OSError:
        font_reg = font_bold = font_bold_lg = ImageFont.load_default()
    return font_reg, font_bold, font_bold_lg


def draw_text(draw, x, y, text, font, fill=(20, 20, 20)):
    draw.text((x, y), text, font=font, fill=fill)


def measure(text, font):
    bbox = font.getbbox(text)
    return bbox[2] - bbox[0]


def centered(text, font, width):
    return (width - measure(text, font)) // 2


def draw_separator(draw, y, width, margin, color=(20, 20, 20)):
    draw.line([(margin, y), (width - margin, y)], fill=color, width=1)
    return y + 2


def generate_invoice():
    total_items, sub_total, grand_total = compute_totals(ITEMS)

    W      = 800
    MARGIN = 24
    PAD    = 10
    line_h = 34
    line_hb = 40

    font_reg, font_bold, font_bold_lg = load_fonts(24)

    est_height = 700 + len(ITEMS) * line_h
    img  = Image.new("RGB", (W, est_height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    y    = 28

    # ── HEADER ──
    draw_text(draw, centered(RESTAURANT_NAME, font_bold_lg, W), y, RESTAURANT_NAME, font_bold_lg)
    y += line_hb + 4

    for line in [ADDRESS_LINE1, ADDRESS_LINE2]:
        if line:
            draw_text(draw, centered(line, font_reg, W), y, line, font_reg)
            y += line_h

    draw_text(draw, centered(TIN_NO, font_reg, W), y, TIN_NO, font_reg)
    y += line_h + PAD

    y = draw_separator(draw, y, W, MARGIN) + PAD

    # ── DATE / BILL NO ──
    date_str = f"Date: {DATE}"
    bill_str = f"Bill No.: {BILL_NO}"
    draw_text(draw, MARGIN, y, date_str, font_reg)
    draw_text(draw, W - MARGIN - measure(bill_str, font_reg), y, bill_str, font_reg)
    y += line_h

    # ── TABLE / WAITER ──
    table_str  = f"Table No.{TABLE_NO}"
    waiter_str = f"Waiter No.{WAITER_NO}"
    draw_text(draw, MARGIN, y, table_str, font_reg)
    draw_text(draw, W - MARGIN - measure(waiter_str, font_reg), y, waiter_str, font_reg)
    y += line_h + PAD

    y = draw_separator(draw, y, W, MARGIN) + PAD

    # ── ITEMS TABLE HEADER ──
    col_item   = MARGIN
    col_qty    = W - MARGIN - 270
    col_rate   = W - MARGIN - 155
    col_amount = W - MARGIN - 10

    draw_text(draw, col_item,                                        y, "Ordered Items", font_reg)
    draw_text(draw, col_qty    - measure("Qty",    font_reg)//2,     y, "Qty",           font_reg)
    draw_text(draw, col_rate   - measure("Rate",   font_reg)//2,     y, "Rate",          font_reg)
    draw_text(draw, col_amount - measure("Amount", font_reg),        y, "Amount",        font_reg)
    y += line_h

    y = draw_separator(draw, y, W, MARGIN) + PAD

    # ── ITEMS ──
    for name, qty, rate in ITEMS:
        amount    = qty * rate
        qty_str   = str(qty)
        rate_str  = f"{rate:.2f}"
        amt_str   = f"{amount:.2f}"
        draw_text(draw, col_item,                                          y, name,     font_reg)
        draw_text(draw, col_qty    - measure(qty_str,   font_reg)//2,     y, qty_str,  font_reg)
        draw_text(draw, col_rate   - measure(rate_str,  font_reg)//2,     y, rate_str, font_reg)
        draw_text(draw, col_amount - measure(amt_str,   font_reg),        y, amt_str,  font_reg)
        y += line_h

    y = draw_separator(draw, y, W, MARGIN) + PAD

    # ── TOTALS ──
    ti_str    = f"Total Items: {total_items}"
    sub_str   = f"{sub_total:.2f}"
    grand_str = f"Rs.{grand_total:.2f}"

    draw_text(draw, MARGIN, y, ti_str, font_reg)
    y += line_h

    sub_lbl = "Sub Total:"
    draw_text(draw, W - MARGIN - measure(sub_lbl + "  " + sub_str, font_reg),  y, sub_lbl, font_reg)
    draw_text(draw, W - MARGIN - measure(sub_str, font_reg), y, sub_str, font_reg)
    y += line_h

    grand_lbl = "GRAND TOTAL:"
    draw_text(draw, W - MARGIN - measure(grand_lbl + "  " + grand_str, font_bold), y, grand_lbl, font_bold)
    draw_text(draw, W - MARGIN - measure(grand_str, font_bold), y, grand_str, font_bold)
    y += line_h + PAD

    y = draw_separator(draw, y, W, MARGIN) + PAD

    # ── FOOTER ──
    draw_text(draw, centered(FOOTER_MSG, font_bold, W), y, FOOTER_MSG, font_bold)
    y += line_h + PAD

    y = draw_separator(draw, y, W, MARGIN) + PAD + 20

    img = img.crop((0, 0, W, y))
    img.save(OUTPUT_FILE)
    print(f"✅  Invoice saved → {OUTPUT_FILE}  ({W}×{y} px)")


if __name__ == "__main__":
    generate_invoice()
