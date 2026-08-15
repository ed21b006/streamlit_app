import streamlit as st
import os
import sys
import glob
import importlib.util
import pandas as pd
from PIL import Image, ImageFont
import re

# Set page config
st.set_page_config(page_title="Invoice Generator", layout="wide")
st.title("🧾 Dynamic Invoice Generator")

# Determine base directory dynamically (assumes app.py is in UFLP/streamlit_app)
APP_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(APP_DIR, "templates")
MENUS_DIR = os.path.join(APP_DIR, "menus")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

# --- PATCH IMAGEFONT FOR DEPLOYMENT ---
# The templates use hardcoded Linux font paths (/usr/share/...).
# When deployed on Streamlit Cloud, those paths don't exist, causing fallback to tiny default fonts.
# We intercept those calls to redirect them to our local 'fonts/' directory.
original_truetype = ImageFont.truetype

def patched_truetype(font=None, size=10, index=0, encoding='', layout_engine=None):
    if isinstance(font, str):
        if "DejaVuSansMono-Bold" in font:
            font = os.path.join(APP_DIR, "fonts", "DejaVuSansMono-Bold.ttf")
        elif "DejaVuSans" in font or "DejaVu" in font:
            font = os.path.join(APP_DIR, "fonts", "DejaVuSansMono.ttf")
    
    try:
        return original_truetype(font, size, index, encoding, layout_engine)
    except OSError:
        # Final fallback to standard local font if it fails for some reason
        return original_truetype(os.path.join(APP_DIR, "fonts", "DejaVuSansMono.ttf"), size, index, encoding, layout_engine)

ImageFont.truetype = patched_truetype
# --------------------------------------

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

st.header("📝 Invoice Details")
col1, col2 = st.columns(2)

new_values = {}

# Group variables
items_var = "ITEMS" if "ITEMS" in variables else None
other_vars = [v for v in variables if v != items_var]

for i, var in enumerate(other_vars):
    current_val = getattr(module, var)
    target_col = col1 if i % 2 == 0 else col2
    
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

import json
import inspect

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
    if items:
        if isinstance(items[0], tuple):
            st.session_state.is_tuple = True
            formatted_items = []
            if len(items[0]) == 3:
                for it in items:
                    formatted_items.append({"Name": it[0], "Qty": it[1], "Rate": it[2]})
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

if items_var:
    df = pd.DataFrame(st.session_state.invoice_items)
    if df.empty:
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
sel_item = ac1.selectbox("Select from Menu", ["-- Select --"] + list(menu_items.keys()))
qty = ac2.number_input("Quantity", min_value=1, step=1, value=1)
if ac3.button("Add to Invoice", use_container_width=True):
    if sel_item != "-- Select --":
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
        import os
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
        
        # Execute invoice generation
        original_cwd = os.getcwd()
        os.chdir(APP_DIR)
        try:
            module.generate_invoice()
            output_file = getattr(module, "OUTPUT_FILE", "invoice.png")
            out_path = os.path.join(APP_DIR, output_file)
            
            if os.path.exists(out_path):
                st.success("✅ Invoice generated successfully!")
                
                # Display image
                image = Image.open(out_path)
                st.image(image, caption="Generated Invoice", use_container_width=True)
                
                # Download button
                with open(out_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download Invoice",
                        data=f,
                        file_name=output_file,
                        mime="image/png"
                    )
            else:
                st.error(f"Output file {output_file} not found after generation.")
        except Exception as e:
            st.error(f"Error generating invoice: {e}")
        finally:
            os.chdir(original_cwd)
