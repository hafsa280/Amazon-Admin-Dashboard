from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

ADMIN_NAME = "admin"  # In production, replace this with actual session context

# ---------------- USERS ----------------
@router.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    created_user = crud.create_user(db, user)
    crud.log_admin_activity(db, admin_name=ADMIN_NAME, action="add", target_table="users")
    return created_user

@router.get("/users/", response_model=list[schemas.User])
def read_users(db: Session = Depends(get_db)):
    return crud.get_users(db)

@router.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserCreate, db: Session = Depends(get_db)):
    updated_user = crud.update_user(db, user_id, user)
    crud.log_admin_activity(db, admin_name=ADMIN_NAME, action="update", target_table="users")
    return updated_user

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_user(db, user_id)
    crud.log_admin_activity(db, admin_name=ADMIN_NAME, action="delete", target_table="users")
    return deleted

# ---------------- PRODUCTS ----------------
@router.post("/products/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    created_product = crud.create_product(db, product)
    crud.log_admin_activity(db, admin_name=ADMIN_NAME, action="add", target_table="products")
    return created_product

@router.get("/products/", response_model=list[schemas.Product])
def read_products(db: Session = Depends(get_db)):
    return crud.get_products(db)

@router.put("/products/{product_id}", response_model=schemas.Product)
def update_product(product_id: int, product: schemas.ProductCreate, db: Session = Depends(get_db)):
    updated_product = crud.update_product(db, product_id, product)
    crud.log_admin_activity(db, admin_name=ADMIN_NAME, action="update", target_table="products")
    return updated_product

@router.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_product(db, product_id)
    crud.log_admin_activity(db, admin_name=ADMIN_NAME, action="delete", target_table="products")
    return deleted

# ---------------- ORDERS ----------------
@router.post("/orders/", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    created_order = crud.create_order(db, order)
    crud.log_admin_activity(db, admin_name=ADMIN_NAME, action="add", target_table="orders")
    return created_order

@router.get("/orders/", response_model=list[schemas.Order])
def read_all_orders(db: Session = Depends(get_db)):
    return crud.get_orders(db)

@router.get("/orders/user/{user_id}", response_model=list[schemas.Order])
def read_orders_by_user(user_id: int, db: Session = Depends(get_db)):
    return crud.get_orders_by_user(db, user_id)

@router.put("/orders/{order_id}", response_model=schemas.Order)
def update_order(order_id: int, order: schemas.OrderCreate, db: Session = Depends(get_db)):
    updated_order = crud.update_order(db, order_id, order)
    crud.log_admin_activity(db, admin_name=ADMIN_NAME, action="update", target_table="orders")
    return updated_order

@router.delete("/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_order(db, order_id)
    crud.log_admin_activity(db, admin_name=ADMIN_NAME, action="delete", target_table="orders")
    return deleted


@router.get("/admin-logs", response_model=list[schemas.AdminActivityLog])
def get_logs(db: Session = Depends(get_db)):
    return crud.get_admin_logs(db)
