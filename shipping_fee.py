import streamlit as st

def calculate_shipping_fee(distance, weight, category):
    """Tính cước phí dựa trên khoảng cách, khối lượng và loại hàng"""
    base_fee = 10000  # Phí cố định
    distance_fee = distance * 5000  # 5000đ/km
    weight_fee = weight * 3000  # 3000đ/kg
    
    category_multiplier = {"Dễ vỡ": 1.2, "Thực phẩm": 1.1, "Điện tử": 1.3, "Khác": 1.0}
    multiplier = category_multiplier.get(category, 1.0)
    
    total_fee = (base_fee + distance_fee + weight_fee) * multiplier
    return round(total_fee, 0)  # Làm tròn số

def show():
    st.title("💰 Tính cước phí vận chuyển")

    weight = st.number_input("⚖️ Cân nặng (kg)", min_value=0.1, step=0.1, value=1.0)
    distance = st.number_input("📏 Khoảng cách (km)", min_value=0.1, step=0.1, value=1.0)
    category = st.selectbox("📦 Loại hàng hóa", ["Dễ vỡ", "Thực phẩm", "Điện tử", "Khác"])

    if st.button("🚀 Tính phí"):
        fee = calculate_shipping_fee(distance, weight, category)
        st.success(f"💰 Cước phí vận chuyển: **{fee:,} VND**")
# ✅ Thêm vào cuối mỗi trang:
   

