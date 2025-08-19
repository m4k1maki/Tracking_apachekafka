import streamlit as st
from backend.database import SessionLocal, User, Order
from sqlalchemy.exc import IntegrityError
from kafka import KafkaConsumer
from backend.producer import send_order_event
import json
from collections import defaultdict
import random

def show():
    st.title("Admin - Quản lý Hệ thống")

    menu = st.radio("Chọn chức năng", ["Quản lý Đơn hàng", "Quản lý Người dùng", "Thống kê đơn hàng"])

    if menu == "Quản lý Đơn hàng":
        manage_orders()
    elif menu == "Quản lý Người dùng":
        manage_users()
    elif menu == "Thống kê đơn hàng":
        order_statistics()

# 📌 Quản lý người dùng (Khách hàng & Shipper)
def manage_users():
    st.subheader("📌 Quản lý Người dùng")

    db = SessionLocal()
    users = db.query(User).all()

    show_users(users)

    # 🔍 Tìm kiếm người dùng
    search_user = st.text_input("🔍 Nhập tên tài khoản để tìm kiếm")
    if st.button("Tìm kiếm"):
        user = db.query(User).filter(User.username == search_user).first()
        if user:
            st.success(f"👤 Tìm thấy: {user.username} - Vai trò: {user.role}")
        else:
            st.error("🚫 Không tìm thấy tài khoản!")

    # ➕ Thêm người dùng mới
    st.subheader("➕ Thêm Người dùng")
    new_username = st.text_input("Tên tài khoản mới")
    new_password = st.text_input("Mật khẩu", type="password")
    role = st.selectbox("Chọn vai trò", ["Khách hàng", "Shipper", "Admin"])

    if st.button("Thêm Người dùng"):
        try:
            new_user = User(username=new_username, password=new_password, role=role)
            db.add(new_user)
            db.commit()
            st.success(f"✅ Đã thêm {new_username} ({role}) thành công!")
        except IntegrityError:
            db.rollback()
            st.error("🚫 Tên tài khoản đã tồn tại!")

    # ✏️ Chỉnh sửa người dùng
    st.subheader("✏️ Chỉnh sửa Người dùng")
    edit_username = st.text_input("Nhập tên tài khoản cần sửa")
    if st.button("Tải thông tin người dùng"):
        user = db.query(User).filter(User.username == edit_username).first()
        if user:
            new_role = st.selectbox("🛠️ Vai trò mới", ["Khách hàng", "Shipper", "Admin"], index=["Khách hàng", "Shipper", "Admin"].index(user.role))
            new_password = st.text_input("🔒 Mật khẩu mới (để trống nếu không đổi)", type="password")
            new_email = st.text_input("✉️ Email", value=user.email if user.email else "")
            new_phone = st.text_input("📞 Số điện thoại", value=user.phone_number if user.phone_number else "")

            if st.button("Lưu thay đổi"):
                user.role = new_role
                if new_password.strip():
                    user.password = new_password
                user.email = new_email
                user.phone_number = new_phone
                db.commit()
                st.success(f"✅ Đã cập nhật thông tin tài khoản {edit_username}")
        else:
            st.error("🚫 Không tìm thấy tài khoản!")

    # ❌ Xóa người dùng
    st.subheader("❌ Xóa Người dùng")
    delete_user = st.text_input("Nhập tên tài khoản để xóa")
    if st.button("Xóa"):
        user = db.query(User).filter(User.username == delete_user).first()
        if user:
            db.delete(user)
            db.commit()
            st.success(f"✅ Đã xóa tài khoản {delete_user}")
        else:
            st.error("🚫 Không tìm thấy tài khoản!")

    db.close()


