# 🚚 Online Delivery Tracking System with Apache Kafka  

![Kafka](https://img.shields.io/badge/Apache%20Kafka-231F20?style=for-the-badge&logo=apachekafka&logoColor=white)  
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)  
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)  
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)  
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)  

---

## 🧑‍💻 About the Project  
This project was developed as part of the **Big Data course** at HUFLIT.  
It aims to build an **online delivery tracking system** that allows real-time monitoring of orders using **Apache Kafka**.  

Key motivations:  
- Traditional logistics systems often suffer from delays and poor scalability.  
- Customers, shippers, and admins need **real-time updates**.  
- Businesses require a transparent, reliable, and extensible system.  

---

## ✨ Features  

### 👤 Customer  
- Create new orders  
- Track order status in real time  

### 🚴 Shipper  
- View assigned deliveries  
- Update order status (`Created`, `Picked Up`, `Delivering`, `Delivered`)  

### 🛠️ Admin  
- Manage users (add, edit, delete, assign roles)  
- Manage and assign orders to shippers  
- View order statistics & reports (via **MapReduce** on Kafka topics)  
- Search orders quickly without querying database  

---

🛠️ Tech Stack
-Backend: Python, SQLAlchemy, Kafka-Python
-Frontend: Streamlit
-Database: MySQL
-Big Data: Apache Kafka, MapReduce (Python implementation)
-DevOps: Docker, Docker Compose
⚙️ Installation
1.Clone repository
2.Run Kafka & Zookeeper via Docker
3.Install dependencies
4.Start Streamlit App

📊 Demo
Customer View
Create orders, view status in real time
Shipper View
Update delivery status (Picked Up, Delivering, Delivered)
Admin View
Manage orders & users
Real-time statistics (MapReduce on Kafka topics)
📫 Contact
📧 Email: uongthanhtrung2004@gmail.com
    Admin --> F
    Shipper --> F
