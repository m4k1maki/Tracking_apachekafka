import streamlit as st
from backend.producer import send_order_event
from backend.database import SessionLocal, Order, User
from datetime import datetime, timedelta
import uuid



def calculate_shipping_fee(distance, weight, category):
    base_fee = 10000
    distance_fee = distance * 5000
    weight_fee = weight * 3000
    category_multiplier = {"Dễ vỡ": 1.2, "Thực phẩm": 1.1, "Điện tử": 1.3, "Khác": 1.0}
    multiplier = category_multiplier.get(category, 1.0)
    total_fee = (base_fee + distance_fee + weight_fee) * multiplier
    return round(total_fee, 0)


def update_profile():
    st.title("👤 Cập nhật Thông tin cá nhân")
    db = SessionLocal()
    user = db.query(User).filter(User.username == st.session_state["username"]).first()

    if user:
        new_full_name = st.text_input("👤 Họ và tên", value=user.full_name if user.full_name else "")
        new_phone = st.text_input("📞 Số điện thoại", value=user.phone_number if user.phone_number else "")
        new_email = st.text_input("✉️ Email", value=user.email if user.email else "")

        if st.button("💾 Cập nhật"):
            user.full_name = new_full_name
            user.phone_number = new_phone
            user.email = new_email
            db.commit()
            st.success("✅ Thông tin cá nhân đã được cập nhật!")

    if st.button("🔙 Quay lại", key="admin_back"):
        st.session_state["show_profile"] = False
        st.rerun()

    db.close()


def show():
    st.title("Khách hàng - Theo dõi và đặt đơn hàng")

    if st.button("👤 Cập nhật Thông tin"):
        update_profile()

    order_id = str(uuid.uuid4())[:8]  # Cắt ngắn cho gọn (8 ký tự)
    st.write(f"🔢 Mã đơn hàng của bạn: **{order_id}**")

    items = st.text_area("Danh sách hàng hóa (mỗi dòng 1 mặt hàng)")
    address = st.text_input("Địa chỉ giao hàng")

    distance = st.number_input("📏 Khoảng cách (km)", min_value=0.1, step=0.1, value=1.0)
    weight = st.number_input("⚖️ Khối lượng hàng (kg)", min_value=0.1, step=0.1, value=1.0)
    category = st.selectbox("📦 Loại hàng hóa", ["Dễ vỡ", "Thực phẩm", "Điện tử", "Khác"])

    shipping_fee = calculate_shipping_fee(distance, weight, category)
    st.markdown(f"### 💰 Cước phí vận chuyển: **{shipping_fee:,} VNĐ**")

    if st.button("🚀 Tạo đơn hàng"):
        db = SessionLocal()
        existing_order = db.query(Order).filter(Order.order_id == order_id).first()

        if existing_order:
            st.error(f"🚫 Đơn hàng {order_id} đã tồn tại trong hệ thống!")
        else:
            estimated_time = int(distance * 3)
            order = Order(
                order_id=order_id,
                customer=st.session_state["username"],
                address=address,
                items=", ".join(items.split("\n")),
                status="created",
                shipping_fee=shipping_fee,
                estimated_delivery_time=estimated_time
            )
            db.add(order)
            db.commit()
            db.close()

            send_order_event(
                order_id=order_id,
                customer=st.session_state["username"],
                address=address,
                items=", ".join(items.split("\n")),
                distance=distance,
                weight=weight,
                category=category,
                status="Created"
            )

            st.success(f"✅ Đã tạo đơn hàng {order_id} thành công với cước phí **{shipping_fee:,} VNĐ**!")

    st.subheader("📋 Danh sách đơn hàng của bạn")

    db = SessionLocal()
    orders = db.query(Order).filter(Order.customer == st.session_state["username"]).all()
    order_data = []

    for o in orders:
        shipper = db.query(User).filter(User.username == o.assigned_shipper).first()
        shipper_phone = shipper.phone_number if shipper else "Không có"
        customer = db.query(User).filter(User.username == o.customer).first()
        customer_name = customer.full_name if customer and customer.full_name else "Không có"

        delivery_note = ""
        if o.status == "Đã lấy hàng" and o.picked_at:
            created_local = o.created_at + timedelta(hours=7)
            picked_local = o.picked_at + timedelta(hours=7)
            delta = picked_local - created_local
            delivery_note = f"⏱️ Thời gian lấy hàng: {delta.total_seconds() // 60:.0f} phút trước"

        elif o.status == "Đang giao" and o.picked_at:
            delivery_note = f"🚚 Ước tính giao hàng: {o.estimated_delivery_time} phút"

        elif o.status == "Đã giao" and o.delivered_at:
            delivered_local = o.delivered_at + timedelta(hours=7)
            delivery_note = f"✅ Đã giao lúc: {delivered_local.strftime('%H:%M:%S')}"

        order_data.append({
            "Mã đơn": o.order_id,
            "👤 Họ và tên": customer_name,
            "Hàng hóa": o.items,
            "Địa chỉ": o.address,
            "Shipper": o.assigned_shipper or "Chưa phân công",
            "📞 SĐT Shipper": shipper_phone,
            "💰 Cước phí": f"{o.shipping_fee:,} VNĐ",
            "🔄 Trạng thái": o.status,
            "📌 Ghi chú giao hàng": delivery_note
        })

    if order_data:
        st.table(order_data)
    else:
        st.write("Bạn chưa có đơn hàng nào.")

    if st.button("🔙 Quay lại", key="customer_back"):
        st.session_state["show_profile"] = False
        st.rerun()
