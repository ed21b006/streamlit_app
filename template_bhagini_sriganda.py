"""
Invoice Generator - Template: BHAGINI (Sriganda Palace)
=========================================================
Based on: example_templates/v2/1.jpg

Layout:
  - Brand logo text "Bhagini" (bold, centered, with leaf accent)
  - Restaurant name (centered)
  - Full address (centered, multi-line)
  - GST No (centered)
  - Dashed separator with "RECEIPT" label
  - Name (left) | Invoice No (right)
  - Table (left) | Date (right)
  - Solid separator
  - Items table header: Item | Price | Qty | Total
  - Solid separator
  - Item rows
  - Solid separator
  - Sub-Total (right)
  - CGST 2.5% (right)
  - SGST 2.5% (right)
  - Dashed separator
  - Mode: Cash (left) | Total: ₹ (right)
  - Solid separator
  - Footer: **SAVE PAPER SAVE NATURE !!** (centered, bold)
  - Time (centered)
  - Solid separator

Output: bhagini_sriganda_invoice.png
"""

from PIL import Image, ImageDraw, ImageFont

# ─────────────────────────────────────────────
#  VARIABLES  — edit these before running
# ─────────────────────────────────────────────

BRAND_NAME      = "Bhagini"           # large brand name at very top
RESTAURANT_NAME = "Sriganda Palace"
ADDRESS_LINE1   = "Service Rd, T K Reddy Layout,"
ADDRESS_LINE2   = "Annaiah Reddy Layout, Banaswadi,"
ADDRESS_LINE3   = "Bengaluru, Karnataka 560043"
GST_NO          = "GST No 29ADDPR8125K1Z2"

CUSTOMER_NAME   = "Siva Shankar"
INVOICE_NO      = "7767"
TABLE_NO        = "#37"
DATE            = "16 May 2024"       # e.g. "16 May 2024"

# Menu items: list of (name, unit_price, qty)
ITEMS = [
    ("Mutton biriyani", 400, 4),
    ("Tandoori Roti",    30, 5),
    ("Chilly chicken",  250, 2),
    ("Chicken pepper",  250, 3),
]

CGST_RATE       = 2.5                 # percentage
SGST_RATE       = 2.5                 # percentage
PAYMENT_MODE    = "Cash"              # "Cash" / "UPI" / "Card" etc.
TIME            = "21:18"

FOOTER_MSG      = "**SAVE PAPER SAVE NATURE !!"

OUTPUT_FILE = "bhagini_sriganda_invoice.png"

# ─────────────────────────────────────────────
#  INTERNAL CALCULATIONS (do not edit below)
# ─────────────────────────────────────────────

def compute_totals(items, cgst_rate, sgst_rate):
    sub_total  = sum(price * qty for _, price, qty in items)
    cgst_amt   = round(sub_total * cgst_rate / 100)
    sgst_amt   = round(sub_total * sgst_rate / 100)
    grand_total = sub_total + cgst_amt + sgst_amt
    return sub_total, cgst_amt, sgst_amt, grand_total


def load_fonts(base_size=26):
    regular_path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
    bold_path    = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
    try:
        font_reg      = ImageFont.truetype(regular_path, base_size)
        font_bold     = ImageFont.truetype(bold_path,    base_size)
        font_brand    = ImageFont.truetype(bold_path,    base_size + 12)
        font_bold_hdr = ImageFont.truetype(bold_path,    base_size + 2)
        font_bold_lg  = ImageFont.truetype(bold_path,    base_size + 4)
    except OSError:
        font_reg = font_bold = font_brand = font_bold_hdr = font_bold_lg = ImageFont.load_default()
    return font_reg, font_bold, font_brand, font_bold_hdr, font_bold_lg


def draw_text(draw, x, y, text, font, fill=(20, 20, 20)):
    draw.text((x, y), text, font=font, fill=fill)


def measure(text, font):
    bbox = font.getbbox(text)
    return bbox[2] - bbox[0]


def centered(text, font, width):
    return (width - measure(text, font)) // 2


def draw_dashed_separator(draw, y, width, margin, label="", font=None, color=(20, 20, 20)):
    """Draw a dashed separator, optionally with a centered label."""
    if label and font:
        label_w  = measure(label, font)
        side_len = (width - 2 * margin - label_w - 8) // 2
        # left dashes
        seg, gap, x = 6, 4, margin
        while x < margin + side_len:
            draw.line([(x, y + 7), (min(x + seg, margin + side_len), y + 7)], fill=color, width=1)
            x += seg + gap
        # label
        draw.text((margin + side_len + 4, y), label, font=font, fill=color)
        # right dashes
        x = margin + side_len + label_w + 8
        while x < width - margin:
            draw.line([(x, y + 7), (min(x + seg, width - margin), y + 7)], fill=color, width=1)
            x += seg + gap
        return y + 22
    else:
        seg, gap, x = 6, 4, margin
        while x < width - margin:
            draw.line([(x, y), (min(x + seg, width - margin), y)], fill=color, width=1)
            x += seg + gap
        return y + 2


def draw_solid_separator(draw, y, width, margin, color=(20, 20, 20)):
    draw.line([(margin, y), (width - margin, y)], fill=color, width=1)
    return y + 2


