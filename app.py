import streamlit as st
import os
import sys
import glob
import importlib.util
import pandas as pd
from PIL import Image, ImageFont
import re
import json
import inspect
import io
import zipfile
from datetime import datetime, time as dt_time, date as dt_date

# Set page config
st.set_page_config(page_title="Invoice Generator", layout="wide")

# Determine base directory dynamically
APP_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(APP_DIR, "templates")
MENUS_DIR = os.path.join(APP_DIR, "menus")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from dateutil.parser import parse as date_parse

# ─────────────────────────────────────────────
#  PATTERN LOCK AUTHENTICATION
# ─────────────────────────────────────────────
CORRECT_PATTERN = "4,2,5,3"

def show_pattern_lock():
    """Render a 3x3 pattern lock as a self-contained HTML/JS component."""
    import streamlit.components.v1 as components

    # Hide sidebar & Streamlit chrome on lock screen, and hide the native Streamlit unlock button
    st.markdown("""<style>
    [data-testid="stSidebar"], [data-testid="stSidebarNav"],
    header, footer, #MainMenu {display: none !important;}
    .block-container {padding-top: 0 !important; max-width: 100% !important;}
    [data-testid="stAppViewContainer"] {background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);}
    
    /* Hide the Streamlit trigger button used for unlocking */
    div[data-testid="stButton"] {display: none !important;}
    </style>""", unsafe_allow_html=True)

    components.html("""
    <!DOCTYPE html>
    <html><head><style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        display: flex; justify-content: center; align-items: center;
        min-height: 480px; height: 100%;
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        background: transparent; color: #fff;
        -webkit-tap-highlight-color: transparent;
        user-select: none; -webkit-user-select: none;
    }
    .lock-wrap { text-align: center; }
    .lock-icon { font-size: 2.5rem; margin-bottom: 0.3rem; }
    .lock-title {
        font-size: 1.8rem; font-weight: 700; margin-bottom: 0.2rem;
        background: linear-gradient(135deg, #667eea, #a78bfa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .lock-sub { color: #aaa; font-size: 0.95rem; margin-bottom: 1.5rem; }
    .progress {
        min-height: 2.5rem; font-size: 1.3rem; letter-spacing: 0.4rem;
        color: #a78bfa; font-weight: 600; margin-bottom: 1rem;
    }
    .grid {
        display: grid; grid-template-columns: repeat(3, 75px);
        grid-template-rows: repeat(3, 75px);
        gap: 15px; justify-content: center; margin-bottom: 1.5rem;
    }
    .dot {
        width: 75px; height: 75px; border-radius: 50%;
        border: 2.5px solid rgba(255,255,255,0.25);
        background: rgba(255,255,255,0.06);
        display: flex; align-items: center; justify-content: center;
        cursor: pointer; transition: all 0.2s ease;
        font-size: 1.6rem; color: rgba(255,255,255,0.35);
    }
    .dot:hover { border-color: rgba(167,139,250,0.6); background: rgba(167,139,250,0.1); }
    .dot:active { transform: scale(0.92); }
    .dot.selected {
        border-color: #667eea; background: rgba(102,126,234,0.25);
        color: #a78bfa; box-shadow: 0 0 16px rgba(102,126,234,0.35);
    }
    .dot.wrong {
        border-color: #ef4444; background: rgba(239,68,68,0.2);
        color: #ef4444; animation: shake 0.4s ease;
    }
    @keyframes shake {
        0%,100% { transform: translateX(0); }
        25% { transform: translateX(-6px); }
        75% { transform: translateX(6px); }
    }
    .error { color: #ef4444; font-size: 0.95rem; min-height: 1.5rem; margin-bottom: 0.5rem; }
    .reset-btn {
        background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15);
        color: #ccc; padding: 0.5rem 1.6rem; border-radius: 8px;
        cursor: pointer; font-size: 0.9rem; transition: all 0.2s;
    }
    .reset-btn:hover { background: rgba(255,255,255,0.15); color: #fff; }
    
    @media (max-width: 400px) {
        .grid { grid-template-columns: repeat(3, 65px); grid-template-rows: repeat(3, 65px); gap: 12px; }
        .dot { width: 65px; height: 65px; font-size: 1.4rem; }
    }
    </style></head>
    <body>
    <div class="lock-wrap">
        <div class="lock-icon">🔒</div>
        <div class="lock-title">Pattern Lock</div>
        <div class="lock-sub">Tap the dots in the correct order</div>
        <div class="progress" id="progress">. . .</div>
        <div class="error" id="error"></div>
        <div class="grid" id="grid"></div>
        <button class="reset-btn" onclick="resetPattern()">🔄 Reset</button>
    </div>
    <script>
    const CORRECT = [4,2,5,3];
    let selected = [];
    const grid = document.getElementById('grid');
    const progress = document.getElementById('progress');
    const error = document.getElementById('error');

    for (let i = 1; i <= 9; i++) {
        const d = document.createElement('div');
        d.className = 'dot';
        d.textContent = '○';
        d.dataset.num = i;
        d.addEventListener('click', () => tapDot(i, d));
        grid.appendChild(d);
    }

    function tapDot(num, el) {
        if (selected.includes(num)) return;
        selected.push(num);
        el.classList.add('selected');
        el.textContent = '●';
        error.textContent = '';
        progress.textContent = selected.join(' → ');

        if (selected.length === CORRECT.length) {
            if (JSON.stringify(selected) === JSON.stringify(CORRECT)) {
                progress.style.color = '#4ade80';
                progress.textContent = '✓ Unlocked';
                setTimeout(() => {
                    // Click the hidden Streamlit button using textContent.includes
                    try {
                        const btns = window.parent.document.querySelectorAll('button');
                        for (const btn of btns) {
                            if (btn.textContent.includes('UNLOCK_TRIGGER_12345')) {
                                btn.click();
                                return;
                            }
                        }
                    } catch(e) { console.error('Unlock error:', e); }
                }, 400);
            } else {
                error.textContent = '❌ Wrong pattern!';
                document.querySelectorAll('.dot').forEach(d => d.classList.add('wrong'));
                setTimeout(resetPattern, 800);
            }
        }
    }

    function resetPattern() {
        selected = [];
        error.textContent = '';
        progress.textContent = '. . .';
        progress.style.color = '#a78bfa';
        document.querySelectorAll('.dot').forEach(d => {
            d.className = 'dot';
            d.textContent = '○';
        });
    }
    </script>
    </body></html>
    """, height=520)

    # Hidden unlock button for the JS above to click
    if st.button("UNLOCK_TRIGGER_12345", key="hidden_unlock_btn"):
        st.session_state.authenticated = True
        st.rerun()


