from kafka import KafkaConsumer
import json

# Khôi phục consumer cũ không lưu HDFS
consumer = KafkaConsumer(
    "orders",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    group_id="orders_group",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    consumer_timeout_ms=1000
)

# Xử lý dữ liệu Kafka như bình thường
print("🟢 Kafka consumer đang lắng nghe topic 'orders'...")

for msg in consumer:
    order = msg.value
    print("\n📦 Nhận đơn hàng:")
    print(f"- Mã đơn: {order.get('order_id')}")
    print(f"- Khách hàng: {order.get('customer')}")
    print(f"- Địa chỉ: {order.get('address')}")
    print(f"- Hàng hoá: {order.get('items')}")
    print(f"- Khoảng cách: {order.get('distance')} km")
    print(f"- Khối lượng: {order.get('weight')} kg")
    print(f"- Loại hàng: {order.get('category')}")
    print(f"📦 Đơn hàng nhận: {order}")
    order_id = order.get("order_id")
    status = order.get("status")
     # Lấy lại thông tin cũ nếu cần
    if status == "Đang giao":
        # Thực hiện cập nhật hoặc xử lý thông tin cũ nếu cần
        print(f"Đơn hàng {order_id} đang giao")
    elif status == "Đã giao":
        # Xử lý khi trạng thái đã giao
        print(f"Đơn hàng {order_id} đã giao")
    else:
        # Trạng thái mặc định
        print(f"Đơn hàng {order_id} có trạng thái khác")

print("✅ Kết thúc lắng nghe Kafka.")