def generate_invoice():
    sub_total, cgst_amt, sgst_amt, grand_total = compute_totals(ITEMS, CGST_RATE, SGST_RATE)

    W      = 780
    MARGIN = 28
    PAD    = 10
    line_h = 36
    line_hb = 42

    font_reg, font_bold, font_brand, font_bold_hdr, font_bold_lg = load_fonts(26)

    est_height = 900 + len(ITEMS) * line_h
    img  = Image.new("RGB", (W, est_height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    y    = 28

    # ── BRAND NAME ──
    draw_text(draw, centered(BRAND_NAME, font_brand, W), y, BRAND_NAME, font_brand)
    y += line_hb + 4

    # ── RESTAURANT NAME ──
    draw_text(draw, centered(RESTAURANT_NAME, font_bold_hdr, W), y, RESTAURANT_NAME, font_bold_hdr)
    y += line_hb

    # ── ADDRESS ──
    for line in [ADDRESS_LINE1, ADDRESS_LINE2, ADDRESS_LINE3]:
        if line:
            draw_text(draw, centered(line, font_reg, W), y, line, font_reg)
            y += line_h

    # ── GST NO ──
    draw_text(draw, centered(GST_NO, font_reg, W), y, GST_NO, font_reg)
    y += line_h + PAD

    # ── DASHED RECEIPT SEPARATOR ──
    y = draw_dashed_separator(draw, y, W, MARGIN, label="RECEIPT", font=font_reg) + PAD

    # ── NAME / INVOICE NO ──
    name_str    = f"Name: {CUSTOMER_NAME}"
    invoice_str = f"Invoice No: {INVOICE_NO}"
    draw_text(draw, MARGIN, y, name_str, font_reg)
    draw_text(draw, W - MARGIN - measure(invoice_str, font_reg), y, invoice_str, font_reg)
    y += line_h

    # ── TABLE / DATE ──
    table_str = f"Table: {TABLE_NO}"
    date_str  = f"Date: {DATE}"
    draw_text(draw, MARGIN, y, table_str, font_reg)
    draw_text(draw, W - MARGIN - measure(date_str, font_reg), y, date_str, font_reg)
    y += line_h + PAD

    # ── SOLID SEPARATOR ──
    y = draw_solid_separator(draw, y, W, MARGIN) + PAD

    # ── ITEMS TABLE HEADER ──
    col_item  = MARGIN
    col_price = MARGIN + 340
    col_qty   = W - MARGIN - 160
    col_total = W - MARGIN - 10

    draw_text(draw, col_item,                                  y, "Item",  font_reg)
    draw_text(draw, col_price - measure("Price", font_reg)//2, y, "Price", font_reg)
    draw_text(draw, col_qty   - measure("Qty",   font_reg)//2, y, "Qty",   font_reg)
    draw_text(draw, col_total - measure("Total", font_reg),    y, "Total", font_reg)
    y += line_h

    # ── SOLID SEPARATOR ──
    y = draw_solid_separator(draw, y, W, MARGIN) + PAD

    # ── ITEMS ──
    for name, price, qty in ITEMS:
        total_item = price * qty
        price_str  = f"\u20b9{price}"
        qty_str    = str(qty)
        total_str  = f"\u20b9{total_item}"
        draw_text(draw, col_item,                                        y, name,       font_reg)
        draw_text(draw, col_price - measure(price_str, font_reg)//2,     y, price_str,  font_reg)
        draw_text(draw, col_qty   - measure(qty_str,   font_reg)//2,     y, qty_str,    font_reg)
        draw_text(draw, col_total - measure(total_str, font_reg),        y, total_str,  font_reg)
        y += line_h

    # ── SOLID SEPARATOR ──
    y = draw_solid_separator(draw, y, W, MARGIN) + PAD

    # ── SUB-TOTAL / CGST / SGST ──
    right_label_x = W - MARGIN - 310
    right_val_x   = W - MARGIN - 10

    sub_str  = f"\u20b9 {sub_total}"
    cgst_str = f"  {CGST_RATE}%   \u20b9 {cgst_amt}"
    sgst_str = f"  {SGST_RATE}%   \u20b9 {sgst_amt}"

    draw_text(draw, right_label_x, y, "Sub-Total:",  font_reg)
    draw_text(draw, right_val_x - measure(sub_str, font_reg), y, sub_str, font_reg)
    y += line_h

    draw_text(draw, right_label_x, y, "CGST:",       font_reg)
    draw_text(draw, right_val_x - measure(cgst_str, font_reg), y, cgst_str, font_reg)
    y += line_h

    draw_text(draw, right_label_x, y, "SGST:",       font_reg)
    draw_text(draw, right_val_x - measure(sgst_str, font_reg), y, sgst_str, font_reg)
    y += line_h + PAD

    # ── DASHED SEPARATOR ──
    y = draw_dashed_separator(draw, y, W, MARGIN) + PAD

    # ── MODE / TOTAL ──
    mode_str  = f"Mode: {PAYMENT_MODE}"
    draw_text(draw, MARGIN, y, mode_str, font_reg)
    total_label = "Total: \u20b9"
    total_val   = str(grand_total)
    full_total  = total_label + total_val
    draw_text(draw, W - MARGIN - measure(full_total, font_bold), y, total_label, font_bold)
    draw_text(draw, W - MARGIN - measure(total_val, font_bold), y, total_val, font_bold)
    y += line_h + PAD

    # ── SOLID SEPARATOR ──
    y = draw_solid_separator(draw, y, W, MARGIN) + PAD

    # ── FOOTER ──
    draw_text(draw, centered(FOOTER_MSG, font_bold, W), y, FOOTER_MSG, font_bold)
    y += line_h

    time_str = f"Time: {TIME}"
    draw_text(draw, centered(time_str, font_reg, W), y, time_str, font_reg)
    y += line_h + PAD

    # ── FINAL SEPARATOR ──
    y = draw_solid_separator(draw, y, W, MARGIN) + PAD + 20

    img = img.crop((0, 0, W, y))
    img.save(OUTPUT_FILE)
    print(f"✅  Invoice saved → {OUTPUT_FILE}  ({W}×{y} px)")


if __name__ == "__main__":
    generate_invoice()
