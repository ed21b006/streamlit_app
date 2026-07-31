"""
Invoice Generator - Template: NAKSHATRA KITCHEN
================================================
Based on: example_templates/1000174412.jpg

Layout:
  - Restaurant name (bold, centered)
  - Address block (centered)
  - Phone (centered)
  - Separator line
  - Customer Name line
  - Separator line
  - Date / Order type / Time / Cashier / Bill No
  - Separator line
  - Items table (Item | Qty | Price | Amount)
  - Separator line
  - Total Qty / Sub Total
  - Separator line
  - Grand Total (bold, right aligned)
  - Separator line
  - Thank you message (centered)

Output: nakshatra_kitchen_invoice.png
"""

from PIL import Image, ImageDraw, ImageFont
import math

# ─────────────────────────────────────────────
#  VARIABLES  — edit these before running
# ─────────────────────────────────────────────

RESTAURANT_NAME = "NAKSHATRA KITCHEN"
ADDRESS_LINE1   = "392/1,Shop#3, JRS Commerical"
ADDRESS_LINE2   = "complex,Near Krishana Temple &"
ADDRESS_LINE3   = "Behind Whitefield post office,"
ADDRESS_LINE4   = "Dodswort Layout, Whitefield,"
ADDRESS_LINE5   = "Banglore-560066"
PHONE           = "Phone No: 8105654116"

CUSTOMER_NAME   = ""                # leave blank if not filled
DATE            = "07/07/26"        # DD/MM/YY
TIME            = "22:49"
ORDER_TYPE      = "Pick Up"         # "Pick Up" or "Dine In"
CASHIER         = "biller"
BILL_NO         = "5075"

# Menu items: list of (name, qty, unit_price)
ITEMS = [
    ("Pulka (Butter)", 4, 25.00),
    ("Kadai Paneer",   1, 160.00),
    ("Goli Soda",      2, 30.00),
]

THANK_YOU_MESSAGE = "THANK YOU VISIT AGAIN"

OUTPUT_FILE = "nakshatra_kitchen_invoice.png"

# ─────────────────────────────────────────────
#  INTERNAL CALCULATIONS (do not edit below)
# ─────────────────────────────────────────────

def compute_totals(items):
    sub_total  = sum(qty * price for _, qty, price in items)
    total_qty  = sum(qty for _, qty, _ in items)
    grand_total = sub_total
    return total_qty, sub_total, grand_total


def load_fonts(base_size=28):
    regular_path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
    bold_path    = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
    try:
        font_reg  = ImageFont.truetype(regular_path, base_size)
        font_bold = ImageFont.truetype(bold_path,    base_size)
        font_bold_lg = ImageFont.truetype(bold_path, base_size + 6)
        font_bold_hdr = ImageFont.truetype(bold_path, base_size + 4)
    except OSError:
        font_reg = font_bold = font_bold_lg = font_bold_hdr = ImageFont.load_default()
    return font_reg, font_bold, font_bold_lg, font_bold_hdr


def draw_text(draw, x, y, text, font, fill=(20, 20, 20)):
    draw.text((x, y), text, font=font, fill=fill)


def measure(text, font):
    bbox = font.getbbox(text)
    return bbox[2] - bbox[0]


def centered(text, font, width):
    return (width - measure(text, font)) // 2


def draw_separator(draw, y, width, margin, dashed=False, color=(20, 20, 20)):
    if dashed:
        seg, gap = 8, 6
        x = margin
        while x < width - margin:
            draw.line([(x, y), (min(x + seg, width - margin), y)], fill=color, width=1)
            x += seg + gap
    else:
        draw.line([(margin, y), (width - margin, y)], fill=color, width=2)
    return y + 2


