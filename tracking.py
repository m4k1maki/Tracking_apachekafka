import streamlit as st
from kafka import KafkaConsumer
import json
from datetime import datetime
from backend.database import SessionLocal, Order, User

# Hàm dùng mapreduce để tra cứu thông tin đơn hàng

def show():
    st.title("🔍 Tra cứu đơn hàng")

    # Tạo Kafka consumer
    consumer = KafkaConsumer(
        "orders",
        bootstrap_servers="localhost:9092",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        group_id="tracking_group",
        auto_offset_reset="earliest",
        enable_auto_commit=False
    )

    # 🔍 Lấy danh sách order_id từ Kafka
    order_ids = set()
    all_messages = []

    records = consumer.poll(timeout_ms=2000, max_records=1000)
    for tp, messages in records.items():
        for msg in messages:
            order = msg.value
            all_messages.append(order)
            if "order_id" in order:
                order_ids.add(str(order["order_id"]))

    consumer.close()

    if not order_ids:
        st.warning("🚫 Không tìm thấy mã đơn hàng trong Kafka.")
        return

    # ✅ Hiển thị danh sách để chọn mã đơn
    selected_order_id = st.selectbox("Chọn mã đơn hàng để tra cứu", sorted(order_ids, reverse=True))

    if st.button("🔍 Tra cứu"):
        # Tìm bản ghi mới nhất trong all_messages
        latest_order = None
        for order in all_messages:
            if str(order.get("order_id")) == selected_order_id:
                latest_order = order

        # Nếu tìm được thì hiển thị thông tin từ Kafka và MySQL
        if latest_order:
            st.success("📦 Đã tìm thấy đơn hàng mới nhất từ Kafka!")

            db = SessionLocal()
            order_db = db.query(Order).filter(Order.order_id == selected_order_id).first()
            customer = db.query(User).filter(User.username == order_db.customer).first() if order_db else None
            shipper = db.query(User).filter(User.username == order_db.assigned_shipper).first() if order_db and order_db.assigned_shipper else None

            # Hiển thị thông tin
            st.write(f"👤 Khách hàng: {customer.full_name if customer and customer.full_name else order_db.customer if order_db else 'Không có dữ liệu'}")
            st.write(f"📍 Địa chỉ: {order_db.address if order_db else 'Không có dữ liệu'}")
            st.write(f"📦 Hàng hóa: {order_db.items if order_db else 'Không có dữ liệu'}")
            st.write(f"🚚 Shipper: {order_db.assigned_shipper if order_db and order_db.assigned_shipper else 'Chưa phân công'}")
            st.write(f"📞 SĐT Shipper: {shipper.phone_number if shipper else 'Không có'}")
            st.write(f"🔄 Trạng thái: {latest_order.get('status', 'Không có dữ liệu')}")

            # ⏱️ Thời gian xử lý
            delivery_note = ""
            if order_db:
                if order_db.status == "Đã lấy hàng" and order_db.picked_at:
                    delta = order_db.picked_at - order_db.created_at
                    delivery_note = f"⏱️ Thời gian lấy hàng: {delta.total_seconds()//60:.0f} phút"
                elif order_db.status == "Đang giao" and order_db.picked_at:
                    delivery_note = f"🚚 Ước tính giao hàng: {order_db.estimated_delivery_time} phút"
                elif order_db.status == "Đã giao" and order_db.delivered_at:
                    delivery_note = f"✅ Đã giao lúc: {order_db.delivered_at.strftime('%H:%M:%S')}"

            if delivery_note:
                st.info(delivery_note)

            db.close()
        else:
            st.warning("❌ Không tìm thấy đơn hàng trong Kafka.")
