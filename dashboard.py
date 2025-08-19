import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime
from backend.kafka_mapreduce import get_order_status_counts, get_order_status_counts_by_date
from datetime import datetime 
from backend.database import SessionLocal, Order, User  # Lấy dữ liệu từ DB

def show():
    st.title("📊 Dashboard - Tổng quan hệ thống")

    # Lấy vai trò người dùng hiện tại
    role = st.session_state.get("role", "Khách hàng")

    db = SessionLocal()

    # ------------- HIỂN THỊ SỐ LIỆU CHUNG -------------
    if role == "Admin":
        total_orders = db.query(Order).count()
        total_shippers = db.query(User).filter(User.role == "Shipper").count()
        total_customers = db.query(User).filter(User.role == "Khách hàng").count()

        col1, col2, col3 = st.columns(3)
        col1.metric("📦 Tổng số đơn hàng", total_orders)
        col2.metric("🚚 Số lượng shipper", total_shippers)
        col3.metric("👥 Số lượng khách hàng", total_customers)

         # 🔄 LẤY THỐNG KÊ TỪ KAFKA (MAPREDUCE) truy vấn từ kafka_mapreduce
        st.subheader("📊 Thống kê đơn hàng")

        st.markdown("## 📊 Thống kê trạng thái đơn hàng từ Kafka (Interactive 🎨)")

        selected_date = st.date_input("🗓 Chọn ngày thống kê", value=datetime.today())
        status_counts = get_order_status_counts_by_date(str(selected_date))

        if status_counts:
            df = pd.DataFrame({
                "Trạng thái": list(status_counts.keys()),
                "Số lượng": list(status_counts.values())
            })

            fig = px.bar(
                df,
                x="Trạng thái",
                y="Số lượng",
                color="Trạng thái",
                text="Số lượng",
                title=f"📦 Biểu đồ Trạng thái Đơn hàng (Kafka) - {selected_date}",
                color_discrete_sequence=px.colors.qualitative.Set3
            )

            fig.update_layout(
                xaxis_title="Trạng thái đơn hàng",
                yaxis_title="Số lượng",
                title_font_size=20,
                template="plotly_white"
            )

            st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")
            st.subheader("📄 Thống kê nhanh")
            st.write(f"📦 Đơn đang lấy hàng: **{status_counts.get('Đã lấy hàng', 0)}**")
            st.write(f"🚚 Đơn đang giao: **{status_counts.get('Đang giao', 0)}**")
            st.write(f"✅ Đơn đã giao: **{status_counts.get('Đã giao', 0)}**")
            st.write(f"❌ Đơn đã hủy: **{status_counts.get('Hủy đơn', 0)}**")
        else:
            st.info("⚠️ Chưa có dữ liệu đơn hàng trong Kafka.")

    elif role == "Shipper":
        st.subheader("🚚 Đơn hàng đang giao")
        ongoing_orders = db.query(Order).filter(Order.status == "Đang giao").all()
        st.write(f"Bạn có {len(ongoing_orders)} đơn hàng đang giao.")

        if ongoing_orders:
            st.table([{ "Mã đơn": o.order_id, "Địa chỉ": o.address, "Trạng thái": o.status } for o in ongoing_orders])

    else:  # Khách hàng
        st.subheader("📦 Đơn hàng của bạn")
        customer_orders = db.query(Order).filter(Order.customer == st.session_state["username"]).all()
        
        if customer_orders:
            st.table([{ "Mã đơn": o.order_id, "Trạng thái": o.status } for o in customer_orders])
        else:
            st.write("Bạn chưa có đơn hàng nào.")

    db.close()
   
    if st.button("🔙 Quay lại", key="dashboard_back"):
        st.session_state["show_profile"] = False
        st.rerun()


