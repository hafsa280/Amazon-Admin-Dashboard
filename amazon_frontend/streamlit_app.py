import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import re

API_URL = "http://backend:8000"
st.set_page_config(page_title="Amazon Admin", layout="wide")

# ----------------- AUTHENTICATION -----------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "login_error" not in st.session_state:
    st.session_state.login_error = False

if not st.session_state.authenticated:
    st.title("🔒 Admin Login")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        login = st.form_submit_button("Login")

    if login:
        users = requests.get(f"{API_URL}/users/").json()
        for user in users:
            if user['email'] == email and user['password'] == password and user['role'] == 'admin':
                st.session_state.authenticated = True
                st.rerun()
        st.session_state.login_error = True

    if st.session_state.login_error:
        st.error("Invalid credentials or not an admin user.")
    st.stop()

# ----------------- SESSION INIT -----------------
if "page" not in st.session_state:
    st.session_state.page = "home"
if "form_reset" not in st.session_state:
    st.session_state.form_reset = False

# ----------------- DATA FETCH -----------------
def refresh_data():
    st.session_state.users_data = requests.get(f"{API_URL}/users/").json()
    st.session_state.products_data = requests.get(f"{API_URL}/products/").json()
    st.session_state.orders_data = requests.get(f"{API_URL}/orders/").json()

refresh_data()

# ----------------- HELPERS -----------------
def get_unique_categories():
    return sorted(set([p['category'] for p in st.session_state.products_data if p['category']]))

def is_valid_email(email):
    return re.match(r"[^@\s]+@[^@\s]+\.[a-zA-Z0-9]+$", email)

# ----------------- SIDEBAR -----------------
st.sidebar.title("Navigation")
st.session_state.page = st.sidebar.radio("Go to", ["Home", "Users", "Products", "Orders"])

# ----------------- HOME PAGE -----------------
if st.session_state.page == "Home":
    st.title("Amazon Admin Dashboard")
    st.write("Welcome! Use the sidebar to manage Users, Products, and Orders.")
# ----------------- USERS PAGE -----------------

