"""
Invoice Generator - Template: V&RO HOSPITALITY PVT LTD (Plan B)
=================================================================
Based on: example_templates/v2/images.jpeg

Layout:
  - Company name (bold, centered)
  - "PLAN B" (bold, centered)
  - "PLAN B" repeated (centered, sub-line)
  - Address (centered, multi-line)
  - GSTIN (centered)
  - Separator
  - Bill No | Stw: name | Date | Time
  - Table No | Covers
  - Separator
  - SNc | Description | Qty | Rate | Amount (table header)
  - Separator
  - Items rows (with support for sub-items at ₹0 rate)
  - Separator
  - Total Amount (right)
  - SERC @ X% (right)
  - State Gst @ X% (right)
  - Central Gst @ X% (right)
  - Round Off (right)
  - Net Amount (bold, right)
  - Separator
  - KOT NO / Total Items / User ID
  - Separator
  - Thank you (centered)

Output: vro_hospitality_invoice.png
"""

from PIL import Image, ImageDraw, ImageFont

# ─────────────────────────────────────────────
#  VARIABLES  — edit these before running
# ─────────────────────────────────────────────

COMPANY_NAME    = "V&RO HOSPITALITY PVT LTD"
OUTLET_NAME     = "PLAN B"
OUTLET_SUB      = "PLAN B"            # second line under outlet name
ADDRESS_LINE1   = "No 942, 21st Main Rd, Siddanna"
ADDRESS_LINE2   = "Layout,Banashankari"
ADDRESS_LINE3   = "Bengaluru - 560070"
GSTIN           = "GSTIN:29AAGCV4390M1ZL"

BILL_NO         = "2314PBSK/23-24"
STW_NAME        = "SUMIT"             # steward / server name
DATE            = "30-05-23"
TIME            = "15:19"
TABLE_NO        = "44"
COVERS          = "5"                 # number of guests

# Menu items: list of dicts with keys:
#   sno       (int or "")   – serial number; leave "" for sub-items
#   name      (str)         – item name
#   qty       (int or 0)    – quantity; 0 for sub-items (addon/modifier)
#   rate      (float or 0)  – rate; 0 for sub-items
#   amount    (float or 0)  – override amount; use 0 to auto-calculate (qty*rate)
#                             For sub-items set all to 0 and amount=0 → shows 0.00
ITEMS = [
    {"sno": 1, "name": "GINGER ALE",          "qty": 3, "rate": 130.00, "amount": 0},
    {"sno": 2, "name": "Brownie",              "qty": 2, "rate": 230.00, "amount": 0},
    {"sno": 3, "name": "Seasoned Fries",       "qty": 1, "rate": 270.00, "amount": 0},
    {"sno": 4, "name": "Tuesday 1 Dozer",      "qty": 1, "rate": 315.00, "amount": 0},
    # {"sno": "",  "name": "  NAKED PERI PERI",  "qty": 0, "rate": 0,      "amount": 0},
    # {"sno": 5, "name": "Tuesday 1/2 Doz",      "qty": 10, "rate": 225.00, "amount": 0},
    # {"sno": "",  "name": "  NAKED PERI PERI",  "qty": 0, "rate": 0,      "amount": 0},
    # {"sno": "",  "name": "  SPICY GARLIC",     "qty": 0, "rate": 0,      "amount": 0},
    # {"sno": "",  "name": "  FIRE CRACKER",     "qty": 0, "rate": 0,      "amount": 0},
    # {"sno": "",  "name": "  ABS",              "qty": 0, "rate": 0,      "amount": 0},
    # {"sno": "",  "name": "  FLAMING JALAPENO", "qty": 0, "rate": 0,      "amount": 0},
    # {"sno": "",  "name": "  FIRE CRACKER",     "qty": 0, "rate": 0,      "amount": 0},
    # {"sno": "",  "name": "  CREAMY BUFFALO",   "qty": 0, "rate": 0,      "amount": 0},
    # {"sno": "",  "name": "  HONEY CHILLI",     "qty": 0, "rate": 0,      "amount": 0},
    # {"sno": "",  "name": "  ABS",              "qty": 0, "rate": 0,      "amount": 0},
    # {"sno": 6, "name": "MANGOBLOOM*",          "qty": 1, "rate": 280.00, "amount": 0},
    # {"sno": 7, "name": "TEETOTTALERS",         "qty": 1, "rate": 280.00, "amount": 0},
    # {"sno": 8, "name": "ELECTRIC CURF",        "qty": 1, "rate": 280.00, "amount": 0},
]

