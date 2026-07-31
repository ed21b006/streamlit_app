import streamlit as st
import os
import sys
import glob
import importlib.util
import pandas as pd
from PIL import Image

# Set page config
st.set_page_config(page_title="Invoice Generator", layout="wide")
st.title("🧾 Dynamic Invoice Generator")

# Determine base directory dynamically (assumes app.py is in UFLP/streamlit_app)
APP_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(APP_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Find all template files
template_files = glob.glob(os.path.join(BASE_DIR, "template_*.py"))
template_names = [os.path.basename(f) for f in template_files]

if not template_names:
    st.error(f"No templates found in {BASE_DIR}")
    st.stop()

selected_template = st.selectbox("Select a Template", sorted(template_names))

@st.cache_resource
def load_module(filepath):
    module_name = os.path.splitext(os.path.basename(filepath))[0]
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    module = importlib.util.module_from_spec(spec)
    
    # Temporarily change CWD and sys.path so template can find any local resources
    original_cwd = os.getcwd()
    os.chdir(BASE_DIR)
    
    try:
        spec.loader.exec_module(module)
    finally:
        os.chdir(original_cwd)
            
    return module

selected_path = os.path.join(BASE_DIR, selected_template)
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
    os.chdir(BASE_DIR)
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

st.subheader("🍔 Menu Items")

is_tuple = False
if items_var:
    items = getattr(module, items_var)
    if items and isinstance(items[0], tuple):
        is_tuple = True
        if len(items[0]) == 3:
            df = pd.DataFrame(items, columns=["Name", "Qty", "Rate"])
        else:
            cols = [f"Col{i+1}" for i in range(len(items[0]))]
            df = pd.DataFrame(items, columns=cols)
    elif items and isinstance(items[0], dict):
        df = pd.DataFrame(items)
    else:
        # Empty list fallback
        df = pd.DataFrame(columns=["Name", "Qty", "Rate"])
        is_tuple = True
        
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
else:
    st.info("No ITEMS variable found in this template.")

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
            if is_tuple:
                # Convert back to tuple
                final_items = [tuple(row.values()) for row in new_items_list]
            else:
                final_items = new_items_list
            setattr(module, items_var, final_items)
        
        # Execute invoice generation
        original_cwd = os.getcwd()
        os.chdir(BASE_DIR)
        try:
            module.generate_invoice()
            output_file = getattr(module, "OUTPUT_FILE", "invoice.png")
            out_path = os.path.join(BASE_DIR, output_file)
            
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
