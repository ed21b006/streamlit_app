"""
Invoice Generator - Template: AVIGNA LOKESH HOTELS PVT LTD
===========================================================
Based on: example_templates/v2/veerus-village-restaurant-makali-bangalore-north-indian-restaurants-fak95rb5uk.jpg

Layout:
  - Company name (bold, centered)
  - Address block (centered, multi-line)
  - GSTIN (centered)
  - Separator
  - Name: (label + customer name)
  - Separator
  - Date / Dine In count (left/right)
  - Time (left)
  - Cashier (left) | Bill No (right)
  - Token Nos (bold)
  - Separator
  - Item | Qty. | Price | Amount (table header)
  - Separator
  - Item rows
  - Separator
  - Total Qty / Sub Total (left/right on same row)
  - CGST X% (right)
  - SGST X% (right)
  - Separator (double/thick)
  - Grand Total ₹ (bold, right)
  - Separator
  - Thank you (centered)

Output: avigna_lokesh_invoice.png
"""

from PIL import Image, ImageDraw, ImageFont

# ─────────────────────────────────────────────
#  VARIABLES  — edit these before running
# ─────────────────────────────────────────────

COMPANY_NAME    = "Avigna lokesh Hotels Pvt Ltd"
ADDRESS_LINE1   = "11/1A, 1D Makali Tumkur Road"
ADDRESS_LINE2   = "Dasanapaura Hobli Next to Himalaya"
ADDRESS_LINE3   = "Drug Co., Bangalore North 562162"
GSTIN           = "GSTIN: 29AANCA9784F1ZY"

CUSTOMER_NAME   = ""                  # leave blank if not filled in
DATE            = "08/06/25"
DINE_IN         = "6"                 # number of covers / pax; or "Pick Up" etc.
TIME            = "20:34"
CASHIER         = "biller"
BILL_NO         = "34653"
TOKEN_NOS       = "139, 161, 166"     # comma-separated token numbers; leave blank to hide

# Menu items: list of (name, qty, unit_price)
ITEMS = [
    ("Mushroom Manchurian", 2, 200.00),
    ("Mushroom Kadai",      2, 200.00),
    ("Roti (plain)",        8,  35.00),
    ("Water",               2,  34.00),
    ("Chicken Biryani",     2, 230.00),
    ("Veg Biryani",         1, 160.00),
]

CGST_RATE       = 2.5                 # percentage
SGST_RATE       = 2.5                 # percentage

THANK_YOU_MSG   = "Thank you visit again!!!"

OUTPUT_FILE = "avigna_lokesh_invoice.png"

# ─────────────────────────────────────────────
#  INTERNAL CALCULATIONS (do not edit below)
# ─────────────────────────────────────────────

def compute_totals(items, cgst_rate, sgst_rate):
    sub_total   = sum(qty * price for _, qty, price in items)
    total_qty   = sum(qty for _, qty, _ in items)
    cgst_amt    = round(sub_total * cgst_rate / 100, 2)
    sgst_amt    = round(sub_total * sgst_rate / 100, 2)
    grand_total = round(sub_total + cgst_amt + sgst_amt, 2)
    return total_qty, sub_total, cgst_amt, sgst_amt, grand_total


def load_fonts(base_size=26):
    regular_path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
    bold_path    = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
    try:
        font_reg     = ImageFont.truetype(regular_path, base_size)
        font_bold    = ImageFont.truetype(bold_path,    base_size)
        font_bold_hdr = ImageFont.truetype(bold_path,  base_size + 4)
        font_bold_lg  = ImageFont.truetype(bold_path,  base_size + 6)
    except OSError:
        font_reg = font_bold = font_bold_hdr = font_bold_lg = ImageFont.load_default()
    return font_reg, font_bold, font_bold_hdr, font_bold_lg


def draw_text(draw, x, y, text, font, fill=(20, 20, 20)):
    draw.text((x, y), text, font=font, fill=fill)


def measure(text, font):
    bbox = font.getbbox(text)
    return bbox[2] - bbox[0]


def centered(text, font, width):
    return (width - measure(text, font)) // 2


def draw_separator(draw, y, width, margin, thick=False, color=(20, 20, 20)):
    w = 2 if thick else 1
    draw.line([(margin, y), (width - margin, y)], fill=color, width=w)
    return y + (3 if thick else 2)


