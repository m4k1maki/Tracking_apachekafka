from kafka import KafkaConsumer
import json
from collections import Counter
from datetime import datetime
import pandas as pd
from collections import defaultdict


#hàm mapreduce thống kê
def get_order_status_counts():
    consumer = KafkaConsumer(
        "orders",
        bootstrap_servers="localhost:9092",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        group_id="dashboard_group",
        auto_offset_reset="earliest",
        enable_auto_commit=False
    )

    latest_orders = {}

    records = consumer.poll(timeout_ms=3000, max_records=500)
    for tp, messages in records.items():
        for msg in messages:
            order = msg.value
            order_id = order.get("order_id")
            if order_id:
                latest_orders[order_id] = order  # Ghi đè giữ bản ghi mới nhất

    consumer.close()

    # Đếm trạng thái cuối cùng
    from collections import Counter
    status_counter = Counter()
    for order in latest_orders.values():
        status_counter[order.get("status", "Unknown")] += 1

    return dict(status_counter)

#map reduce thống kê theo id và ngày
def get_order_status_counts_by_date(target_date):
    consumer = KafkaConsumer(
        "orders",
        bootstrap_servers="localhost:9092",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        group_id="dashboard_group_by_date",
        auto_offset_reset="earliest",
        enable_auto_commit=False
    )

    latest_orders = {}
    records = consumer.poll(timeout_ms=3000, max_records=1000)

    for tp, messages in records.items():
        for msg in messages:
            order = msg.value
            order_id = order.get("order_id")
            if order_id:
                latest_orders[order_id] = (order, msg.timestamp)  # Lưu bản ghi mới nhất cùng timestamp

    consumer.close()

    # Gom nhóm theo ngày và trạng thái
    result = Counter()
    for order, timestamp in latest_orders.values():
        msg_date = datetime.fromtimestamp(timestamp / 1000.0).strftime('%Y-%m-%d')
        if msg_date == target_date:
            status = order.get("status", "Unknown")
            result[status] += 1

    return dict(result)