# 📌 Quản lý đơn hàng (Tìm kiếm, Sửa, Xóa)
def manage_orders():
    st.subheader("📌 Quản lý Đơn hàng")

    db = SessionLocal()
    orders = db.query(Order).all()

    show_orders(orders)

    # Tìm kiếm đơn hàng
    search_order = st.text_input("🔍 Nhập mã đơn để tìm kiếm")
    if st.button("Tìm kiếm đơn hàng"):
        order = db.query(Order).filter(Order.order_id == search_order).first()
        if order:
            st.success(f"📦 Tìm thấy đơn hàng: {order.order_id} - Trạng thái: {order.status}")
        else:
            st.error("🚫 Không tìm thấy đơn hàng!")

    # Sửa trạng thái đơn hàng
    st.subheader("✏️ Chỉnh sửa trạng thái đơn hàng")
    order_id = st.text_input("Nhập mã đơn cần cập nhật")
    new_status = st.selectbox("Chọn trạng thái mới", ["Created", "Đã lấy hàng", "Đang giao", "Đã giao", "Hủy đơn"])

    if st.button("Cập nhật trạng thái"):
        order = db.query(Order).filter(Order.order_id == order_id).first()
        if order:
            order.status = new_status
            db.commit()

            # ✅ Gửi cập nhật trạng thái lên Kafka
            send_order_event(order_id=order_id, status=new_status)

            st.success(f"✅ Đã cập nhật trạng thái đơn hàng {order_id} thành {new_status}")
            st.rerun()
        else:
            st.error("🚫 Không tìm thấy đơn hàng!")

    # Xóa đơn hàng
    st.subheader("🗑️ Xóa đơn hàng")
    delete_order = st.text_input("Nhập mã đơn cần xóa")
    if st.button("Xóa đơn hàng"):
        order = db.query(Order).filter(Order.order_id == delete_order).first()
        if order:
            db.delete(order)
            db.commit()
            st.success(f"✅ Đã xóa đơn hàng {delete_order}")
        else:
            st.error("🚫 Không tìm thấy đơn hàng!")

    db.close()

# 📊 Thống kê đơn hàng
def order_statistics():
    st.subheader("📊 Thống kê đơn hàng (dữ liệu từ Kafka)")

    # Tạo Kafka Consumer
    consumer = KafkaConsumer(
        "orders",
        bootstrap_servers="localhost:9092",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        group_id="statistics_group",
        auto_offset_reset="earliest",
        enable_auto_commit=False
    )

    # MapReduce mini: đếm trạng thái
    status_counter = defaultdict(int)

    for msg in consumer:
        order = msg.value
        status = order.get("status")

        if status:
            status_counter[status] += 1

    consumer.close()

    # Hiển thị kết quả trên giao diện Streamlit
    total = sum(status_counter.values())
    st.write(f"📦 Tổng số đơn hàng: **{total}**")
    for k, v in status_counter.items():
        emoji = "✅" if "giao" in k.lower() else "❌" if "hủy" in k.lower() else "🔄"
        st.write(f"{emoji} {k}: **{v}**")


def assign_orders():
    """ Admin phân phối đơn hàng ngẫu nhiên cho shipper """
    st.title("📦 Phân phối đơn hàng cho Shipper")

    db = SessionLocal()
    
    # Lấy danh sách đơn hàng chưa có shipper
    unassigned_orders = db.query(Order).filter(Order.assigned_shipper == None).all()
    shippers = db.query(User).filter(User.role == "Shipper").all()

    # Hiển thị danh sách đơn hàng đã phân phối
    st.subheader("📋 Danh sách đơn hàng đã phân phối")
    assigned_orders = db.query(Order).filter(Order.assigned_shipper != None).all()
    
    if assigned_orders:
        st.table([
            {
                "Mã đơn": o.order_id,
                "Khách hàng": o.customer,
                "Shipper": o.assigned_shipper,
                "Trạng thái": o.status
            } for o in assigned_orders
        ])
    else:
        st.write("🚫 Hiện chưa có đơn hàng nào được giao cho shipper.")

    # ✅ Hiển thị nút phân phối đơn hàng ngay cả khi đã có đơn hàng được phân phối trước đó
    if not shippers:
        st.error("🚨 Không có shipper nào trong hệ thống!")
        db.close()
        return

    if st.button("🚀 Phân phối đơn hàng"):
        if not unassigned_orders:
            st.success("✅ Tất cả đơn hàng đã được phân công. Phân phối lại toàn bộ đơn hàng.")
            all_orders = db.query(Order).all()
            for order in all_orders:
                assigned_shipper = random.choice(shippers)
                order.assigned_shipper = assigned_shipper.username
            db.commit()
            st.rerun()
        else:
            for order in unassigned_orders:
                assigned_shipper = random.choice(shippers)
                order.assigned_shipper = assigned_shipper.username
            db.commit()
            st.success("✅ Đã phân phối đơn hàng thành công!")
            st.rerun()

    db.close()

def show_orders(orders):
    st.subheader("📋 Danh sách Đơn hàng")
    st.table([{
        "Mã đơn": o.order_id,
        "Khách hàng": o.customer,
        "Địa chỉ": o.address,
        "Hàng hóa": o.items,
        "Trạng thái": o.status
    } for o in orders])

def show_users(users):
    st.subheader("📋 Danh sách Người dùng")
    st.table([{
        "ID": u.id,
        "Tên tài khoản": u.username,
        "Vai trò": u.role
    } for u in users])
