"""
Invoice Generator - Template: FRUIT N ME
=========================================
Based on: example_templates/1000174485.jpg

Layout:
  - Restaurant name (bold, centered)
  - Address / location (centered)
  - Phone (centered)
  - Dashed separator
  - Date / Order type (Dine In: table no or Pick Up)
  - Time
  - Cashier / Bill No
  - Token No (bold)
  - Dashed separator
  - Items table (Item | Qty | Price | Amount)
  - Dashed separator
  - Total Qty / Sub Total
  - Dashed separator
  - Grand Total (bold, right aligned)
  - Payment method line
  - Dashed separator
  - Thanks message (centered)

Output: fruit_n_me_invoice.png
"""

from PIL import Image, ImageDraw, ImageFont

# ─────────────────────────────────────────────
#  VARIABLES  — edit these before running
# ─────────────────────────────────────────────

RESTAURANT_NAME = "FRUIT N ME"
ADDRESS_LINE1   = "FOOD COURT,ITPL,"
ADDRESS_LINE2   = "Whitefield Bangalore"
PHONE           = "Phone : 9886863647"

DATE            = "08/07/26"
ORDER_TYPE      = "Dine In: SS"   # e.g. "Dine In: SS" or "Pick Up"
TIME            = "14:20"
CASHIER         = "biller"
BILL_NO         = "20719"
TOKEN_NO        = "68"            # leave blank "" to hide Token No row

# Menu items: list of (name, qty, unit_price)
ITEMS = []

PAYMENT_METHOD  = "Paid via Other [UPI]"   # leave blank to hide
THANKS_MESSAGE  = "Thanks visit us again."

OUTPUT_FILE = "fruit_n_me_invoice.png"

# ─────────────────────────────────────────────
#  INTERNAL CALCULATIONS (do not edit below)
# ─────────────────────────────────────────────

def compute_totals(items):
    sub_total  = sum(qty * price for _, qty, price in items)
    total_qty  = sum(qty for _, qty, _ in items)
    return total_qty, sub_total, sub_total   # grand = subtotal (no tax)


def load_fonts(base_size=28):
    regular_path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
    bold_path    = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
    try:
        font_reg     = ImageFont.truetype(regular_path, base_size)
        font_bold    = ImageFont.truetype(bold_path,    base_size)
        font_bold_lg = ImageFont.truetype(bold_path,    base_size + 6)
        font_bold_hdr= ImageFont.truetype(bold_path,    base_size + 4)
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


def draw_separator(draw, y, width, margin, dashed=True, color=(20, 20, 20)):
    if dashed:
        seg, gap = 6, 4
        x = margin
        while x < width - margin:
            draw.line([(x, y), (min(x + seg, width - margin), y)], fill=color, width=1)
            x += seg + gap
    else:
        draw.line([(margin, y), (width - margin, y)], fill=color, width=2)
    return y + 2


def generate_invoice():
    total_qty, sub_total, grand_total = compute_totals(ITEMS)

    W       = 760
    MARGIN  = 28
    PAD     = 10
    line_h  = 36
    line_hb = 40

    font_reg, font_bold, font_bold_lg, font_bold_hdr = load_fonts(26)

    est_height = 800 + len(ITEMS) * line_h
    img  = Image.new("RGB", (W, est_height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    y    = 30

    # ── HEADER ──
    draw_text(draw, centered(RESTAURANT_NAME, font_bold_hdr, W), y, RESTAURANT_NAME, font_bold_hdr)
    y += line_hb + PAD

    for line in [ADDRESS_LINE1, ADDRESS_LINE2]:
        if line:
            draw_text(draw, centered(line, font_reg, W), y, line, font_reg)
            y += line_h

    draw_text(draw, centered(PHONE, font_reg, W), y, PHONE, font_reg)
    y += line_h + PAD

    y = draw_separator(draw, y, W, MARGIN, dashed=True) + PAD

    # ── META INFO ──
    # Row 1: Date | Order Type
    draw_text(draw, MARGIN, y, f"Date: {DATE}", font_reg)
    draw_text(draw, W - MARGIN - measure(ORDER_TYPE, font_bold), y, ORDER_TYPE, font_bold)
    y += line_h

    # Row 2: Time
    draw_text(draw, MARGIN, y, TIME, font_reg)
    y += line_h

    # Row 3: Cashier | Bill No
    cashier_str = f"Cashier: {CASHIER}"
    bill_str    = f"Bill No.: {BILL_NO}"
    draw_text(draw, MARGIN, y, cashier_str, font_reg)
    draw_text(draw, W - MARGIN - measure(bill_str, font_reg), y, bill_str, font_reg)
    y += line_h

    # Row 4: Token No (bold) — optional
    if TOKEN_NO:
        token_str = f"Token No.: {TOKEN_NO}"
        draw_text(draw, MARGIN, y, token_str, font_bold)
        y += line_hb

    y += PAD
    y = draw_separator(draw, y, W, MARGIN, dashed=True) + PAD

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

    y = draw_separator(draw, y, W, MARGIN, dashed=True) + PAD

    # ── ITEMS ──
    for name, qty, price in ITEMS:
        amount    = qty * price
        qty_str   = str(qty)
        price_str = f"{price:.2f}"
        amt_str   = f"{amount:.2f}"
        draw_text(draw, col_item,                                  y, name,      font_reg)
        draw_text(draw, col_qty   - measure(qty_str,   font_reg) // 2, y, qty_str,   font_reg)
        draw_text(draw, col_price - measure(price_str, font_reg),  y, price_str, font_reg)
        draw_text(draw, col_amt   - measure(amt_str,   font_reg),  y, amt_str,   font_reg)
        y += line_h

    y = draw_separator(draw, y, W, MARGIN, dashed=True) + PAD

    # ── TOTAL QTY / SUB TOTAL ──
    tq_str  = f"Total Qty: {total_qty}"
    sub_lbl = "Sub Total"
    sub_val = f"{sub_total:.2f}"
    draw_text(draw, MARGIN, y, tq_str, font_reg)
    draw_text(draw, col_price - measure(sub_lbl, font_reg), y, sub_lbl, font_reg)
    draw_text(draw, col_amt   - measure(sub_val, font_reg), y, sub_val, font_reg)
    y += line_h + PAD

    y = draw_separator(draw, y, W, MARGIN, dashed=True) + PAD

    # ── GRAND TOTAL ──
    grand_value = f"\u20b9{grand_total:.2f}"
    grand_label = "Grand Total"
    label_w     = measure(grand_label + "  ", font_bold_lg)
    full_w      = measure(grand_label + "  " + grand_value, font_bold_lg)
    start_x     = W - MARGIN - full_w
    draw_text(draw, start_x,            y, grand_label, font_bold_lg)
    draw_text(draw, start_x + label_w,  y, grand_value, font_bold_lg)
    y += line_hb + PAD

    # ── PAYMENT METHOD ──
    if PAYMENT_METHOD:
        draw_text(draw, MARGIN, y, PAYMENT_METHOD, font_reg)
        y += line_h + PAD

    y = draw_separator(draw, y, W, MARGIN, dashed=True) + PAD

    # ── THANKS ──
    draw_text(draw, centered(THANKS_MESSAGE, font_reg, W), y, THANKS_MESSAGE, font_reg)
    y += line_h + 30

    img = img.crop((0, 0, W, y))
    img.save(OUTPUT_FILE)
    print(f"✅  Invoice saved → {OUTPUT_FILE}  ({W}×{y} px)")


if __name__ == "__main__":
    generate_invoice()