# ─────────────────────────────────────────────
#  AUTH GATE
# ─────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    show_pattern_lock()
    st.stop()


# ─────────────────────────────────────────────
#  BACKUP / RESTORE (sidebar)
# ─────────────────────────────────────────────
def create_backup_zip():
    """Zip templates/ and menus/ directories."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for folder in ["templates", "menus"]:
            folder_path = os.path.join(APP_DIR, folder)
            if os.path.isdir(folder_path):
                for root, dirs, files in os.walk(folder_path):
                    # Skip __pycache__
                    dirs[:] = [d for d in dirs if d != "__pycache__"]
                    for fname in files:
                        fpath = os.path.join(root, fname)
                        arcname = os.path.relpath(fpath, APP_DIR)
                        zf.write(fpath, arcname)
    buf.seek(0)
    return buf.getvalue()

def restore_from_zip(zip_bytes):
    """Restore templates/ and menus/ from uploaded zip."""
    buf = io.BytesIO(zip_bytes)
    with zipfile.ZipFile(buf, "r") as zf:
        for member in zf.namelist():
            # Only allow templates/ and menus/ to be restored
            if member.startswith("templates/") or member.startswith("menus/"):
                target = os.path.join(APP_DIR, member)
                os.makedirs(os.path.dirname(target), exist_ok=True)
                if not member.endswith("/"):
                    with zf.open(member) as src, open(target, "wb") as dst:
                        dst.write(src.read())

with st.sidebar:
    st.markdown("### 💾 Backup & Restore")
    st.caption("Templates & menus are lost when the cloud app sleeps. Download a backup and restore when needed.")
    
    backup_data = create_backup_zip()
    st.download_button(
        "⬇️ Download Backup",
        data=backup_data,
        file_name="invoice_app_backup.zip",
        mime="application/zip",
        use_container_width=True
    )
    
    uploaded_zip = st.file_uploader("Upload Backup to Restore", type=["zip"], key="restore_zip")
    if uploaded_zip is not None:
        if st.button("🔄 Restore from Backup", use_container_width=True):
            try:
                restore_from_zip(uploaded_zip.getvalue())
                st.success("✅ Restored! Refreshing...")
                st.rerun()
            except Exception as e:
                st.error(f"Restore failed: {e}")
    
    st.markdown("---")


# ─────────────────────────────────────────────
#  MAIN APP (original app.py logic below)
# ─────────────────────────────────────────────

st.title("🧾 Dynamic Invoice Generator")

@st.cache_resource
def clear_old_invoices():
    for ext in ["*.png", "*.pdf", "*.html"]:
        for f in glob.glob(os.path.join(APP_DIR, ext)):
            if os.path.basename(f) == "logo.png":
                continue
            try:
                os.remove(f)
            except Exception:
                pass
    return True

clear_old_invoices()

# ─────────────────────────────────────────────
#  GLOBAL DPI SCALING (Monkey Patch PIL)
#  Guard: only patch once per process lifetime.
#  Streamlit reruns app.py top-level code on every
#  interaction. Without this guard, each rerun would
#  re-capture the already-patched functions as
#  "originals", compounding the SCALE factor and
#  eventually causing "invalid pixel size" from PIL.
# ─────────────────────────────────────────────
from PIL import Image, ImageDraw, ImageFont

SCALE = 3

if not getattr(Image, "_pil_dpi_patched", False):
    _original_new = Image.new
    def patched_new(mode, size, color=0):
        real_size = (int(size[0] * SCALE), int(size[1] * SCALE))
        img = _original_new(mode, real_size, color)
        original_crop = img.crop
        def patched_crop(box=None):
            if box is not None:
                box = tuple(int(v * SCALE) for v in box)
            return original_crop(box)
        img.crop = patched_crop
        return img
    Image.new = patched_new
    Image._pil_dpi_patched = True

class ScaledFont:
    def __init__(self, real_font):
        self.real_font = real_font
    def getbbox(self, text, *args, **kwargs):
        bbox = self.real_font.getbbox(text, *args, **kwargs)
        if bbox is None: return None
        return tuple(v / SCALE for v in bbox)
    def getlength(self, text, *args, **kwargs):
        length = self.real_font.getlength(text, *args, **kwargs)
        return length / SCALE
    def getsize(self, text, *args, **kwargs):
        size = self.real_font.getsize(text, *args, **kwargs)
        return tuple(v / SCALE for v in size)

if not getattr(ImageFont, "_pil_dpi_patched", False):
    _original_truetype = ImageFont.truetype
    def patched_truetype(font=None, size=10, index=0, encoding='', layout_engine=None):
        real_size = int(size * SCALE)
        if isinstance(font, str):
            if "DejaVuSansMono-Bold" in font:
                font = os.path.join(APP_DIR, "fonts", "DejaVuSansMono-Bold.ttf")
            elif "DejaVuSans" in font or "DejaVu" in font:
                font = os.path.join(APP_DIR, "fonts", "DejaVuSansMono.ttf")
        try:
            real_font = _original_truetype(font, real_size, index, encoding, layout_engine)
        except OSError:
            real_font = _original_truetype(os.path.join(APP_DIR, "fonts", "DejaVuSansMono.ttf"), real_size, index, encoding, layout_engine)
        return ScaledFont(real_font)
    ImageFont.truetype = patched_truetype
    ImageFont._pil_dpi_patched = True

if not getattr(ImageDraw, "_pil_dpi_patched", False):
    _original_draw = ImageDraw.Draw
    def patched_draw(im, mode=None):
        real_draw = _original_draw(im, mode)
        class DrawWrapper:
            def text(self, xy, text, fill=None, font=None, anchor=None, *args, **kwargs):
                real_xy = (xy[0] * SCALE, xy[1] * SCALE)
                real_font = font.real_font if isinstance(font, ScaledFont) else font
                real_draw.text(real_xy, text, fill=fill, font=real_font, anchor=anchor, *args, **kwargs)
            def line(self, xy, fill=None, width=0, *args, **kwargs):
                if isinstance(xy[0], (list, tuple)):
                    real_xy = [(x * SCALE, y * SCALE) for x, y in xy]
                else:
                    real_xy = [v * SCALE for v in xy]
                real_width = max(1, int(width * SCALE)) if width else 0
                real_draw.line(real_xy, fill=fill, width=real_width, *args, **kwargs)
            def rectangle(self, xy, fill=None, outline=None, width=1, *args, **kwargs):
                if isinstance(xy[0], (list, tuple)):
                    real_xy = [(x * SCALE, y * SCALE) for x, y in xy]
                else:
                    real_xy = [v * SCALE for v in xy]
                real_width = max(1, int(width * SCALE)) if width else 1
                real_draw.rectangle(real_xy, fill=fill, outline=outline, width=real_width, *args, **kwargs)
        return DrawWrapper()
    ImageDraw.Draw = patched_draw
    ImageDraw._pil_dpi_patched = True
# ─────────────────────────────────────────────

# Find all template files
template_files = glob.glob(os.path.join(TEMPLATES_DIR, "*.py"))
template_names = [os.path.basename(f) for f in template_files]

if not template_names:
    st.error(f"No templates found in {APP_DIR}")
    st.stop()

selected_template = st.selectbox("Select a Template", sorted(template_names))

@st.cache_resource
def load_module(filepath):
    module_name = os.path.splitext(os.path.basename(filepath))[0]
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    module = importlib.util.module_from_spec(spec)
    
    # Temporarily change CWD and sys.path so template can find any local resources
    original_cwd = os.getcwd()
    os.chdir(APP_DIR)
    
    try:
        spec.loader.exec_module(module)
    finally:
        os.chdir(original_cwd)
            
    return module

selected_path = os.path.join(TEMPLATES_DIR, selected_template)
try:
    # We reload it without cache if we want dynamic variables, but caching the module object is fine
    # because we modify its attributes later. Actually, it's safer NOT to cache so that each selection starts fresh.
    # We'll remove @st.cache_resource.
    pass
except:
    pass

def get_module(filepath):
    module_name = os.path.splitext(os.path.basename(filepath))[0]
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    module = importlib.util.module_from_spec(spec)
    original_cwd = os.getcwd()
    os.chdir(APP_DIR)
    try:
        spec.loader.exec_module(module)
    finally:
        os.chdir(original_cwd)
    return module

try:
    module = get_module(selected_path)
except Exception as e:
    st.error(f"Failed to load module {selected_template}: {e}")
    st.stop()

# Introspect uppercase variables
variables = [v for v in dir(module) if v.isupper() and not v.startswith('_')]
if "OUTPUT_FILE" in variables:
    variables.remove("OUTPUT_FILE")

# ─────────────────────────────────────────────
#  DATE/TIME PICKER & AUTO-DERIVED FIELDS
# ─────────────────────────────────────────────

# Identify bill number variable names for this template
BILL_NO_VARS = ["BILL_NO", "INVOICE_NO", "ORDER_ID", "ORDER_NO", "RECEIPT_NO", "BILL_NUMBER", "INVOICE_NUMBER", "ORDER_NUMBER"]
template_bill_vars = [v for v in variables if v in BILL_NO_VARS]

# Identify date/time variables
DATE_VARS = ["DATE", "ORDER_DATE", "DUE_DATE"]
TIME_VARS = ["TIME"]

# Detect which date/time vars exist in this template
template_date_vars = [v for v in DATE_VARS if v in variables]
template_time_vars = [v for v in TIME_VARS if v in variables]

# Parse the default date from the template to use as the base date for bill number formula
default_date_str = ""
for dv in template_date_vars:
    val = getattr(module, dv, "")
    if val:
        default_date_str = val
        break

default_template_date = None
if default_date_str:
    try:
        default_template_date = date_parse(str(default_date_str)).date()
    except Exception:
        default_template_date = dt_date(2026, 7, 11)  # fallback
else:
    default_template_date = dt_date(2026, 7, 11)

# Parse the default time
default_time_str = ""
for tv in template_time_vars:
    val = getattr(module, tv, "")
    if val:
        default_time_str = val
        break

default_template_time = dt_time(9, 0)
if default_time_str:
    try:
        default_template_time = date_parse(str(default_time_str)).time()
    except Exception:
        pass

st.header("📝 Invoice Details")

# Date & Time picker section
st.subheader("📅 Bill Date & Time")
dt_col1, dt_col2 = st.columns(2)
with dt_col1:
    bill_date = st.date_input("Bill Date", value=default_template_date)
with dt_col2:
    bill_time = st.time_input("Bill Time", value=default_template_time)

bill_datetime = datetime.combine(bill_date, bill_time)

# ── Auto-generate bill number offset ──
# Formula: 500 * days_since_default + hours * 15 + minutes * 3
days_diff = (bill_date - default_template_date).days
bill_hours = bill_time.hour
bill_minutes = bill_time.minute
bill_offset = days_diff * 500 + bill_hours * 15 + bill_minutes * 3

# ── Helper: format date in the style of the template's default ──
def detect_date_format(original_str):
    """Detect the date format used by the template and return a strftime format string."""
    original = str(original_str).strip()
    # "Jul 11, 2026" or "Jul 10 2026"
    if re.match(r'^[A-Z][a-z]{2}\s+\d{1,2},?\s+\d{4}$', original):
        if ',' in original:
            return "%b %d, %Y"
        return "%b %d %Y"
    # "16 May 2024"
    if re.match(r'^\d{1,2}\s+[A-Z][a-z]+\s+\d{4}$', original):
        return "%d %b %Y"
    # "06-Jul-2026"
    if re.match(r'^\d{2}-[A-Z][a-z]{2}-\d{4}$', original):
        return "%d-%b-%Y"
    # "DD/MM/YYYY" or "DD-MM-YYYY"
    if re.match(r'^\d{2}[/-]\d{2}[/-]\d{4}$', original):
        sep = '/' if '/' in original else '-'
        return f"%d{sep}%m{sep}%Y"
    # "DD/MM/YY" or "DD-MM-YY"
    if re.match(r'^\d{2}[/-]\d{2}[/-]\d{2}$', original):
        sep = '/' if '/' in original else '-'
        return f"%d{sep}%m{sep}%y"
    # Fallback
    return "%d/%m/%Y"

def detect_time_format(original_str):
    """Detect the time format used by the template."""
    original = str(original_str).strip()
    # "10:31 PM" or "09:15 PM" (12-hour with AM/PM)
    if re.match(r'^\d{1,2}:\d{2}\s*[APap][Mm]$', original):
        return "%I:%M %p"
    # "20:34" or "22:51" (24-hour)
    if re.match(r'^\d{1,2}:\d{2}$', original):
        return "%H:%M"
    # "14:17:31" (24-hour with seconds)
    if re.match(r'^\d{1,2}:\d{2}:\d{2}$', original):
        return "%H:%M:%S"
    # Fallback
    return "%H:%M"

# ── Compute auto-derived date/time values ──
auto_derived = {}  # var_name -> (formatted_value, type)

for dv in template_date_vars:
    orig = str(getattr(module, dv, ""))
    fmt = detect_date_format(orig)
    # For DUE_DATE, add 1 day offset from ORDER_DATE
    if dv == "DUE_DATE":
        from datetime import timedelta
        # Calculate original offset between ORDER_DATE and DUE_DATE
        try:
            orig_order = date_parse(str(getattr(module, "ORDER_DATE", getattr(module, "DATE", "")))).date()
            orig_due = date_parse(orig).date()
            day_offset = (orig_due - orig_order).days
        except Exception:
            day_offset = 1
        due_date = bill_date + timedelta(days=day_offset)
        auto_derived[dv] = (due_date.strftime(fmt), str)
    else:
        auto_derived[dv] = (bill_date.strftime(fmt), str)

for tv in template_time_vars:
    orig = str(getattr(module, tv, ""))
    fmt = detect_time_format(orig)
    auto_derived[tv] = (bill_datetime.strftime(fmt), str)

# ── Auto-derive bill number ──
for b_var in template_bill_vars:
    orig_bill = str(getattr(module, b_var, ""))
    # Check if original has trailing digits
    digits_match = re.search(r'(\d+)$', orig_bill)
    if digits_match:
        orig_digits = digits_match.group(1)
        pad_len = len(orig_digits)
        base_num = int(orig_digits)
        new_num = base_num + bill_offset
        
        new_num_str = str(abs(new_num))
        if len(new_num_str) > pad_len:
            new_num_str = new_num_str[-pad_len:]
        else:
            new_num_str = new_num_str.zfill(pad_len)
            
        auto_bill_str = orig_bill[:digits_match.start()] + new_num_str
    else:
        auto_bill_str = f"{orig_bill}{bill_offset}"
    auto_derived[b_var] = (auto_bill_str, str)

# Show auto-derived values
if auto_derived:
    with st.expander("🔢 Auto-derived Date/Time & Bill Number", expanded=True):
        for var_name, (val, _) in auto_derived.items():
            st.text(f"{var_name}: {val}")

# ── Set of variables to skip from manual editing ──
skip_vars = set(auto_derived.keys())

st.markdown("---")

col1, col2 = st.columns(2)

new_values = {}

# Add auto-derived values to new_values first
for var_name, (val, vtype) in auto_derived.items():
    new_values[var_name] = (val, vtype)

# Group variables
items_var = "ITEMS" if "ITEMS" in variables else None
other_vars = [v for v in variables if v != items_var and v not in skip_vars]

manual_idx = 0
for var in other_vars:
    current_val = getattr(module, var)
    target_col = col1 if manual_idx % 2 == 0 else col2
    manual_idx += 1
    
    if isinstance(current_val, str):
        val = target_col.text_input(var, value=current_val)
        new_values[var] = (val, str)
    elif isinstance(current_val, float):
        val = target_col.number_input(var, value=current_val, format="%f")
        new_values[var] = (val, float)
    elif isinstance(current_val, int):
        val = target_col.number_input(var, value=current_val, step=1)
        new_values[var] = (val, int)
    elif isinstance(current_val, list):
        joined_val = "\n".join([str(v) for v in current_val])
        val = target_col.text_area(var, value=joined_val)
        new_values[var] = (val, list)
    else:
        # Fallback for unexpected types
        val = target_col.text_input(var, value=str(current_val))
        new_values[var] = (val, type(current_val))

def calculate_live_total(module, new_values, items_list):
    if not items_list:
        return 0.0
        
    if getattr(st.session_state, 'is_tuple', True):
        final_items = [tuple(row.values()) for row in items_list]
    else:
        final_items = items_list
        
    if hasattr(module, "compute_totals"):
        try:
            sig = inspect.signature(module.compute_totals)
            kwargs = {}
            for param_name in sig.parameters:
                if param_name == "items":
                    kwargs["items"] = final_items
                    continue
                var_name = param_name.upper()
                potential_vars = [var_name, var_name.replace("_PCT", "_PERCENT")]
                val_found = False
                for pv in potential_vars:
                    if pv in new_values:
                        kwargs[param_name] = new_values[pv][0]
                        val_found = True
                        break
                    elif hasattr(module, pv):
                        kwargs[param_name] = getattr(module, pv)
                        val_found = True
                        break
                if not val_found:
                    kwargs[param_name] = 0.0
            
            res = module.compute_totals(**kwargs)
            if isinstance(res, tuple):
                return float(res[-1])
            return float(res)
        except Exception as e:
            pass
            
    subtotal = 0.0
    for row in items_list:
        try:
            qty = float(row.get("Qty", 0))
            rate = float(row.get("Rate", 0.0))
        except (ValueError, TypeError):
            qty = 0.0
            rate = 0.0
        subtotal += qty * rate
        
    total_tax = 0.0
    for tax_var in ["CGST_RATE", "SGST_RATE", "CGST_PERCENT", "SGST_PERCENT", "CENTRAL_GST_RATE", "STATE_GST_RATE"]:
        tax_rate = 0.0
        if tax_var in new_values:
            try:
                tax_rate = float(new_values[tax_var][0])
            except (ValueError, TypeError):
                tax_rate = 0.0
        elif hasattr(module, tax_var):
            try:
                tax_rate = float(getattr(module, tax_var))
            except (ValueError, TypeError):
                tax_rate = 0.0
        total_tax += (subtotal * tax_rate / 100.0)
        
    return subtotal + total_tax

colA, colB = st.columns([3, 1])
with colA:
    st.subheader("🍔 Menu Items")
tot_placeholder = colB.empty()


# Initialize session state for items
if "current_template" not in st.session_state or st.session_state.current_template != selected_template:
    st.session_state.current_template = selected_template
    
    items = getattr(module, items_var) if items_var else []
    
    st.session_state.is_tuple = False
    st.session_state.tuple_len = 3  # default tuple length
    if items:
        if isinstance(items[0], tuple):
            st.session_state.is_tuple = True
            st.session_state.tuple_len = len(items[0])
            formatted_items = []
            if len(items[0]) == 3:
                for it in items:
                    formatted_items.append({"Name": it[0], "Qty": it[1], "Rate": it[2]})
            elif len(items[0]) == 5:
                # Laundry template: (description, sub_description, unit_price, quantity_str, total)
                for it in items:
                    formatted_items.append({
                        "Description": it[0],
                        "Sub Description": it[1],
                        "Unit Price": it[2],
                        "Quantity": it[3],
                        "Total": it[4]
                    })
            else:
                for it in items:
                    d = {}
                    for i, val in enumerate(it):
                        d[f"Col{i+1}"] = val
                    formatted_items.append(d)
            st.session_state.invoice_items = formatted_items
        elif isinstance(items[0], dict):
            st.session_state.invoice_items = list(items)
    else:
        st.session_state.is_tuple = True
        st.session_state.invoice_items = []

# Load menu
menu_file = f"{os.path.splitext(selected_template)[0]}.json"
menu_path = os.path.join(MENUS_DIR, menu_file)
if os.path.exists(menu_path):
    with open(menu_path, "r") as f:
        menu_items = json.load(f)
else:
    menu_items = {}

with st.expander("📖 Manage Menu"):
    # --- Add new item ---
    c1, c2, c3 = st.columns([2, 1, 1])
    n_name = c1.text_input("New Menu Item Name")
    n_price = c2.number_input("New Menu Item Price", min_value=0.0, step=1.0)
    if c3.button("Save to Menu", use_container_width=True):
        if n_name:
            menu_items[n_name] = n_price
            with open(menu_path, "w") as f:
                json.dump(menu_items, f, indent=4)
            st.success(f"Added {n_name} to menu!")
            st.rerun()

    # --- Display existing items with prices & delete ---
    if menu_items:
        st.markdown("**Current Menu Items:**")
        for item_name, item_price in sorted(menu_items.items()):
            mc1, mc2, mc3 = st.columns([3, 1, 0.5])
            mc1.write(item_name)
            mc2.write(f"₹ {item_price:.2f}")
            if mc3.button("🗑️", key=f"del_menu_{item_name}", help=f"Delete {item_name}"):
                del menu_items[item_name]
                with open(menu_path, "w") as f:
                    json.dump(menu_items, f, indent=4)
                st.rerun()
    else:
        st.caption("No items in menu yet.")

if items_var:
    df = pd.DataFrame(st.session_state.invoice_items)
    if df.empty:
        tuple_len = getattr(st.session_state, 'tuple_len', 3)
        if tuple_len == 5:
            df = pd.DataFrame(columns=["Description", "Sub Description", "Unit Price", "Quantity", "Total"])
        else:
            df = pd.DataFrame(columns=["Name", "Qty", "Rate"])
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    st.session_state.invoice_items = edited_df.to_dict('records')
else:
    st.info("No ITEMS variable found in this template.")

# Calculate and display live total
live_tot = calculate_live_total(module, new_values, st.session_state.get('invoice_items', []))
tot_placeholder.metric("Live Total", f"₹ {live_tot:.2f}")


st.write("### Add Menu Item to Invoice")
ac1, ac2, ac3 = st.columns([2, 1, 1])
menu_display = {f"{name}  —  ₹{price:.2f}": name for name, price in menu_items.items()}
sel_display = ac1.selectbox("Select from Menu", ["-- Select --"] + list(menu_display.keys()))
qty = ac2.number_input("Quantity", min_value=1, step=1, value=1)
if ac3.button("Add to Invoice", use_container_width=True):
    if sel_display != "-- Select --":
        sel_item = menu_display[sel_display]
        price = menu_items[sel_item]
        st.session_state.invoice_items.append({"Name": sel_item, "Qty": qty, "Rate": price})
        st.rerun()

st.header("💾 Create New Template")
with st.expander("Save current configuration as a new template", expanded=False):
    new_tmpl_name = st.text_input("New Template Name (e.g. 'my_restaurant')")
    if st.button("Create Template"):
        if new_tmpl_name:
            # Read original template
            with open(selected_path, "r") as f:
                tmpl_content = f.read()
            
            # Replace variables with new_values
            for var, (val, vtype) in new_values.items():
                if vtype is str:
                    def repl(m, v=val):
                        return m.group(1) + repr(v)
                    tmpl_content = re.sub(rf'^({var}\s*=\s*).*$', repl, tmpl_content, flags=re.MULTILINE)
                elif vtype is list:
                    list_val = [line for line in val.split("\n") if line]
                    def repl(m, v=list_val):
                        return m.group(1) + repr(v)
                    tmpl_content = re.sub(rf'^({var}\s*=\s*).*$', repl, tmpl_content, flags=re.MULTILINE)
                else:
                    def repl(m, v=val):
                        return m.group(1) + repr(v)
                    tmpl_content = re.sub(rf'^({var}\s*=\s*).*$', repl, tmpl_content, flags=re.MULTILINE)
            
            # Clear items list
            if items_var:
                tmpl_content = re.sub(rf'^({items_var}\s*=\s*)\[.*?\]', rf'{items_var} = []', tmpl_content, flags=re.MULTILINE | re.DOTALL)
            
            # Save new template
            safe_name = new_tmpl_name.strip().replace(' ', '_').lower()
            if safe_name.startswith("template_"):
                safe_name = safe_name.replace("template_", "", 1)
            if not safe_name.endswith(".py"):
                safe_name += ".py"
                
            new_file_path = os.path.join(TEMPLATES_DIR, safe_name)
            with open(new_file_path, "w") as f:
                f.write(tmpl_content)
            
            # Create empty menu
            new_menu_name = f"{os.path.splitext(safe_name)[0]}.json"
            new_menu_path = os.path.join(MENUS_DIR, new_menu_name)
            with open(new_menu_path, "w") as f:
                json.dump({}, f)
                
            st.success(f"Successfully created {safe_name}! Please refresh the page to see it.")

st.markdown("---")

st.header("🗑️ Delete Template")
with st.expander("Delete this template and its menu", expanded=False):
    st.warning(f"Are you sure you want to delete '{selected_template}'?")
    if st.button("Confirm Delete"):
        if os.path.exists(selected_path):
            os.remove(selected_path)
        if os.path.exists(menu_path):
            os.remove(menu_path)
        st.success("Deleted successfully. Please refresh the page.")

if st.button("🚀 Generate Invoice", type="primary"):
    with st.spinner("Generating Invoice..."):
        # Apply changes to module
        for var, (val, vtype) in new_values.items():
            if vtype is list:
                setattr(module, var, [line for line in val.split("\n") if line])
            else:
                try:
                    setattr(module, var, vtype(val))
                except Exception:
                    setattr(module, var, val)
            
        if items_var:
            new_items_list = edited_df.to_dict('records')
            if st.session_state.is_tuple:
                # Convert back to tuple
                final_items = [tuple(row.values()) for row in new_items_list]
            else:
                final_items = new_items_list
            setattr(module, items_var, final_items)
            
        # Determine dynamic filename using bill_date and bill_time from the picker
        dynamic_name = getattr(module, "OUTPUT_FILE", "invoice.png")
        _, ext = os.path.splitext(dynamic_name)
        if not ext:
            ext = ".png"
            
        try:
            day = bill_date.day
            month = bill_date.strftime("%B")
            
            if "bumble_dry" in selected_template.lower():
                dynamic_name = f"Laundry {day} {month}{ext}"
            else:
                meal_type = ""
                hour = bill_time.hour
                if hour < 12:
                    meal_type = "Breakfast"
                elif hour < 16:
                    meal_type = "Lunch"
                else:
                    meal_type = "Dinner"
                
                if meal_type:
                    dynamic_name = f"{meal_type} {day} {month}{ext}"
                else:
                    dynamic_name = f"{day} {month}{ext}"
        except Exception:
            pass
                
        setattr(module, "OUTPUT_FILE", dynamic_name)
        
        # Execute invoice generation
        original_cwd = os.getcwd()
        os.chdir(APP_DIR)
        try:
            module.generate_invoice()
            output_file = getattr(module, "OUTPUT_FILE", "invoice.png")
            out_path = os.path.join(APP_DIR, output_file)
            
            if os.path.exists(out_path):
                st.success("✅ Invoice generated successfully!")
                
                is_pdf = out_path.lower().endswith(".pdf")
                is_html = out_path.lower().endswith(".html")
                
                if not is_pdf and not is_html:
                    # Display image
                    image = Image.open(out_path)
                    st.image(image, caption="Generated Invoice", use_container_width=True)
                else:
                    doc_type = "PDF" if is_pdf else "HTML document"
                    st.info(f"{doc_type} generated successfully. Please download it below.")
                
                # Determine mime type
                mime_type = "image/png"
                if is_pdf: mime_type = "application/pdf"
                if is_html: mime_type = "text/html"
                
                # Download button
                with open(out_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download Invoice",
                        data=f,
                        file_name=output_file,
                        mime=mime_type
                    )
            else:
                st.error(f"Output file {output_file} not found after generation.")
        except Exception as e:
            import traceback
            st.error(f"Error generating invoice: {e}")
            st.code(traceback.format_exc(), language="python")
        finally:
            os.chdir(original_cwd)
