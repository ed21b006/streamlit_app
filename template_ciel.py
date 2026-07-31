"""
Invoice Generator - Template: CIEL
====================================
Based on: example_templates/ciel_invoice.jpg

Layout:
  - Restaurant name (centered)
  - Address (centered, 2 lines)
  - "TAX INVOICE" (centered)
  - "Table : X" (left, bold)
  - Dashed separator
  - BillNo (left) + Date (right)
  - Captain (left) + Cover (right)
  - Dashed separator
  - KOTs line (left)
  - Dashed separator
  - Items table: Description | Qty | Rate | Amount
      (long names wrap; qty/rate/amount always on the last wrapped line)
  - Dashed separator
  - Right-aligned tax block:
      Total :      xxx.xx
      SGST x% :   xxx.xx
      CGST x% :   xxx.xx
      Bill Total : xxx.xx
  - "============" separator (equals signs)
  - G.Total : xxx.xx  (bold, right aligned)
  - "============" separator
  - GST / FSSAI / Thank You  (left, small)

Output: ciel_invoice.png
"""

from PIL import Image, ImageDraw, ImageFont

# ─────────────────────────────────────────────
#  VARIABLES  — edit these before running
# ─────────────────────────────────────────────

RESTAURANT_NAME = "CIEL"
ADDRESS_LINE1   = "45, Teli Gali, Andheri (E)"
ADDRESS_LINE2   = "Mumbai- 400 069"

TABLE_NO        = "2-"            # shown as  "Table : 2-"

BILL_NO         = "F-4026"
DATE            = "06-Jul-2026"
TIME            = "22:51"         # appended to date → "06-Jul-2026 22:51"
CAPTAIN         = "Bapi"
COVER           = "8"

KOTS            = "41637, 41647"  # Kitchen Order Tokens; leave "" to hide row

# Menu items: list of (description, qty, rate)
# qty=0 means qty/rate/amount are hidden (e.g. no-charge garnish lines)
ITEMS = [
    ("MINERAL WATER",              1,  69.00),
    ("STIR FRY YAKI SOBA NO ODLE", 1, 339.00),
    ("MAMA ROSA PENNE",             1, 459.00),
]

# Tax rates (percent, applied on sub_total)
SGST_PERCENT = 2.5
CGST_PERCENT = 2.5

GST_NO   = "GST:27AAFCF5019C1ZZ"
FSSAI_NO = "FSSAI:11523005000296"
THANK_YOU = "Thank You !!"

OUTPUT_FILE = "ciel_invoice.png"

# ─────────────────────────────────────────────
#  INTERNAL CALCULATIONS (do not edit below)
# ─────────────────────────────────────────────

def compute_totals(items, sgst_pct, cgst_pct):
    import math
    sub_total  = sum(qty * rate for _, qty, rate in items if qty > 0)
    # Truncate (floor) to 2 decimal places — matches original receipt behavior
    sgst       = math.floor(sub_total * sgst_pct / 100 * 100) / 100
    cgst       = math.floor(sub_total * cgst_pct / 100 * 100) / 100
    bill_total = round(sub_total + sgst + cgst, 2)
    g_total    = bill_total
    return sub_total, sgst, cgst, bill_total, g_total


def load_fonts(base_size=26):
    reg_path  = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
    bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
    try:
        font_reg    = ImageFont.truetype(reg_path,  base_size)
        font_bold   = ImageFont.truetype(bold_path, base_size)
        font_bold_lg= ImageFont.truetype(bold_path, base_size + 8)
        font_sm     = ImageFont.truetype(reg_path,  base_size - 4)
    except OSError:
        font_reg = font_bold = font_bold_lg = font_sm = ImageFont.load_default()
    return font_reg, font_bold, font_bold_lg, font_sm


def draw_text(draw, x, y, text, font, fill=(20, 20, 20)):
    draw.text((x, y), text, font=font, fill=fill)


def measure(text, font):
    bbox = font.getbbox(text)
    return bbox[2] - bbox[0]


def centered(text, font, width):
    return (width - measure(text, font)) // 2


