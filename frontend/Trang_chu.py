"""
File: frontend/Trang_chu.py
Description:
    This is the main entry point for the Streamlit Frontend application.
    This file is responsible for:
    1. Configuring the page (st.set_page_config) in wide layout mode.
    2. Defining and running the multi-page navigation menu (st.navigation) displayed in the sidebar.
    3. Displaying content for the Home page (welcome page).
"""
import streamlit as st

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Dashboard Nông nghiệp VN",
    page_icon="🌾",
    layout="wide"
)

# --- 2. DEFINE HOME PAGE CONTENT ---
def show_home_page():
    st.title("🌾 Chào mừng đến với Dashboard Nông nghiệp Việt Nam")
    st.markdown("---")
    st.header("Giới thiệu dự án")
    st.write("""
        Đây là demo dashboard phân tích dữ liệu nông nghiệp Việt Nam, bao gồm các phân tích về địa lý, khí hậu, thổ nhưỡng và dự đoán sản lượng và năng suất nông nghiệp.
        Mục tiêu của dự án là cung cấp cái nhìn sâu sắc về các yếu tố ảnh hưởng đến năng suất nông nghiệp và hỗ trợ ra quyết định dựa trên dữ liệu.
    """)


    st.info("Vui lòng chọn một trang phân tích từ thanh điều hướng bên trái để bắt đầu.", icon="👈")

# --- 3. CREATE CUSTOM NAVIGATION ---
pages = [
    st.Page(show_home_page, title="Trang chủ", icon="🏠", default=True), 
    
    # Other pages
    st.Page("pages/1_Phân_tích_Nông_nghiệp.py", title="Phân tích Nông nghiệp", icon="📊"),
    st.Page("pages/2_Phân_tích_Địa_lý.py", title="Phân tích Địa lý", icon="🗺️"),
    st.Page("pages/3_Phân_tích_Khí_hậu.py", title="Phân tích Khí hậu", icon="☀️"),
    st.Page("pages/4_Phân_tích_Thổ_nhưỡng.py", title="Phân tích Thổ nhưỡng", icon="🌱"),
    st.Page("pages/5_Dự_đoán_số_liệu.py", title="Dự đoán Số liệu", icon="🔮"),
]
nav = st.navigation(pages)

# --- 4. RUN SELECTED PAGE ---
nav.run()