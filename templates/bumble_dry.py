"""
Invoice Generator - Template: BUMBLE DRY (Laundry Service)
============================================================
A4-format laundry invoice with professional styling.

Layout (Page 1):
  - Header: Logo + Company info + Invoice pill + Invoice No + Dates
  - Bill To: Customer name + Contact
  - Items Table: Item | Price | Quantity | Total
  - Lower Section: Thank-you card + Price details card
    (Expected Value, Sub Total, GST 18%, Net Amount, Amount Paid, Balance)
  - Footer

Layout (Page 2):
  - Header (same)
  - Terms & Conditions
  - Footer

Output: bumble_dry_invoice.png
"""

import os
import base64

# ─────────────────────────────────────────────
#  VARIABLES  — edit these before running
# ─────────────────────────────────────────────

COMPANY_NAME     = "Bumble Dry"
COMPANY_LOCATION = "Bangalore"
COMPANY_PHONE    = "9731830308"
COMPANY_GST      = "29ABCFK4241J1Z8"

INVOICE_NO       = "SAR0001721"
ORDER_DATE       = "Jul 11, 2026"
DUE_DATE         = "Jul 12, 2026"

CUSTOMER_NAME    = "Aditya Raj"
CUSTOMER_PHONE   = "7547832355"

# Items: list of (description, sub_description, unit_price, quantity_str, total)
# quantity_str can be like "3.4 pieces" or "2 kg" etc.
ITEMS = [
    ("Wash & Iron (Mixedwash | Laundry)", "(15 Clothes)", 159.00, "3.4 pieces", 540.60),
]

GST_RATE         = 18.0   # GST percentage (applied on sub-total to verify net)
AMOUNT_PAID      = 0.00

# Terms & Conditions lines
TERMS = [
    "Order Terms : All orders are subject to Bumbledry terms and conditions.",
    "No refunds will be done under any circumstances.",
    "Fabric Care & Liability : Bumbledry ensures the highest standard of fabric care; however, refunds are not provided under any circumstances.",
    "All garments/linen/fabrics are handled with greatest care but owing to the conditions of the articles or non apparent/non-visible defects in its material there is a POSSIBILITY OF DISCOLOURING OR SHRINKAGE, DAMAGE. Such garments are accepted for cleaning at OWNER'S RISK and company will not accept any responsibility for it.",
    "All jurisdiction under Bangalore High Court only.",
    "Customers must disclose at the time of placing or picking up if any item is premium/expensive and requires special care; failure to do so will release BumbleDry from liability for any damage caused.",
]

OUTPUT_FILE = "bumble_dry_invoice.html"

# ─────────────────────────────────────────────
#  INTERNAL CALCULATIONS
# ─────────────────────────────────────────────

def compute_totals(items, gst_rate, amount_paid=0.0):
    """Compute GST breakdown from items.
    
    Expected/Net amount = sum of item totals
    Sub Total = Net Amount / (1 + gst_rate/100)  (i.e. GST-exclusive base)
    GST = Net Amount - Sub Total
    Balance = Net Amount - Amount Paid
    """
    net_amount = sum(item[4] for item in items)  # sum of total column
    sub_total = round(net_amount / (1 + gst_rate / 100), 2)
    gst_amount = round(net_amount - sub_total, 2)
    balance = round(net_amount - amount_paid, 2)
    return net_amount, sub_total, gst_amount, balance


def generate_invoice():
    """Generate the Bumble Dry invoice as a PNG using Playwright to render HTML."""
    from playwright.sync_api import sync_playwright

    net_amount, sub_total, gst_amount, balance = compute_totals(ITEMS, GST_RATE, AMOUNT_PAID)

    # Get logo as base64
    app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logo_path = os.path.join(app_dir, "logo.png")
    logo_b64 = ""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()

    # Build items HTML
    items_html = ""
    for item in ITEMS:
        desc, sub_desc, price, qty_str, total = item
        items_html += f"""
        <div class="item-row">
            <div class="item-main">
                {desc}<br>
                <span class="item-sub">{sub_desc}</span>
            </div>
            <div class="item-cell">Rs.{price:.2f}</div>
            <div class="item-cell">{qty_str}</div>
            <div class="item-cell">Rs.{total:.2f}</div>
        </div>"""

    # Build terms HTML
    terms_html = ""
    for term in TERMS:
        terms_html += f"<p>{term}</p>\n"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Bumble Dry Invoice</title>
