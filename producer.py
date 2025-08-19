from kafka import KafkaProducer
from backend.database import SessionLocal, Order
import json

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def send_order_event(order_id, customer="", address="", items=None, distance=None, weight=None, category="", status="Created"):
    """
    Gửi đơn hàng hoặc cập nhật trạng thái đơn hàng lên Kafka.
    Nếu chỉ truyền order_id và status thì tự động lấy dữ liệu đơn hàng từ DB để gửi đầy đủ.
    """
    order = {
        "order_id": order_id,
        "status": status
    }

    # Nếu chỉ có order_id và status => Lấy dữ liệu từ DB
    if not (customer or address or items or distance or weight or category):
        db = SessionLocal()
        existing_order = db.query(Order).filter(Order.order_id == order_id).first()
        db.close()

        if existing_order:
            order["customer"] = existing_order.customer
            order["address"] = existing_order.address
            order["items"] = existing_order.items
            order["distance"] = getattr(existing_order, "distance", 0)
            order["weight"] = getattr(existing_order, "weight", 0)
            order["category"] = getattr(existing_order, "category", "Không xác định")
    else:
        # Trường hợp tạo đơn mới hoặc cập nhật có đủ thông tin
        if customer: order["customer"] = customer
        if address: order["address"] = address
        if items: order["items"] = items
        if distance is not None: order["distance"] = distance
        if weight is not None: order["weight"] = weight
        if category: order["category"] = category

    # Kiểm tra trước khi gửi
    print(f"Gửi dữ liệu vào Kafka: {order}")
    producer.send("orders", value=order)
    producer.flush()
    print(f"📤 Đã gửi dữ liệu vào Kafka: {order}")

