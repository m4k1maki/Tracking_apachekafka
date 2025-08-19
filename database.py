from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import datetime

import bcrypt

# Cấu hình kết nối MySQL
DATABASE_URL = "mysql+mysqlconnector://root:hoangvuzent9520%40@localhost:3306/tracking_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False)  # Vai trò: "Khách hàng", "Shipper", "Admin"
    phone_number = Column(String(15), nullable=True)  # Thêm số điện thoại
    email = Column(String(100), nullable=True)  # Thêm email

   
class Order(Base):
    __tablename__ = "orders"

    order_id = Column(String(50), primary_key=True, index=True)
    customer = Column(String(50), nullable=False)
    address = Column(String(255), nullable=False)
    items = Column(String(500), nullable=False)  #  dạng chuỗi thay vì list
    status = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)# tg tạo hàng
    assigned_shipper = Column(String(50), nullable=True)
    shipping_fee = Column(Float, nullable=True)
    picked_at = Column(DateTime, nullable=True)# tg lấy hàng
    delivered_at = Column(DateTime, nullable=True)#tg giao hàng hoàn thành
    estimated_delivery_time = Column(Integer, nullable=True)# tg dự tính giao

# ✅ Hàm mã hóa mật khẩu trước khi lưu vào database
def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

# ✅ Tạo tài khoản mặc định nếu chưa tồn tại
def create_default_users():
    db = SessionLocal()
    
    default_users = [
        {"username": "admin", "password": hash_password("123"), "role": "Admin"},
        {"username": "shipper", "password": hash_password("123"), "role": "Shipper"}
    ]

    for user_data in default_users:  # Đổi tên biến từ `user` -> `user_data` để tránh nhầm lẫn
        existing_user = db.query(User).filter(User.username == user_data["username"]).first()
        
        if not existing_user:
            new_user = User(
                username=user_data["username"],
                password=user_data["password"],  # Chắc chắn lấy từ danh sách
                role=user_data["role"]
            )
            db.add(new_user)
        else:
            # Kiểm tra nếu mật khẩu chưa được hash thì hash lại
            if not existing_user.password.startswith("$2b$"):
                existing_user.password = hash_password(existing_user.password)

    db.commit()
    db.close()


# ✅ Chạy hàm khi hệ thống khởi động
create_default_users()
Base.metadata.create_all(bind=engine)