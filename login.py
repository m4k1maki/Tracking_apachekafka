import streamlit as st
from backend.database import SessionLocal, User  # Import User từ database
from sqlalchemy.exc import IntegrityError
import bcrypt  # ✅ Thêm bcrypt để hash mật khẩu

def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def check_password(hashed_password, plain_password):
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def login_page():
    st.title("🔐 Đăng nhập hệ thống")

    menu = st.radio("Chọn hành động", ["Đăng nhập", "Đăng ký"])

    if menu == "Đăng nhập":
        username = st.text_input("🆔 Tài khoản")
        password = st.text_input("🔑 Mật khẩu", type="password")

        if st.button("Đăng nhập"):
            db = SessionLocal()
            user = db.query(User).filter(User.username == username).first()
            db.close()

            if user and check_password(user.password, password):
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["role"] = user.role
                st.success(f"🎉 Đăng nhập thành công! Xin chào {username}!")
                st.rerun()
            else:
                st.error("❌ Sai tài khoản hoặc mật khẩu!")

    elif menu == "Đăng ký":
        new_username = st.text_input("🆕 Tài khoản mới")
        new_password = st.text_input("🔑 Mật khẩu mới", type="password")

        if st.button("Đăng ký"):
            db = SessionLocal()
            hashed_password = hash_password(new_password)  # Hash mật khẩu trước khi lưu
            new_user = User(username=new_username, password=hashed_password, role="Khách hàng")

            try:
                db.add(new_user)
                db.commit()
                st.success("✅ Đăng ký thành công! Vui lòng đăng nhập.")
            except IntegrityError:
                db.rollback()
                st.error("❌ Tên tài khoản đã tồn tại!")
            finally:
                db.close()