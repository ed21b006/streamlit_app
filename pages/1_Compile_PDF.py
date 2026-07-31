import streamlit as st
import io
from PIL import Image, ImageDraw

st.set_page_config(page_title="Compile PDF", layout="wide")
st.title("📄 Compile Invoices to PDF")

st.markdown("""
Upload multiple generated invoice images here to compile them into a single PDF for easy physical printing.
The layout is optimized into a grid so you can cut them with scissors using straight continuous cuts!
""")

col1, col2, col3 = st.columns(3)
with col1:
    num_cols = st.selectbox("Columns per page", [1, 2, 3, 4], index=2, help="Number of invoices placed side by side.")
with col2:
    margin = st.number_input("Page Margin (pixels)", min_value=0, max_value=500, value=100, step=10)
with col3:
    st.markdown("<br>", unsafe_allow_html=True)
    draw_lines = st.checkbox("Draw cut guidelines", value=True, help="Draws light gray lines to guide scissor cuts.")

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
            
            col_width = (PAGE_W - 2 * margin) // num_cols
            max_img_h = PAGE_H - 2 * margin
            
            pages = []
            current_page = Image.new("RGB", (PAGE_W, PAGE_H), "white")
            draw = ImageDraw.Draw(current_page)
            
            current_y = margin
            
            for i in range(0, len(uploaded_files), num_cols):
                batch = uploaded_files[i : i + num_cols]
                row_imgs = []
                
                for file_obj in batch:
                    img = Image.open(file_obj)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    w_percent = (col_width / float(img.width))
                    h_size = int((float(img.height) * float(w_percent)))
                    
                    if h_size > max_img_h:
                        h_percent = (max_img_h / float(img.height))
                        w_size = int((float(img.width) * float(h_percent)))
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
                    
                current_x = margin
                for idx, img in enumerate(row_imgs):
                    current_page.paste(img, (current_x, current_y))
                    
                    if draw_lines and idx < num_cols - 1:
                        line_x = current_x + col_width
                        draw.line([(line_x, current_y), (line_x, current_y + row_height)], fill="#CCCCCC", width=2)
                        
                    current_x += col_width
                    
                if draw_lines:
                    draw.line([(margin, current_y + row_height), (margin + num_cols * col_width, current_y + row_height)], fill="#CCCCCC", width=2)
                    
                current_y += row_height
                
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
