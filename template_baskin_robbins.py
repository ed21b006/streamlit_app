"""
Invoice Generator - Template: BASKIN ROBBINS (Dotpe / Sachus style)
=====================================================================
Based on: example_templates/1000174924.jpg

Layout:
  - Restaurant name (centered)
  - Sub-outlet name (centered)
  - Address (centered, multi-line wrapped)
  - Phone / GSTIN / FSSAI (centered)
  - "Invoice" heading (centered)
  - Dashed separator
  - Customer name + Order ID (left)
  - Dashed separator
  - Invoice No / Item count / Date+Time / Role
  - Separator line
  - Items table (Name | Qty | Rate | Amount)
  - Dashed separator
  - Sub Total / CGST / SGST / Bill Total
  - Separator line
  - Bill Total (rounded) — large bold, right aligned
  - Separator line
  - Payment Summary / UPI / Balance
  - Separator line
  - Footer ad messages (centered)
  - Footer contact line (centered)
  - "Powered by www.dotpe.in" (centered, small)

Output: baskin_robbins_invoice.png
"""

from PIL import Image, ImageDraw, ImageFont
import math

# ─────────────────────────────────────────────
#  VARIABLES  — edit these before running
# ─────────────────────────────────────────────

RESTAURANT_NAME  = "Baskin Robbins"
OUTLET_NAME      = "Sachus - Whitefield"
ADDRESS_LINE1    = "No.3/3, Sterlingsuites,"
ADDRESS_LINE2    = "Whitefield Main Road,"
ADDRESS_LINE3    = "Bengaluru-560066, Karnataka"
PHONE            = "Phone No-7899569493"
GSTIN            = "GSTIN: 29AFC53514H1ZC"
FSSAI            = "FSSAI Reg no: 21223188000668"

CUSTOMER_NAME    = "KRISH"
ORDER_ID         = "JQ7HNJ3Q"

INVOICE_NO       = "2627-159-11765"
ITEM_COUNT_LABEL = "1 item (1 Qty)"    # e.g. "2 items (3 Qty)"
DATE             = "Jul 10 2026"
TIME             = "10:37 PM"
ROLE             = "Manager"           # e.g. "Manager", "Cashier"

# Menu items: list of (name, qty, rate)
# For long item names that wrap, just write them fully — the script wraps them.
ITEMS = [
    ("Butterscotch Ribbon Ice Cream (Small Scoop 62 gm)", 1, 72),
]

# Tax rates (percent, applied on sub_total)
CGST_PERCENT = 2.5
SGST_PERCENT = 2.5

PAYMENT_LABEL   = "Payment Summary"
PAYMENT_METHOD  = "UPI"
BALANCE         = 0.00

# Footer text blocks (each string is a separate centered paragraph)
FOOTER_MESSAGES = [
    "Scooping Happiness at Lower Prices Effective 22nd September 2025. Enjoy 100% Benefits of Reduced GST Rates.",
    "Your Next Ice Cream Could Be FREE! Join Our Rewards Program Today & Enjoy Free Treats On Every 5th Visit - Just Ask Our Store Staff To Sign You Up. T&C Apply!",
    "For product complaints or suggestions call +91 9167557729 or email us at careline@gravis sgroup.com",
]
POWERED_BY       = "Powered by www.dotpe.in"

OUTPUT_FILE = "baskin_robbins_invoice.png"

# ─────────────────────────────────────────────
#  INTERNAL CALCULATIONS (do not edit below)
# ─────────────────────────────────────────────

def compute_totals(items, cgst_pct, sgst_pct):
    sub_total  = sum(qty * rate for _, qty, rate in items)
    cgst       = round(sub_total * cgst_pct / 100, 2)
    sgst       = round(sub_total * sgst_pct / 100, 2)
    bill_total = sub_total + cgst + sgst
    bill_total_rounded = math.ceil(bill_total)
    return sub_total, cgst, sgst, bill_total, bill_total_rounded


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
    """Wrap text to fit within max_width, returning list of lines."""
    words  = text.split()
    lines  = []
    cur    = ""
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
    return lines


