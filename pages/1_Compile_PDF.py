import streamlit as st
import io
from PIL import Image, ImageDraw

st.set_page_config(page_title="Compile PDF", layout="wide")
st.title("📄 Compile Invoices to PDF")

st.markdown("""
Upload multiple generated invoice images here to compile them into a single PDF for easy physical printing.
The layout is optimized into a grid so you can cut them with scissors using straight continuous cuts!
""")

# --- Helper: mm to pixels at 300 DPI ---
def mm_to_px(mm):
    return int(mm * 300 / 25.4)

# --- Controls ---
col1, col2 = st.columns(2)
with col1:
    num_cols = st.selectbox("Columns per page", [1, 2, 3, 4], index=1, help="Number of invoices placed side by side.")
with col2:
    page_margin_mm = st.number_input("Page Margin (mm)", min_value=0.0, max_value=50.0, value=15.0, step=1.0, help="Margin on all four sides of the page.")

col3, col4 = st.columns(2)
with col3:
    h_gap_mm = st.number_input("Horizontal Gap (mm)", min_value=0.0, max_value=80.0, value=20.0, step=1.0, help="Space between invoices left-right.")
with col4:
    v_gap_mm = st.number_input("Vertical Gap (mm)", min_value=0.0, max_value=100.0, value=40.0, step=1.0, help="Space between invoices top-bottom.")


if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = 0

uploaded_files = st.file_uploader(
    "Upload Invoice Images", 
    type=["png", "jpg", "jpeg"], 
    accept_multiple_files=True, 
    key=f"uploader_{st.session_state['uploader_key']}"
)

if st.button("🔨 Compile PDF", type="primary"):
    if not uploaded_files:
        st.warning("Please upload at least one image.")
    else:
        with st.spinner("Compiling PDF..."):
            # A4 dimensions at 300 DPI
            PAGE_W = 2480
            PAGE_H = 3508
            
            margin = mm_to_px(page_margin_mm)
            h_gap = mm_to_px(h_gap_mm)
            v_gap = mm_to_px(v_gap_mm)
            
            # Usable width = page width - 2*margin - (num_cols-1)*h_gap
            total_h_gaps = (num_cols - 1) * h_gap
            col_width = (PAGE_W - 2 * margin - total_h_gaps) // num_cols
            max_img_h = PAGE_H - 2 * margin  # max height for a single image
            
            pages = []
            current_page = Image.new("RGB", (PAGE_W, PAGE_H), "white")
            draw = ImageDraw.Draw(current_page)
            
            current_y = margin
            row_index = 0  # track rows for separator logic
            
            for i in range(0, len(uploaded_files), num_cols):
                batch = uploaded_files[i : i + num_cols]
                row_imgs = []
                
                for file_obj in batch:
                    img = Image.open(file_obj)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Scale to fit column width while maintaining aspect ratio
                    scale = col_width / float(img.width)
                    h_size = int(float(img.height) * scale)
                    
                    if h_size > max_img_h:
                        scale = max_img_h / float(img.height)
                        w_size = int(float(img.width) * scale)
                        img = img.resize((w_size, max_img_h), Image.Resampling.LANCZOS)
                    else:
                        img = img.resize((col_width, h_size), Image.Resampling.LANCZOS)
                        
                    row_imgs.append(img)
                    
                row_height = max(img.height for img in row_imgs)
                
                # If this row exceeds the page height, start a new page
                if current_y + row_height > PAGE_H - margin:
                    pages.append(current_page)
                    current_page = Image.new("RGB", (PAGE_W, PAGE_H), "white")
                    draw = ImageDraw.Draw(current_page)
                    current_y = margin
                    row_index = 0
                
                # Draw HORIZONTAL separator line ABOVE this row (between rows, not before first)
                if row_index > 0:
                    line_y = current_y - v_gap // 2
                    draw.line(
                        [(margin, line_y), (PAGE_W - margin, line_y)],
                        fill=(0, 0, 0), width=1
                    )
                
                # Paste images in this row
                current_x = margin
                for idx, img in enumerate(row_imgs):
                    # Center image vertically within row_height
                    y_offset = (row_height - img.height) // 2
                    current_page.paste(img, (current_x, current_y + y_offset))
                    
                    # Draw VERTICAL separator line between columns (not after last)
                    if idx < len(row_imgs) - 1:
                        line_x = current_x + col_width + h_gap // 2
                        # Draw from top of page content to current bottom of this row
                        draw.line(
                            [(line_x, margin), (line_x, PAGE_H - margin)],
                            fill=(0, 0, 0), width=1
                        )
                    
                    current_x += col_width + h_gap
                    
                current_y += row_height + v_gap
                row_index += 1
                
            pages.append(current_page)
            
            pdf_bytes = io.BytesIO()
            if len(pages) > 0:
                pages[0].save(pdf_bytes, format="PDF", save_all=True, append_images=pages[1:], resolution=300)
            pdf_bytes.seek(0)
            
            st.session_state["pdf_bytes"] = pdf_bytes.getvalue()
            st.success(f"✅ Successfully compiled {len(uploaded_files)} invoices into {len(pages)} pages!")

if "pdf_bytes" in st.session_state:
    st.download_button(
        label="⬇️ Download PDF",
        data=st.session_state["pdf_bytes"],
        file_name="compiled_invoices.pdf",
        mime="application/pdf"
    )
    if st.button("🗑️ Clear Memory & Start Over"):
        del st.session_state["pdf_bytes"]
        st.session_state["uploader_key"] += 1
        st.rerun()
