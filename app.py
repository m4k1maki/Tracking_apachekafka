import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
from login import login_page
from components import menu


# Cấu hình trang
st.set_page_config(page_title="Theo dõi giao nhận hàng", layout="wide")

# Kiểm tra trạng thái đăng nhập
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Nếu chưa đăng nhập, hiển thị trang đăng nhập
if not st.session_state["logged_in"]:
    login_page()
    st.stop()

# Gọi menu chính sau khi đăng nhập
menu.show()
