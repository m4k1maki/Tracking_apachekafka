import streamlit as st
from components import admin, shipper, customer, tracking, shipping_fee, dashboard
import os



def show():
    """ Hiển thị giao diện menu chính và điều hướng theo vai trò người dùng """

    # ✅ Kiểm tra nếu ảnh tồn tại trước khi hiển thị
   

    st.sidebar.title(f"👤 {st.session_state['username']} ({st.session_state['role']})")

    # ✅ Nút cập nhật thông tin cá nhân
    if st.sidebar.button("🔄 Cập nhật Thông tin"):
        st.session_state["show_profile"] = True

    # ✅ Nút đăng xuất
    if st.sidebar.button("🔴 Đăng xuất"):
        st.session_state["logged_in"] = False
        st.session_state.pop("username", None)
        st.session_state.pop("role", None)
        st.rerun()

    # ✅ Nếu chọn cập nhật thông tin, mở trang cập nhật và dừng menu chính
    if st.session_state.get("show_profile", False):
        from components.customer import update_profile
        update_profile()
        return

    # ✅ Hiển thị danh sách chức năng theo vai trò
    role = st.session_state.get("role", "Khách hàng")

    if role == "Admin":
        option = st.selectbox(
            "🔹 Chọn chức năng",
            ["Dashboard", "Quản lý đơn hàng", "Quản lý người dùng", "Tra cứu đơn hàng", "Tính cước phí", "Phân phối đơn hàng"]
        )
    elif role == "Shipper":
        option = st.selectbox(
            "🔹 Chọn chức năng",
            ["Dashboard", "Tra cứu đơn hàng", "Cập nhật trạng thái đơn hàng"]
        )
    else:  # Khách hàng
        option = st.selectbox(
            "🔹 Chọn chức năng",
            ["Dashboard", "Danh sách đơn hàng", "Tra cứu đơn hàng", "Tính cước phí"]
        )
        # ✅ Thêm vào cuối mỗi trang:
    



    API_BASE_URL = "http://127.0.0.1:8000"

    # ✅ Chuyển hướng đến trang tương ứng
    if option == "Dashboard":
        dashboard.show()
    elif option == "Tra cứu đơn hàng":
        tracking.show()
    elif option == "Tính cước phí":
        shipping_fee.show()
    elif option == "Quản lý đơn hàng" and role == "Admin":
        admin.manage_orders()
    elif option == "Quản lý người dùng" and role == "Admin":
        admin.manage_users()
    elif option == "Phân phối đơn hàng" and role == "Admin":
        admin.assign_orders()
    elif option == "Cập nhật trạng thái đơn hàng" and role == "Shipper":
        shipper.show(API_BASE_URL)
    elif option == "Danh sách đơn hàng" and role == "Khách hàng":
        customer.show()
