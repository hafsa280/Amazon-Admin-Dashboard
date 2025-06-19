from sqlalchemy import Column, Integer, String, Text, DECIMAL, ForeignKey, Enum, Float, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True, autoincrement=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    role = Column(Enum("customer", "seller", "admin", name="user_roles"), nullable=False)
    orders = relationship("Order", back_populates="user")


class Product(Base):
    __tablename__ = "products"
    product_id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.user_id"))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    stock = Column(Integer, nullable=False)
    category = Column(String(100), nullable=True)
    
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    total_amount = Column(Float)
    status = Column(String, default="pending")
    order_date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="orders")
    
class AdminActivityLog(Base):
    __tablename__ = "admin_activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_name = Column(String, nullable=False)
    action = Column(String, nullable=False)  # e.g., add/update/delete
    target_table = Column(String, nullable=False)  # e.g., users/products/orders
    timestamp = Column(DateTime, default=datetime.utcnow)