<style>
    @page {{
        size: A4;
        margin: 0;
    }}
    * {{
        box-sizing: border-box;
    }}
    html, body {{
        margin: 0;
        padding: 0;
        background: #ffffff;
        font-family: Arial, Helvetica, sans-serif;
        color: #263238;
    }}
    body {{
        width: 210mm;
        margin: 0 auto;
    }}
    .page {{
        width: 210mm;
        height: 297mm;
        position: relative;
        overflow: hidden;
        background: #fff;
        padding: 10.5mm 10.5mm 12mm 10.5mm;
        page-break-after: always;
    }}
    .page:last-child {{
        page-break-after: auto;
    }}
    :root {{
        --navy: #203f66;
        --light-blue: #f1f5f9;
        --text: #27333f;
        --muted: #7b8794;
        --line: #e2e5e8;
    }}
    .invoice-header {{
        width: 100%;
        height: 43mm;
        background: var(--light-blue);
        border-radius: 5mm;
        display: flex;
        align-items: center;
        padding: 6.2mm;
        position: relative;
    }}
    .logo-box {{
        width: 25mm;
        height: 25mm;
        background: #fff;
        border-radius: 4mm;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        flex-shrink: 0;
    }}
    .logo-box img {{
        width: 100%;
        height: 100%;
        object-fit: contain;
        padding: 1.5mm;
    }}
    .company-info {{
        margin-left: 5.3mm;
        align-self: center;
    }}
    .company-name {{
        color: var(--navy);
        font-size: 24px;
        line-height: 1;
        font-weight: 700;
        margin-bottom: 4mm;
    }}
    .company-detail {{
        color: #7b8794;
        font-size: 12px;
        line-height: 1.7;
    }}
    .invoice-info {{
        position: absolute;
        right: 6.3mm;
        top: 6.2mm;
        width: 52mm;
        text-align: right;
    }}
    .invoice-pill {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        height: 7mm;
        min-width: 29mm;
        padding: 0 5mm;
        background: var(--navy);
        color: white;
        border-radius: 4mm;
        font-size: 10px;
        letter-spacing: 3px;
        font-weight: 500;
        margin-bottom: 5.5mm;
    }}
    .invoice-number {{
        color: var(--navy);
        font-size: 23px;
        line-height: 1;
        font-weight: 700;
        margin-bottom: 4.5mm;
    }}
    .invoice-date {{
        color: #727e8b;
        font-size: 11.5px;
        line-height: 1.75;
    }}
    .invoice-date span {{
        display: inline-block;
        min-width: 22mm;
        text-align: right;
        color: #7c8792;
    }}
    .bill-to {{
        margin-top: 5.5mm;
        height: 30.5mm;
        width: 100%;
        background: var(--light-blue);
        border-radius: 5mm;
        padding: 7mm 5.3mm;
    }}
    .bill-title {{
        color: var(--navy);
        font-size: 15px;
        font-weight: 700;
        margin-bottom: 5mm;
    }}
    .customer-name {{
        color: #303a44;
        font-size: 17px;
        font-weight: 700;
        margin-bottom: 2mm;
    }}
    .customer-contact {{
        color: #7c8792;
        font-size: 12px;
    }}
    .items {{
        margin-top: 6.5mm;
        width: 100%;
    }}
    .table-header {{
        height: 14mm;
        background: var(--navy);
        color: white;
        border-radius: 2mm;
        display: grid;
        grid-template-columns: 58% 14% 14% 14%;
        align-items: center;
        padding: 0 4mm;
    }}
    .table-header div {{
        font-size: 13px;
        font-weight: 500;
    }}
    .table-header div:not(:first-child) {{
        text-align: right;
    }}
    .item-row {{
        min-height: 18mm;
        display: grid;
        grid-template-columns: 58% 14% 14% 14%;
        padding: 6.5mm 4mm 4mm;
        border-bottom: 1px solid var(--line);
    }}
    .item-main {{
        font-size: 13px;
        color: #333d46;
        line-height: 1.4;
    }}
    .item-sub {{
        font-size: 12px;
        color: #697581;
    }}
    .item-cell {{
        font-size: 13px;
        color: #303943;
        text-align: right;
        white-space: nowrap;
    }}
    .lower-section {{
        display: grid;
        grid-template-columns: 56% 40%;
        gap: 5%;
        margin-top: 8mm;
    }}
    .thank-card, .price-card {{
        background: var(--light-blue);
        border-radius: 5mm;
        height: 77mm;
    }}
    .thank-card {{
        padding: 7mm 5.3mm;
    }}
    .thank-title {{
        color: var(--navy);
        font-size: 16px;
        font-weight: 700;
        margin-bottom: 4mm;
    }}
    .thank-placeholder {{
        width: 42mm;
        height: 57mm;
        background: white;
        border-radius: 4mm;
        border: 1px solid #edf0f2;
    }}
    .price-card {{
        padding: 7mm 5.3mm;
    }}
    .price-title {{
        color: var(--navy);
        font-size: 15px;
        font-weight: 700;
        margin-bottom: 7mm;
    }}
    .price-row {{
        display: flex;
        justify-content: space-between;
        font-size: 13px;
        color: #39444e;
        min-height: 9mm;
        align-items: center;
    }}
    .price-row.border {{
        border-bottom: 1px solid #d8dde2;
    }}
    .price-row.bold {{
        font-weight: 700;
        color: #27333f;
    }}
    .price-row .amount {{
        text-align: right;
        white-space: nowrap;
    }}
    .price-row.net {{
        margin-top: 3mm;
    }}
    .price-row.muted {{
        color: #9ca8b4;
    }}
    .price-row.muted .amount {{
        color: #39444e;
    }}
    .terms {{
        margin-top: 12mm;
    }}
    .terms-title {{
        color: var(--navy);
        font-size: 23px;
        font-weight: 700;
        margin-bottom: 7mm;
    }}
    .terms-content {{
        padding-left: 5.3mm;
        color: #353d45;
        font-size: 12.5px;
        line-height: 1.7;
    }}
    .terms-content p {{
        margin: 0;
    }}
    .footer {{
        position: absolute;
        left: 10.5mm;
        right: 10.5mm;
        bottom: 9mm;
        height: 7mm;
        border-top: 1px solid #eeeeee;
        display: flex;
        align-items: flex-end;
        justify-content: space-between;
        padding-top: 4mm;
        color: #7c8792;
        font-size: 10px;
    }}