SERC_RATE       = 10.0                # service charge %
STATE_GST_RATE  = 2.5                 # state GST %
CENTRAL_GST_RATE = 2.5               # central GST %

KOT_NOS         = "4797,4806,4834,4852"
USER_ID         = "SHASHI"
FOOTER_MSG      = "Thank You visit again"

OUTPUT_FILE = "vro_hospitality_invoice.png"

# ─────────────────────────────────────────────
#  INTERNAL CALCULATIONS (do not edit below)
# ─────────────────────────────────────────────

def compute_item_amount(item):
    if item["amount"]:
        return item["amount"]
    if item["qty"] and item["rate"]:
        return item["qty"] * item["rate"]
    return 0.0


def compute_totals(items, serc_rate, state_gst_rate, central_gst_rate):
    total_amount  = sum(compute_item_amount(it) for it in items)
    total_items   = sum(it["qty"] for it in items if it["qty"])
    serc_amt      = round(total_amount * serc_rate / 100, 2)
    state_gst_amt = round(total_amount * state_gst_rate / 100, 2)
    central_gst_amt = round(total_amount * central_gst_rate / 100, 2)
    raw_net       = total_amount + serc_amt + state_gst_amt + central_gst_amt
    net_amount    = round(raw_net, 2)
    round_off     = round(round(raw_net) - raw_net, 2)
    return total_amount, total_items, serc_amt, state_gst_amt, central_gst_amt, round_off, net_amount


def load_fonts(base_size=24):
    regular_path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
    bold_path    = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
    try:
        font_reg  = ImageFont.truetype(regular_path, base_size)
        font_bold = ImageFont.truetype(bold_path,    base_size)
        font_bold_hdr = ImageFont.truetype(bold_path, base_size + 4)
        font_bold_lg  = ImageFont.truetype(bold_path, base_size + 6)
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


def draw_separator(draw, y, width, margin, color=(20, 20, 20)):
    draw.line([(margin, y), (width - margin, y)], fill=color, width=1)
    return y + 2