def draw_separator(draw, y, width, margin, dashed=False, thick=1, color=(20, 20, 20)):
    if dashed:
        seg, gap = 7, 5
        x = margin
        while x < width - margin:
            draw.line([(x, y), (min(x + seg, width - margin), y)], fill=color, width=thick)
            x += seg + gap
    else:
        draw.line([(margin, y), (width - margin, y)], fill=color, width=thick)
    return y + thick


def generate_invoice():
    sub_total, cgst, sgst, bill_total, bill_rounded = compute_totals(
        ITEMS, CGST_PERCENT, SGST_PERCENT
    )

    W       = 760
    MARGIN  = 30
    PAD     = 10
    line_h  = 34
    line_hb = 40

    font_reg, font_bold, font_bold_lg, font_sm = load_fonts(26)

    # Estimate height generously
    est_h = 1600 + len(ITEMS) * line_h * 3 + len(FOOTER_MESSAGES) * line_h * 5
    img   = Image.new("RGB", (W, est_h), color=(255, 255, 255))
    draw  = ImageDraw.Draw(img)
    y     = 30

    # ── RESTAURANT HEADER ──
    draw_text(draw, centered(RESTAURANT_NAME, font_reg, W), y, RESTAURANT_NAME, font_reg)
    y += line_h
    draw_text(draw, centered(OUTLET_NAME, font_reg, W), y, OUTLET_NAME, font_reg)
    y += line_h + PAD // 2

    for addr_line in [ADDRESS_LINE1, ADDRESS_LINE2, ADDRESS_LINE3]:
        if addr_line:
            draw_text(draw, centered(addr_line, font_reg, W), y, addr_line, font_reg)
            y += line_h

    y += PAD // 2
    for info_line in [PHONE, GSTIN, FSSAI]:
        draw_text(draw, centered(info_line, font_reg, W), y, info_line, font_reg)
        y += line_h

    y += PAD
    invoice_label = "Invoice"
    draw_text(draw, centered(invoice_label, font_reg, W), y, invoice_label, font_reg)
    y += line_h + PAD

    y = draw_separator(draw, y, W, MARGIN, dashed=True) + PAD

    # ── CUSTOMER INFO ──
    draw_text(draw, MARGIN, y, CUSTOMER_NAME, font_reg)
    y += line_h
    draw_text(draw, MARGIN, y, ORDER_ID, font_reg)
    y += line_h + PAD

    y = draw_separator(draw, y, W, MARGIN, dashed=True) + PAD

    # ── INVOICE META ──
    inv_str   = f"Invoice {INVOICE_NO}"
    count_str = ITEM_COUNT_LABEL
    draw_text(draw, MARGIN, y, inv_str, font_reg)
    draw_text(draw, W - MARGIN - measure(count_str, font_reg), y, count_str, font_reg)
    y += line_h

    date_str = f"{DATE} {TIME}"
    draw_text(draw, MARGIN, y, date_str, font_reg)
    draw_text(draw, W - MARGIN - measure(ROLE, font_reg), y, ROLE, font_reg)
    y += line_h + PAD

    # ── TABLE HEADER ──
    col_name  = MARGIN
    col_qty   = W - MARGIN - 290
    col_rate  = W - MARGIN - 160
    col_amt   = W - MARGIN - 10

    y = draw_separator(draw, y, W, MARGIN, dashed=False, thick=2) + PAD

    draw_text(draw, col_name, y, "Name", font_reg)
    draw_text(draw, col_qty,  y, "Qty", font_reg)
    draw_text(draw, col_rate - measure("Rate", font_reg), y, "Rate", font_reg)
    draw_text(draw, col_amt  - measure("Amount", font_reg), y, "Amount", font_reg)
    y += line_h

    y = draw_separator(draw, y, W, MARGIN, dashed=False, thick=2) + PAD

    # ── ITEMS ──
    max_name_w = col_qty - col_name - 10
    for name, qty, rate in ITEMS:
        amount    = qty * rate
        amt_str   = f"{amount:.2f}"
        rate_str  = str(rate)
        qty_str   = str(qty)

        name_lines = wrap_text(name, font_reg, max_name_w)
        for i, nl in enumerate(name_lines):
            draw_text(draw, col_name, y, nl, font_reg)
            if i == 0:
                # Only draw qty/rate/amount on the first line
                pass  # draw after all name lines
            y += line_h

        # draw qty/rate/amount below the name block
        draw_text(draw, col_qty,                                  y, qty_str,  font_reg)
        draw_text(draw, col_rate - measure(rate_str, font_reg),   y, rate_str, font_reg)
        draw_text(draw, col_amt  - measure(amt_str,  font_reg),   y, amt_str,  font_reg)
        y += line_h + PAD // 2

    y = draw_separator(draw, y, W, MARGIN, dashed=True) + PAD

    # ── TAX SUMMARY ──
    def right_pair(label, value_str):
        nonlocal y
        draw_text(draw, MARGIN, y, label, font_reg)
        draw_text(draw, W - MARGIN - measure(value_str, font_reg), y, value_str, font_reg)
        y += line_h

    right_pair("Sub Total", f"{sub_total:.2f}")
    right_pair(f"CGST {CGST_PERCENT}% on {sub_total:.2f}", f"{cgst:.2f}")
    right_pair(f"SGST {SGST_PERCENT}% on {sub_total:.2f}", f"{sgst:.2f}")
    right_pair("Bill Total", f"{bill_total:.2f}")

    y = draw_separator(draw, y, W, MARGIN, dashed=False, thick=2) + PAD

    # ── BILL TOTAL (ROUNDED) — large bold ──
    bt_label = "Bill Total (rounded)"
    bt_value = f"{bill_rounded:.2f}"
    draw_text(draw, MARGIN, y, bt_label, font_bold_lg)
    draw_text(draw, W - MARGIN - measure(bt_value, font_bold_lg), y, bt_value, font_bold_lg)
    y += line_hb + PAD

    y = draw_separator(draw, y, W, MARGIN, dashed=False, thick=2) + PAD

    # ── PAYMENT SUMMARY ──
    draw_text(draw, MARGIN, y, PAYMENT_LABEL, font_reg)
    draw_text(draw, W - MARGIN - measure(f"{bill_rounded:.2f}", font_reg), y, f"{bill_rounded:.2f}", font_reg)
    y += line_h

    draw_text(draw, MARGIN, y, PAYMENT_METHOD, font_reg)
    y += line_h

    balance_str = f"{BALANCE:.2f}"
    draw_text(draw, MARGIN, y, "Balance", font_reg)
    draw_text(draw, W - MARGIN - measure(balance_str, font_reg), y, balance_str, font_reg)
    y += line_h + PAD

    y = draw_separator(draw, y, W, MARGIN, dashed=False, thick=2) + PAD + 4

    # ── FOOTER MESSAGES ──
    max_footer_w = W - MARGIN * 2
    for msg in FOOTER_MESSAGES:
        wrapped = wrap_text(msg, font_sm, max_footer_w)
        for wl in wrapped:
            draw_text(draw, centered(wl, font_sm, W), y, wl, font_sm)
            y += line_h - 4
        y += PAD

    y += PAD
    draw_text(draw, centered(POWERED_BY, font_sm, W), y, POWERED_BY, font_sm)
    y += line_h + 30

    img = img.crop((0, 0, W, y))
    img.save(OUTPUT_FILE)
    print(f"✅  Invoice saved → {OUTPUT_FILE}  ({W}×{y} px)")


if __name__ == "__main__":
    generate_invoice()