def generate_invoice():
    total_qty, sub_total, grand_total = compute_totals(ITEMS)

    # Canvas dimensions
    W       = 760
    MARGIN  = 28
    PAD     = 10   # vertical padding between elements

    font_reg, font_bold, font_bold_lg, font_bold_hdr = load_fonts(26)

    line_h  = 36   # line height for regular text
    line_hb = 40   # line height for bold text

    # ── Estimate total height ──
    header_lines = 8           # name + 5 addr + phone + separator
    info_lines   = 4           # name, date+type, time+cashier+billno, sep
    item_lines   = len(ITEMS) + 3   # header + items + sep
    total_lines  = 4           # total qty/sub + sep + grand + sep + thanks
    est_height   = (header_lines + info_lines + item_lines + total_lines) * line_h + 200
    H = max(est_height, 600)

    img  = Image.new("RGB", (W, H), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    y    = 30

    # ── HEADER ──
    draw_text(draw, centered(RESTAURANT_NAME, font_bold_hdr, W), y, RESTAURANT_NAME, font_bold_hdr)
    y += line_hb + PAD

    for line in [ADDRESS_LINE1, ADDRESS_LINE2, ADDRESS_LINE3, ADDRESS_LINE4, ADDRESS_LINE5]:
        if line:
            draw_text(draw, centered(line, font_reg, W), y, line, font_reg)
            y += line_h

    draw_text(draw, centered(PHONE, font_reg, W), y, PHONE, font_reg)
    y += line_h + PAD

    y = draw_separator(draw, y, W, MARGIN) + PAD

    # ── CUSTOMER NAME ──
    name_label = f"Name: {CUSTOMER_NAME}"
    draw_text(draw, MARGIN, y, name_label, font_reg)
    y += line_h + PAD

    y = draw_separator(draw, y, W, MARGIN) + PAD

    # ── DATE / ORDER TYPE / TIME / CASHIER / BILL NO ──
    date_str   = f"Date: {DATE}"
    order_str  = ORDER_TYPE
    cashier_str = f"Cashier: {CASHIER}"
    bill_str   = f"Bill No.: {BILL_NO}"

    # Row 1: Date (left) | OrderType (bold, right)
    draw_text(draw, MARGIN, y, date_str, font_reg)
    draw_text(draw, W - MARGIN - measure(order_str, font_bold), y, order_str, font_bold)
    y += line_h

    # Row 2: Time (left)
    draw_text(draw, MARGIN, y, TIME, font_reg)
    y += line_h

    # Row 3: Cashier (left) | Bill No (right)
    draw_text(draw, MARGIN, y, cashier_str, font_reg)
    draw_text(draw, W - MARGIN - measure(bill_str, font_reg), y, bill_str, font_reg)
    y += line_h + PAD

    y = draw_separator(draw, y, W, MARGIN) + PAD

    # ── ITEMS TABLE HEADER ──
    col_item  = MARGIN
    col_qty   = W - MARGIN - 290
    col_price = W - MARGIN - 170
    col_amt   = W - MARGIN - 10

    draw_text(draw, col_item, y, "Item", font_reg)
    draw_text(draw, col_qty  - measure("Qty.", font_reg) // 2, y, "Qty.", font_reg)
    draw_text(draw, col_price - measure("Price", font_reg), y, "Price", font_reg)
    draw_text(draw, col_amt   - measure("Amount", font_reg), y, "Amount", font_reg)
    y += line_h

    y = draw_separator(draw, y, W, MARGIN) + PAD

    # ── ITEMS ──
    for name, qty, price in ITEMS:
        amount    = qty * price
        qty_str   = str(qty)
        price_str = f"{price:.2f}"
        amt_str   = f"{amount:.2f}"
        draw_text(draw, col_item, y, name, font_reg)
        draw_text(draw, col_qty   - measure(qty_str,   font_reg) // 2, y, qty_str,   font_reg)
        draw_text(draw, col_price - measure(price_str, font_reg),      y, price_str, font_reg)
        draw_text(draw, col_amt   - measure(amt_str,   font_reg),      y, amt_str,   font_reg)
        y += line_h

    y = draw_separator(draw, y, W, MARGIN) + PAD

    # ── TOTAL QTY / SUB TOTAL ──
    tq_str  = f"Total Qty: {total_qty}"
    sub_lbl = "Sub Total"
    sub_val = f"{sub_total:.2f}"
    draw_text(draw, MARGIN, y, tq_str, font_reg)
    draw_text(draw, col_price - measure(sub_lbl, font_reg), y, sub_lbl, font_reg)
    draw_text(draw, col_amt   - measure(sub_val, font_reg), y, sub_val, font_reg)
    y += line_h + PAD

    y = draw_separator(draw, y, W, MARGIN) + PAD

    # ── GRAND TOTAL ──
    grand_label = "Grand Total"
    grand_value = f"\u20b9{grand_total:.2f}"
    grand_str   = f"{grand_label}  {grand_value}"
    draw_text(draw, W - MARGIN - measure(grand_str, font_bold_lg), y, grand_label, font_bold_lg)
    # Draw value part in same line
    label_w = measure(grand_label + "  ", font_bold_lg)
    draw_text(draw, W - MARGIN - measure(grand_str, font_bold_lg) + label_w, y, grand_value, font_bold_lg)
    y += line_hb + PAD

    y = draw_separator(draw, y, W, MARGIN) + PAD

    # ── THANK YOU ──
    draw_text(draw, centered(THANK_YOU_MESSAGE, font_reg, W), y, THANK_YOU_MESSAGE, font_reg)
    y += line_h + 30

    # Crop to actual content height
    img = img.crop((0, 0, W, y))
    img.save(OUTPUT_FILE)
    print(f"✅  Invoice saved → {OUTPUT_FILE}  ({W}×{y} px)")


if __name__ == "__main__":
    generate_invoice()
