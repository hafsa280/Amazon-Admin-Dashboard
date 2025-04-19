from pydantic import BaseModel
from typing import Optional

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

    class Config:
        orm_mode = True

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