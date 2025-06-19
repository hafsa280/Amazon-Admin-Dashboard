from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ------------------ USER ------------------ #

class UserBase(BaseModel):
    name: str
    email: str
    phone_number: Optional[str]
    address: Optional[str]
    role: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    user_id: int
    password: str

    class Config:
        orm_mode = True

# ------------------ PRODUCT ------------------ #

class ProductBase(BaseModel):
    name: str
    description: Optional[str]
    price: float
    stock: int
    category: Optional[str]

class ProductCreate(ProductBase):
    seller_id: int

class Product(ProductBase):
    product_id: int
    seller_id: int

    class Config:
        orm_mode = True

# ------------------ ORDER ------------------ #

class OrderBase(BaseModel):
    total_amount: float
    status: Optional[str] = "pending"

class OrderCreate(OrderBase):
    user_id: int

class Order(OrderBase):
    id: int
    user_id: int
    order_date: datetime

    class Config:
        from_attributes = True