def wrap_text(text, font, max_width):
    """Word-wrap text to fit max_width. Returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        test = (cur + " " + word).strip()
        if measure(test, font) <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines or [""]


def draw_dashed_sep(draw, y, width, margin, color=(20, 20, 20)):
    seg, gap, x = 7, 5, margin
    while x < width - margin:
        draw.line([(x, y), (min(x + seg, width - margin), y)], fill=color, width=1)
        x += seg + gap
    return y + 1


def draw_equals_sep(draw, y, width, margin, color=(20, 20, 20)):
    """Draw a row of '=' characters as a separator."""
    seg, gap, x = 10, 3, margin
    while x < width - margin:
        draw.line([(x, y),     (min(x + seg, width - margin), y)], fill=color, width=2)
        draw.line([(x, y + 4), (min(x + seg, width - margin), y + 4)], fill=color, width=2)
        x += seg + gap
    return y + 5


def generate_invoice():
    sub_total, sgst, cgst, bill_total, g_total = compute_totals(
        ITEMS, SGST_PERCENT, CGST_PERCENT
    )

    W       = 720
    MARGIN  = 28
    PAD     = 10
    line_h  = 34
    line_hb = 40

    font_reg, font_bold, font_bold_lg, font_sm = load_fonts(26)

    est_h = 1200 + len(ITEMS) * line_h * 3
    img   = Image.new("RGB", (W, est_h), color=(255, 255, 255))
    draw  = ImageDraw.Draw(img)
    y     = 30

    # ── RESTAURANT HEADER ──
    draw_text(draw, centered(RESTAURANT_NAME, font_reg, W), y, RESTAURANT_NAME, font_reg)
    y += line_h

    for addr in [ADDRESS_LINE1, ADDRESS_LINE2]:
        if addr:
            draw_text(draw, centered(addr, font_reg, W), y, addr, font_reg)
            y += line_h

    tax_label = "TAX INVOICE"
    draw_text(draw, centered(tax_label, font_reg, W), y, tax_label, font_reg)
    y += line_h + PAD

    # ── TABLE NUMBER ──
    table_str = f"Table  : {TABLE_NO}"
    draw_text(draw, MARGIN, y, table_str, font_bold)
    y += line_hb + PAD // 2

    # ── BILL / DATE / CAPTAIN / COVER ──
    y = draw_dashed_sep(draw, y, W, MARGIN) + PAD

    bill_str    = f"BillNo : {BILL_NO}"
    date_str    = f"Date : {DATE} {TIME}"
    captain_str = f"Captain : {CAPTAIN}"
    cover_str   = f"Cover : {COVER}"

    draw_text(draw, MARGIN, y, bill_str, font_reg)
    draw_text(draw, W - MARGIN - measure(date_str, font_reg), y, date_str, font_reg)
    y += line_h

    draw_text(draw, MARGIN, y, captain_str, font_reg)
    draw_text(draw, W - MARGIN - measure(cover_str, font_reg), y, cover_str, font_reg)
    y += line_h + PAD

    # ── KOTs ──
    y = draw_dashed_sep(draw, y, W, MARGIN) + PAD

    if KOTS:
        kots_str = f"KOTs : {KOTS}"
        draw_text(draw, MARGIN, y, kots_str, font_reg)
        y += line_h + PAD

    # ── ITEMS TABLE ──
    y = draw_dashed_sep(draw, y, W, MARGIN) + PAD

    col_desc  = MARGIN
    col_qty   = W - MARGIN - 290
    col_rate  = W - MARGIN - 165
    col_amt   = W - MARGIN - 10

    # Table header
    draw_text(draw, col_desc, y, "Description", font_reg)
    draw_text(draw, col_qty  - measure("Qty", font_reg) // 2, y, "Qty",    font_reg)
    draw_text(draw, col_rate - measure("Rate", font_reg),     y, "Rate",   font_reg)
    draw_text(draw, col_amt  - measure("Amount", font_reg),   y, "Amount", font_reg)
    y += line_h

    y = draw_dashed_sep(draw, y, W, MARGIN) + PAD

    # Items
    max_desc_w = col_qty - col_desc - 12
    for name, qty, rate in ITEMS:
        amount    = qty * rate if qty > 0 else 0.0
        desc_lines = wrap_text(name, font_reg, max_desc_w)

        # Draw all wrapped description lines except the last
        for dl in desc_lines[:-1]:
            draw_text(draw, col_desc, y, dl, font_reg)
            y += line_h

        # On the last description line, also draw qty / rate / amount
        draw_text(draw, col_desc, y, desc_lines[-1], font_reg)
        if qty > 0:
            qty_str   = str(qty)
            rate_str  = f"{rate:.2f}"
            amt_str   = f"{amount:.2f}"
            draw_text(draw, col_qty  - measure(qty_str,  font_reg) // 2, y, qty_str,  font_reg)
            draw_text(draw, col_rate - measure(rate_str, font_reg),       y, rate_str, font_reg)
            draw_text(draw, col_amt  - measure(amt_str,  font_reg),       y, amt_str,  font_reg)
        y += line_h

    y += PAD // 2
    y = draw_dashed_sep(draw, y, W, MARGIN) + PAD

    # ── TAX BLOCK (right-aligned label : value pairs) ──
    def tax_row(label, value):
        nonlocal y
        val_str   = f"{value:.2f}"
        label_str = f"{label}"
        colon_str = f"{label_str}   {val_str}"
        # Draw label on left of the right block, value on far right
        lbl_x = col_rate - measure(label_str + " :", font_reg)
        draw_text(draw, lbl_x, y, label_str + " :", font_reg)
        draw_text(draw, col_amt - measure(val_str, font_reg), y, val_str, font_reg)
        y += line_h

    tax_row("Total",              sub_total)
    tax_row(f"SGST {SGST_PERCENT}%", sgst)
    tax_row(f"CGST {CGST_PERCENT}%", cgst)
    tax_row("Bill Total",         bill_total)

    y += PAD

    # ── EQUALS SEPARATOR ──
    y = draw_equals_sep(draw, y, W, MARGIN) + PAD + 4

    # ── G.TOTAL ──
    gt_label  = "G.Total : "
    gt_value  = f"{g_total:.2f}"
    gt_full   = gt_label + gt_value
    gt_x      = W - MARGIN - measure(gt_full, font_bold_lg)
    draw_text(draw, gt_x, y, gt_label, font_bold_lg)
    draw_text(draw, gt_x + measure(gt_label, font_bold_lg), y, gt_value, font_bold_lg)
    y += line_hb + PAD

    # ── EQUALS SEPARATOR ──
    y = draw_equals_sep(draw, y, W, MARGIN) + PAD + 8

    # ── FOOTER ──
    for footer_line in [GST_NO, FSSAI_NO, THANK_YOU]:
        if footer_line:
            draw_text(draw, MARGIN, y, footer_line, font_sm)
            y += line_h - 4

    y += 30

    img = img.crop((0, 0, W, y))
    img.save(OUTPUT_FILE)
    print(f"✅  Invoice saved → {OUTPUT_FILE}  ({W}×{y} px)")


if __name__ == "__main__":
    generate_invoice()