def generate_invoice():
    total_amount, total_items, serc_amt, state_gst_amt, central_gst_amt, round_off, net_amount = \
        compute_totals(ITEMS, SERC_RATE, STATE_GST_RATE, CENTRAL_GST_RATE)

    W      = 900
    MARGIN = 24
    PAD    = 8
    line_h = 32
    line_hb = 38

    font_reg, font_bold, font_bold_hdr, font_bold_lg = load_fonts(22)

    est_height = 900 + len(ITEMS) * line_h
    img  = Image.new("RGB", (W, est_height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    y    = 24

    # ── HEADER ──
    draw_text(draw, centered(COMPANY_NAME, font_bold_hdr, W), y, COMPANY_NAME, font_bold_hdr)
    y += line_hb + 4

    draw_text(draw, centered(OUTLET_NAME, font_bold, W), y, OUTLET_NAME, font_bold)
    y += line_hb

    draw_text(draw, centered(OUTLET_SUB, font_reg, W), y, OUTLET_SUB, font_reg)
    y += line_h

    for line in [ADDRESS_LINE1, ADDRESS_LINE2, ADDRESS_LINE3]:
        if line:
            draw_text(draw, centered(line, font_reg, W), y, line, font_reg)
            y += line_h

    draw_text(draw, centered(GSTIN, font_reg, W), y, GSTIN, font_reg)
    y += line_h + PAD

    y = draw_separator(draw, y, W, MARGIN) + PAD

    # ── BILL INFO ──
    bill_str  = f"Bill No: {BILL_NO}"
    stw_str   = f"Stw: {STW_NAME}"
    date_str  = f"Date: {DATE}"
    time_str  = f"Time: {TIME}"

    draw_text(draw, MARGIN, y, bill_str, font_reg)
    draw_text(draw, W - MARGIN - measure(date_str + "  " + time_str, font_reg), y, date_str, font_reg)
    draw_text(draw, W - MARGIN - measure(time_str, font_reg), y, time_str, font_reg)
    y += line_h

    table_str  = f"Table No {TABLE_NO}"
    covers_str = f"Covers: {COVERS}"
    draw_text(draw, MARGIN, y, stw_str, font_reg)
    # draw_text(draw, W - MARGIN - measure(covers_str, font_reg), y, covers_str, font_reg)
    y += line_h

    draw_text(draw, MARGIN, y, table_str, font_reg)
    y += line_h + PAD

    y = draw_separator(draw, y, W, MARGIN) + PAD

    # ── ITEMS TABLE HEADER ──
    col_sno    = MARGIN
    col_desc   = MARGIN + 52
    col_qty    = W - MARGIN - 280
    col_rate   = W - MARGIN - 160
    col_amount = W - MARGIN - 10

    draw_text(draw, col_sno,   y, "SNc", font_reg)
    draw_text(draw, col_desc,  y, "Description", font_reg)
    draw_text(draw, col_qty    - measure("Qty",    font_reg)//2, y, "Qty",    font_reg)
    draw_text(draw, col_rate   - measure("Rate",   font_reg)//2, y, "Rate",   font_reg)
    draw_text(draw, col_amount - measure("Amount", font_reg),    y, "Amount", font_reg)
    y += line_h

    y = draw_separator(draw, y, W, MARGIN) + PAD

    # ── ITEMS ──
    for it in ITEMS:
        sno    = str(it["sno"]) if it["sno"] != "" else ""
        name   = it["name"]
        qty    = it["qty"]
        rate   = it["rate"]
        amount = compute_item_amount(it)

        qty_str  = str(qty) if qty else ""
        rate_str = f"{rate:.2f}" if rate else ""
        amt_str  = f"{amount:.2f}"

        draw_text(draw, col_sno,  y, sno,  font_reg)
        draw_text(draw, col_desc, y, name, font_reg)
        if qty_str:
            draw_text(draw, col_qty - measure(qty_str, font_reg)//2, y, qty_str, font_reg)
        if rate_str:
            draw_text(draw, col_rate - measure(rate_str, font_reg)//2, y, rate_str, font_reg)
        draw_text(draw, col_amount - measure(amt_str, font_reg), y, amt_str, font_reg)
        y += line_h

    y += PAD
    y = draw_separator(draw, y, W, MARGIN) + PAD

    right_val_x = W - MARGIN - 10

    def draw_right_row(label, value_str, fnt=font_reg):
        nonlocal y
        draw_text(draw, W - MARGIN - measure(label + "  " + value_str, fnt), y, label, fnt)
        draw_text(draw, right_val_x - measure(value_str, fnt), y, value_str, fnt)
        y += line_h

    # ── TOTALS ──
    draw_right_row("Total Amount", f"{total_amount:.2f}")
    draw_right_row(f"SERC @ {SERC_RATE}%", f"{serc_amt:.2f}")
    draw_right_row(f"State Gst @ {STATE_GST_RATE}%", f"{state_gst_amt:.2f}")
    draw_right_row(f"Central Gst @ {CENTRAL_GST_RATE}%", f"{central_gst_amt:.2f}")
    draw_right_row("Round Off", f"{round_off:.2f}")

    net_str = f"{net_amount:.2f}"
    net_lbl = "Net Amount"
    draw_text(draw, right_val_x - measure(net_lbl + "    " + net_str, font_bold), y, net_lbl, font_bold)
    draw_text(draw, right_val_x - measure(net_str, font_bold_lg), y, net_str, font_bold_lg)
    y += line_hb + PAD

    y = draw_separator(draw, y, W, MARGIN) + PAD

    # ── KOT / TOTAL ITEMS / USER ID ──
    draw_text(draw, MARGIN, y, f"KOT NO : {KOT_NOS}", font_reg)
    y += line_h

    draw_text(draw, MARGIN, y, f"Total Items : {total_items}", font_reg)
    y += line_h

    draw_text(draw, MARGIN, y, f"User ID : {USER_ID}", font_reg)
    y += line_h + PAD

    y = draw_separator(draw, y, W, MARGIN) + PAD

    # ── FOOTER ──
    draw_text(draw, centered(FOOTER_MSG, font_reg, W), y, FOOTER_MSG, font_reg)
    y += line_h + 20

    img = img.crop((0, 0, W, y))
    img.save(OUTPUT_FILE)
    print(f"✅  Invoice saved → {OUTPUT_FILE}  ({W}×{y} px)")


if __name__ == "__main__":
    generate_invoice()
