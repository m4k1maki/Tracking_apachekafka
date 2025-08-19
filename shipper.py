import streamlit as st
from backend.database import SessionLocal, Order, User
from backend.producer import send_order_event
from datetime import datetime

def show(API_BASE_URL):
    """ Hiển thị danh sách đơn hàng của shipper và cho phép cập nhật trạng thái """
    st.title("🚚 Đơn hàng của bạn")

    db = SessionLocal()
    username = st.session_state.get("username", "")

    # Lấy danh sách đơn hàng được phân cho shipper này
    orders = db.query(Order).filter(Order.assigned_shipper == username).all()

    order_data = []
    for o in orders:
        customer = db.query(User).filter(User.username == o.customer).first()
        customer_phone = customer.phone_number if customer else "Không có"

        pickup_time = o.picked_at.strftime("%H:%M") if o.picked_at else "Chưa lấy hàng"
        delivery_time = o.delivered_at.strftime("%H:%M") if o.delivered_at else "Chưa giao hàng"

        order_data.append({
            "Mã đơn": o.order_id,
            "Khách hàng": o.customer,
            "📞 SĐT Khách hàng": customer_phone,
            "Địa chỉ": o.address,
            "Hàng hóa": o.items,
            "Trạng thái": o.status,
            "Thời điểm lấy hàng": pickup_time,
            "Thời điểm giao hàng": delivery_time,
            "Cước phí": f"{o.shipping_fee:,} VND"
        })

    db.close()

    if order_data:
        st.table(order_data)
    else:
        st.write("🚫 Bạn chưa có đơn hàng nào.")

    # ✅ Chọn mã đơn hàng từ danh sách có sẵn
    st.subheader("📦 Cập nhật trạng thái đơn hàng")
    order_id = st.selectbox("Chọn mã đơn hàng", [o.order_id for o in orders])
    new_status = st.selectbox("Trạng thái mới", ["Đã lấy hàng", "Đang giao", "Đã giao"])

    if st.button("✅ Cập nhật trạng thái"):
        db = SessionLocal()
        order = db.query(Order).filter(Order.order_id == order_id, Order.assigned_shipper == username).first()
        if order:
            order.status = new_status

            # Ghi lại thời điểm tương ứng
            if new_status == "Đã lấy hàng":
                order.picked_at = datetime.utcnow()
            elif new_status == "Đã giao":
                order.delivered_at = datetime.utcnow()

            db.commit()
            db.close()

            # ✅ Gửi sự kiện cập nhật trạng thái lên Kafka
            send_order_event(order_id=order_id, status=new_status)

            st.success(f"✅ Đã cập nhật trạng thái đơn hàng {order_id} thành {new_status}")
            st.rerun()
        else:
            st.error("🚫 Không tìm thấy đơn hàng hoặc bạn không được giao đơn hàng này.")

    # ✅ Nút quay lại menu chính
    if st.button("🔙 Quay lại", key="shipper_back"):
        st.session_state["show_profile"] = False
        st.rerun()