def generate_invoice():
    total_qty, sub_total, cgst_amt, sgst_amt, grand_total = compute_totals(ITEMS, CGST_RATE, SGST_RATE)

    W      = 760
    MARGIN = 28
    PAD    = 10
    line_h = 36
    line_hb = 42

    font_reg, font_bold, font_bold_hdr, font_bold_lg = load_fonts(26)

    est_height = 900 + len(ITEMS) * line_h
    img  = Image.new("RGB", (W, est_height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    y    = 28

    # ── HEADER ──
    draw_text(draw, centered(COMPANY_NAME, font_bold_hdr, W), y, COMPANY_NAME, font_bold_hdr)
    y += line_hb + 4

    for line in [ADDRESS_LINE1, ADDRESS_LINE2, ADDRESS_LINE3]:
        if line:
            draw_text(draw, centered(line, font_reg, W), y, line, font_reg)
            y += line_h

    draw_text(draw, centered(GSTIN, font_reg, W), y, GSTIN, font_reg)
    y += line_h + PAD

    y = draw_separator(draw, y, W, MARGIN) + PAD

    # ── CUSTOMER NAME ──
    draw_text(draw, MARGIN, y, f"Name: {CUSTOMER_NAME}", font_reg)
    y += line_h + PAD

    y = draw_separator(draw, y, W, MARGIN) + PAD

    # ── DATE / DINE IN ──
    date_str  = f"Date: {DATE}"
    dine_str  = f"Dine In: {DINE_IN}"
    draw_text(draw, MARGIN, y, date_str, font_reg)
    draw_text(draw, W - MARGIN - measure(dine_str, font_bold), y, dine_str, font_bold)
    y += line_h

    # ── TIME ──
    draw_text(draw, MARGIN, y, TIME, font_reg)
    y += line_h

    # ── CASHIER / BILL NO ──
    cashier_str = f"Cashier: {CASHIER}"
    bill_str    = f"Bill No.: {BILL_NO}"
    draw_text(draw, MARGIN, y, cashier_str, font_reg)
    draw_text(draw, W - MARGIN - measure(bill_str, font_reg), y, bill_str, font_reg)
    y += line_h

    # ── TOKEN NOS ──
    if TOKEN_NOS:
        token_str = f"Token No.: {TOKEN_NOS}"
        draw_text(draw, MARGIN, y, token_str, font_bold)
        y += line_hb

    y += PAD
    y = draw_separator(draw, y, W, MARGIN) + PAD

    # ── ITEMS TABLE HEADER ──
    col_item  = MARGIN
    col_qty   = W - MARGIN - 280
    col_price = W - MARGIN - 160
    col_amount = W - MARGIN - 10

    draw_text(draw, col_item,                                      y, "Item",   font_reg)
    draw_text(draw, col_qty   - measure("Qty.",   font_reg)//2,    y, "Qty.",   font_reg)
    draw_text(draw, col_price - measure("Price",  font_reg)//2,    y, "Price",  font_reg)
    draw_text(draw, col_amount - measure("Amount", font_reg),      y, "Amount", font_reg)
    y += line_h

    y = draw_separator(draw, y, W, MARGIN) + PAD

    # ── ITEMS ──
    for name, qty, price in ITEMS:
        amount    = qty * price
        qty_str   = str(qty)
        price_str = f"{price:.2f}"
        amt_str   = f"{amount:.2f}"
        draw_text(draw, col_item,                                        y, name,      font_reg)
        draw_text(draw, col_qty   - measure(qty_str,   font_reg)//2,    y, qty_str,   font_reg)
        draw_text(draw, col_price - measure(price_str, font_reg)//2,    y, price_str, font_reg)
        draw_text(draw, col_amount - measure(amt_str,  font_reg),       y, amt_str,   font_reg)
        y += line_h

    y += PAD
    y = draw_separator(draw, y, W, MARGIN) + PAD

    right_val_x = W - MARGIN - 10

    # ── TOTAL QTY / SUB TOTAL (same row) ──
    tq_str  = f"Total Qty: {total_qty}"
    sub_lbl = "Sub"
    sub_val = f"{sub_total:.2f}"
    draw_text(draw, MARGIN, y, tq_str, font_reg)
    # "Sub\nTotal" stacked on right — simulate as "Sub Total" inline
    sub_combined = "Sub Total"
    draw_text(draw, right_val_x - measure(sub_val, font_reg) - measure(sub_combined + "  ", font_reg),
              y, sub_combined, font_reg)
    draw_text(draw, right_val_x - measure(sub_val, font_reg), y, sub_val, font_reg)
    y += line_h

    # ── CGST ──
    cgst_lbl = f"CGST {CGST_RATE}%"
    cgst_val = f"{cgst_amt:.2f}"
    draw_text(draw, right_val_x - measure(cgst_lbl + "  " + cgst_val, font_reg), y, cgst_lbl, font_reg)
    draw_text(draw, right_val_x - measure(cgst_val, font_reg), y, cgst_val, font_reg)
    y += line_h

    # ── SGST ──
    sgst_lbl = f"SGST {SGST_RATE}%"
    sgst_val = f"{sgst_amt:.2f}"
    draw_text(draw, right_val_x - measure(sgst_lbl + "  " + sgst_val, font_reg), y, sgst_lbl, font_reg)
    draw_text(draw, right_val_x - measure(sgst_val, font_reg), y, sgst_val, font_reg)
    y += line_h + PAD

    # ── THICK SEPARATOR before Grand Total ──
    y = draw_separator(draw, y, W, MARGIN, thick=True) + 4

    # ── GRAND TOTAL ──
    grand_label = "Grand Total"
    grand_value = f"\u20b9{grand_total:.2f}"
    full_str    = f"{grand_label}  {grand_value}"
    start_x     = W - MARGIN - measure(full_str, font_bold_lg)
    label_w     = measure(grand_label + "  ", font_bold_lg)
    draw_text(draw, start_x,            y, grand_label, font_bold_lg)
    draw_text(draw, start_x + label_w,  y, grand_value, font_bold_lg)
    y += line_hb + PAD

    y = draw_separator(draw, y, W, MARGIN, thick=True) + PAD

    # ── THANK YOU ──
    draw_text(draw, centered(THANK_YOU_MSG, font_reg, W), y, THANK_YOU_MSG, font_reg)
    y += line_h + 30

    img = img.crop((0, 0, W, y))
    img.save(OUTPUT_FILE)
    print(f"✅  Invoice saved → {OUTPUT_FILE}  ({W}×{y} px)")


if __name__ == "__main__":
    generate_invoice()