elif st.session_state.page == "Users":
    st.title("👤 Manage Users")

    with st.expander("➕ Add New User"):
        with st.form("user_form"):
            name = st.text_input("Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            phone = st.text_input("Phone")
            role = st.selectbox("Role", ["customer", "seller"])  # removed "admin"
            address = st.text_area("Address")
            submit = st.form_submit_button("Create User")

            if submit:
                if not name or not email or not password:
                    st.error("Name, Email, and Password are required.")
                elif not is_valid_email(email):
                    st.error("Invalid email format.")
                else:
                    data = {
                        "name": name,
                        "email": email,
                        "password": password,
                        "phone_number": phone,
                        "address": address,
                        "role": role
                    }
                    res = requests.post(f"{API_URL}/users/", json=data)
                    if res.ok:
                        st.success("User created successfully.")
                        refresh_data()
                    else:
                        st.error("Failed to create user.")

    if st.session_state.users_data:
        user_ids = [f"{u['user_id']} - {u['email']}" for u in st.session_state.users_data]
        selected = st.selectbox("Select user to update/delete:", ["None"] + user_ids)

        if selected != "None":
            user_id = int(selected.split(" - ")[0])
            user = next(u for u in st.session_state.users_data if u['user_id'] == user_id)

            is_admin = user['role'] == 'admin'

            if is_admin:
                st.warning("⚠️ Admin users cannot be updated or deleted.")
            else:
                st.subheader("✏️ Update User")
                with st.form("edit_user_form"):
                    new_name = st.text_input("Name", user['name'])
                    new_email = st.text_input("Email", user['email'])
                    new_password = st.text_input("Password", type="password")
                    new_phone = st.text_input("Phone", user.get('phone_number', ''))
                    new_address = st.text_area("Address", user.get('address', ''))
                    new_role = st.selectbox("Role", ["customer", "seller"], index=["customer", "seller"].index(user['role']))
                    update_btn = st.form_submit_button("Update")

                    if update_btn:
                        updated_data = {
                            "name": new_name,
                            "email": new_email,
                            "password": new_password,
                            "phone_number": new_phone,
                            "address": new_address,
                            "role": new_role
                        }
                        res = requests.put(f"{API_URL}/users/{user_id}", json=updated_data)
                        if res.ok:
                            st.success("User updated.")
                            refresh_data()
                        else:
                            st.error("Update failed.")

                if st.button("🗑️ Delete This User"):
                    res = requests.delete(f"{API_URL}/users/{user_id}")
                    if res.ok:
                        st.success("User deleted.")
                        refresh_data()
                    else:
                        st.error("Failed to delete user.")

# ----------------- PRODUCTS PAGE -----------------
elif st.session_state.page == "Products":
    st.title("📦 Manage Products")
    with st.expander("➕ Add New Product"):
        with st.form("product_form"):
            name = st.text_input("Product Name")
            description = st.text_input("Description")
            price = st.number_input("Price", min_value=0.01)
            stock = st.number_input("Stock", min_value=0)
            category = st.text_input("Category")
            seller_id = st.number_input("Seller ID", min_value=1, step=1)
            submit = st.form_submit_button("Create Product")

            if submit:
                if not name:
                    st.error("Product name is required.")
                elif price <= 0 or stock < 0:
                    st.error("Invalid price or stock values.")
                elif seller_id <= 0:
                    st.error("Invalid seller ID.")
                else:
                    product_data = {
                        "name": name,
                        "description": description,
                        "price": price,
                        "stock": stock,
                        "category": category,
                        "seller_id": seller_id
                    }
                    res = requests.post(f"{API_URL}/products/", json=product_data)
                    if res.ok:
                        st.success("Product created successfully.")
                        refresh_data()
                    else:
                        st.error("Failed to create product.")

    if st.session_state.products_data:
        product_ids = [f"{p['product_id']} - {p['name']}" for p in st.session_state.products_data]
        selected = st.selectbox("Select product to update/delete:", ["None"] + product_ids)
        if selected != "None":
            product_id = int(selected.split(" - ")[0])
            product = next(p for p in st.session_state.products_data if p['product_id'] == product_id)

            st.subheader("✏️ Update Product")
            with st.form("edit_product_form"):
                new_name = st.text_input("Product Name", product['name'])
                new_description = st.text_input("Description", product['description'])
                new_price = st.number_input("Price", min_value=0.01, value=product['price'])
                new_stock = st.number_input("Stock", min_value=0, value=product['stock'])
                new_category = st.text_input("Category", product['category'])
                new_seller_id = st.number_input("Seller ID", min_value=1, step=1, value=product['seller_id'])
                update_btn = st.form_submit_button("Update")
                if update_btn:
                    updated_product = {
                        "name": new_name,
                        "description": new_description,
                        "price": new_price,
                        "stock": new_stock,
                        "category": new_category,
                        "seller_id": new_seller_id
                    }
                    res = requests.put(f"{API_URL}/products/{product_id}", json=updated_product)
                    if res.ok:
                        st.success("Product updated.")
                        refresh_data()
                    else:
                        st.error("Update failed.")

            if st.button("🗑️ Delete This Product"):
                res = requests.delete(f"{API_URL}/products/{product_id}")
                if res.ok:
                    st.success("Product deleted.")
                    refresh_data()
                else:
                    st.error("Failed to delete product.")
                    
# ----------------- ORDERS PAGE -----------------
elif st.session_state.page == "Orders":
    st.title("🛒 Manage Orders")
    st.write(f"Total Orders: {len(st.session_state.orders_data)}")

    with st.expander("➕ Create New Order"):
        with st.form("order_form"):
            user_id = st.number_input("User ID", min_value=1, step=1)
            total_amount = st.number_input("Total Amount", min_value=0.01)
            status = st.selectbox("Order Status", ["pending", "shipped", "delivered", "cancelled"])
            submit = st.form_submit_button("Create Order")

            if submit:
                if user_id <= 0 or total_amount <= 0:
                    st.error("Invalid input. Please ensure all fields are filled correctly.")
                else:
                    order_data = {
                        "user_id": user_id,
                        "total_amount": total_amount,
                        "status": status
                    }
                    res = requests.post(f"{API_URL}/orders/", json=order_data)
                    if res.ok:
                        st.success("Order created successfully.")
                        refresh_data()
                    else:
                        st.error("Failed to create order. Ensure user exists.")

    df = pd.DataFrame(st.session_state.orders_data)
    if not df.empty:
        df['order_date'] = pd.to_datetime(df['order_date']).dt.strftime("%Y-%m-%d %H:%M")
        st.dataframe(df, use_container_width=True)

    order_ids = [f"{o['id']} - User {o['user_id']}" for o in st.session_state.orders_data]
    selected = st.selectbox("Select order to update/delete:", ["None"] + order_ids)
    if selected != "None":
        order_id = int(selected.split(" - ")[0])
        order = next(o for o in st.session_state.orders_data if o['id'] == order_id)

        st.subheader("✏️ Update Order")
        with st.form("edit_order_form"):
            new_status = st.selectbox("Status", ["pending", "shipped", "delivered", "cancelled"], index=["pending", "shipped", "delivered", "cancelled"].index(order['status']))
            new_total = st.number_input("Total Amount", min_value=0.01, value=order['total_amount'])
            update_btn = st.form_submit_button("Update")
            if update_btn:
                updated_data = {
                    "user_id": order['user_id'],
                    "status": new_status,
                    "total_amount": new_total
                }
                res = requests.put(f"{API_URL}/orders/{order_id}", json=updated_data)
                if res.ok:
                    st.success("Order updated.")
                    refresh_data()
                else:
                    st.error("Update failed.")

        if st.button("🗑️ Delete This Order"):
            res = requests.delete(f"{API_URL}/orders/{order_id}")
            if res.ok:
                st.success("Order deleted.")
                refresh_data()
            else:
                st.error("Failed to delete order.")