</style>
</head>
<body>

<!-- PAGE 1 -->
<div class="page">
    <div class="invoice-header">
        <div class="logo-box">
            <img src="data:image/png;base64,{logo_b64}" alt="BumbleDry Logo">
        </div>
        <div class="company-info">
            <div class="company-name">{COMPANY_NAME}</div>
            <div class="company-detail">
                {COMPANY_LOCATION}<br>
                Tel. {COMPANY_PHONE}<br>
                GST: {COMPANY_GST}
            </div>
        </div>
        <div class="invoice-info">
            <div class="invoice-pill">INVOICE</div>
            <div class="invoice-number">#{INVOICE_NO}</div>
            <div class="invoice-date">
                <div><span>Order Date:</span> {ORDER_DATE}</div>
                <div><span>Due Date:</span> {DUE_DATE}</div>
            </div>
        </div>
    </div>

    <div class="bill-to">
        <div class="bill-title">Bill To:</div>
        <div class="customer-name">{CUSTOMER_NAME}</div>
        <div class="customer-contact">Contact No. {CUSTOMER_PHONE}</div>
    </div>

    <div class="items">
        <div class="table-header">
            <div>Item</div>
            <div>Price</div>
            <div>Quantity</div>
            <div>Total</div>
        </div>
        {items_html}
    </div>

    <div class="lower-section">
        <div class="thank-card">
            <div class="thank-title">Thank you for your business</div>
            <div class="thank-placeholder"></div>
        </div>

        <div class="price-card">
            <div class="price-title">PRICE DETAILS</div>
            <div class="price-row border">
                <span>Expected Value:</span>
                <span class="amount">Rs.{net_amount:.2f}</span>
            </div>
            <div class="price-row">
                <span>Sub Total:</span>
                <span class="amount">Rs.{sub_total:.2f}</span>
            </div>
            <div class="price-row border">
                <span>GST({GST_RATE:.0f}%)</span>
                <span class="amount">Rs.{gst_amount:.2f}</span>
            </div>
            <div class="price-row bold net">
                <span>Net Amount:</span>
                <span class="amount">Rs.{net_amount:.2f}</span>
            </div>
            <div class="price-row muted">
                <span>Amount Paid</span>
                <span class="amount">Rs.{AMOUNT_PAID:.2f}</span>
            </div>
            <div class="price-row bold">
                <span>Balance Amount</span>
                <span class="amount">Rs.{balance:.2f}</span>
            </div>
        </div>
    </div>

    <div class="footer">
        <div>{COMPANY_NAME}</div>
        <div>Page 1/2</div>
    </div>
</div>

<!-- PAGE 2 -->
<div class="page">
    <div class="invoice-header">
        <div class="logo-box">
            <img src="data:image/png;base64,{logo_b64}" alt="BumbleDry Logo">
        </div>
        <div class="company-info">
            <div class="company-name">{COMPANY_NAME}</div>
            <div class="company-detail">
                {COMPANY_LOCATION}<br>
                Tel. {COMPANY_PHONE}<br>
                GST: {COMPANY_GST}
            </div>
        </div>
        <div class="invoice-info">
            <div class="invoice-pill">INVOICE</div>
            <div class="invoice-number">#{INVOICE_NO}</div>
            <div class="invoice-date">
                <div><span>Order Date:</span> {ORDER_DATE}</div>
                <div><span>Due Date:</span> {DUE_DATE}</div>
            </div>
        </div>
    </div>

    <div class="terms">
        <div class="terms-title">Terms &amp; Conditions</div>
        <div class="terms-content">
            {terms_html}
        </div>
    </div>

    <div class="footer">
        <div>{COMPANY_NAME}</div>
        <div>Page 2/2</div>
    </div>
</div>

</body>
</html>"""

    app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_path = os.path.join(app_dir, OUTPUT_FILE)
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅  Invoice saved → {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_invoice()
