import streamlit as st
import requests
import pandas as pd

API_URL = "http://backend:8000"
st.set_page_config(page_title="Amazon Admin", layout="wide")

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "home"
if "users_data" not in st.session_state:
    st.session_state.users_data = []
if "products_data" not in st.session_state:
    st.session_state.products_data = []
if "selected_user_id" not in st.session_state:
    st.session_state.selected_user_id = None
if "selected_product_id" not in st.session_state:
    st.session_state.selected_product_id = None
if "confirm_delete_user" not in st.session_state:
    st.session_state.confirm_delete_user = False
if "confirm_delete_product" not in st.session_state:
    st.session_state.confirm_delete_product = False
if "form_reset" not in st.session_state:
    st.session_state.form_reset = False

def refresh_data():
    st.session_state.users_data = requests.get(f"{API_URL}/users/").json()
    st.session_state.products_data = requests.get(f"{API_URL}/products/").json()

refresh_data()

def get_unique_categories():
    return sorted(set([p['category'] for p in st.session_state.products_data if p['category']]))

# Home splash screen
if st.session_state.page == "home":
    st.markdown("## 👋 Welcome to the Amazon Admin Dashboard")
    st.write("What would you like to manage?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👤 Manage Users", use_container_width=True):
            st.session_state.page = "users"
            st.rerun()
    with col2:
        if st.button("📦 Manage Products", use_container_width=True):
            st.session_state.page = "products"
            st.rerun()

# Manage Users Page
elif st.session_state.page == "users":
    st.markdown("## 👤 Manage Users")
    st.markdown(f"### 👥 Total Users: {len(st.session_state.users_data)}")
    if st.button("🏠 Back to Home"):
        st.session_state.page = "home"
        st.rerun()

    with st.expander("➕ Add New User", expanded=False):
        with st.form("add_user"):
            col1, col2 = st.columns(2)
            name = col1.text_input("Name", value="" if st.session_state.form_reset else None)
            email = col2.text_input("Email", value="" if st.session_state.form_reset else None)
            password = st.text_input("Password", type="password", value="" if st.session_state.form_reset else None)
            col3, col4 = st.columns(2)
            phone = col3.text_input("Phone", value="" if st.session_state.form_reset else None)
            role = col4.selectbox("Role", ["customer", "seller", "admin"])
            address = st.text_area("Address", value="" if st.session_state.form_reset else None)
            submit = st.form_submit_button("Create User")
            if submit:
                data = {
                    "name": name, "email": email, "password": password,
                    "phone_number": phone, "address": address, "role": role
                }
                res = requests.post(f"{API_URL}/users/", json=data)
                if res.ok:
                    st.success("User created successfully.")
                    st.session_state.form_reset = True
                    refresh_data()
                    st.rerun()
                else:
                    st.error("Failed to create user.")
    st.session_state.form_reset = False

    st.divider()
    st.markdown("### 📋 Existing Users")
    user_df = pd.DataFrame([{
        "ID": u["user_id"],
        "Name": u["name"],
        "Email": u["email"],
        "Role": u["role"],
        "Phone": u["phone_number"],
        "Address": u["address"]
    } for u in st.session_state.users_data])
    st.dataframe(user_df.style.set_properties(**{"text-align": "center"}), use_container_width=True)

    user_ids = [str(u['user_id']) + " - " + u['name'] for u in st.session_state.users_data]
    selected = st.selectbox("Select a user to edit or delete:", ["None"] + user_ids)
    if selected != "None":
        selected_user_id = int(selected.split(" - ")[0])
        selected_user = next((u for u in st.session_state.users_data if u["user_id"] == selected_user_id), None)
        if selected_user:
            st.markdown("#### ✏️ Edit User")
            with st.form("edit_user_form"):
                col1, col2 = st.columns(2)
                new_name = col1.text_input("Name", selected_user["name"])
                new_email = col2.text_input("Email", selected_user["email"])
                col3, col4 = st.columns(2)
                new_phone = col3.text_input("Phone", selected_user["phone_number"] or "")
                new_role = col4.selectbox("Role", ["customer", "seller", "admin"],
                                          index=["customer", "seller", "admin"].index(selected_user["role"]))
                new_address = st.text_area("Address", selected_user["address"] or "")
                new_password = st.text_input("New Password", type="password", value="")
                update_btn = st.form_submit_button("Update")
                if update_btn:
                    updated_data = {
                        "name": new_name,
                        "email": new_email,
                        "phone_number": new_phone,
                        "address": new_address,
                        "role": new_role,
                        "password": new_password or "Temp@1234"
                    }
                    res = requests.put(f"{API_URL}/users/{selected_user_id}", json=updated_data)
                    if res.ok:
                        st.success("User updated.")
                        refresh_data()
                        st.rerun()
                    else:
                        st.error("Update failed.")

            if st.button("🗑️ Delete This User"):
                st.session_state.confirm_delete_user = not st.session_state.confirm_delete_user

            if st.session_state.confirm_delete_user:
                st.warning("Are you sure you want to delete this user?")
                col1, col2 = st.columns(2)
                if col1.button("✅ Yes, delete user"):
                    res = requests.delete(f"{API_URL}/users/{selected_user_id}")
                    if res.ok:
                        st.success("User deleted.")
                        st.session_state.confirm_delete_user = False
                        refresh_data()
                        st.rerun()
                if col2.button("❌ Cancel"):
                    st.session_state.confirm_delete_user = False
# Manage Products Page
elif st.session_state.page == "products":
    st.markdown("## 📦 Manage Products")
    st.markdown(f"### 📦 Total Products: {len(st.session_state.products_data)}")
    if st.button("🏠 Back to Home"):
        st.session_state.page = "home"
        st.rerun()

    with st.expander("➕ Add New Product", expanded=False):
        with st.form("add_product"):
            col1, col2 = st.columns(2)
            name = col1.text_input("Product Name", value="" if st.session_state.form_reset else None)
            description = col2.text_input("Product Description", value="" if st.session_state.form_reset else None)
            col3, col4 = st.columns(2)
            price = col3.number_input("$ Price", min_value=0.01, format="%.2f")
            stock = col4.number_input("Stock", min_value=0, step=1)
            category = st.selectbox("Category", options=(get_unique_categories() + ["Other"]))
            if category == "Other":
                category = st.text_input("Enter New Category")
            st.markdown("**Enter existing seller's User ID (who is a seller)**")
            seller_id = st.number_input("Seller ID", min_value=1, step=1)
            submit = st.form_submit_button("Create Product")
            if submit:
                data = {
                    "name": name,
                    "description": description,
                    "price": price,
                    "stock": stock,
                    "category": category,
                    "seller_id": seller_id
                }
                res = requests.post(f"{API_URL}/products/", json=data)
                if res.ok:
                    st.success("Product created successfully.")
                    st.session_state.form_reset = True
                    refresh_data()
                    st.rerun()
                else:
                    st.error("Failed to create product.")

    st.session_state.form_reset = False

    st.divider()
    st.markdown("### 📋 Existing Products")
    product_df = pd.DataFrame([{
        "ID": p["product_id"],
        "Name": p["name"],
        "Description": p["description"],
        "Price": f"${p['price']:.2f}",
        "Stock": p["stock"],
        "Category": p["category"],
        "Seller ID": p["seller_id"]
    } for p in st.session_state.products_data])
    st.dataframe(product_df.style.set_properties(**{"text-align": "center"}), use_container_width=True)

    product_ids = [str(p['product_id']) + " - " + p['name'] for p in st.session_state.products_data]
    selected = st.selectbox("Select a product to edit or delete:", ["None"] + product_ids)
    if selected != "None":
        selected_product_id = int(selected.split(" - ")[0])
        selected_product = next((p for p in st.session_state.products_data if p["product_id"] == selected_product_id), None)
        if selected_product:
            st.markdown("#### ✏️ Edit Product")
            with st.form("edit_product_form"):
                col1, col2 = st.columns(2)
                new_name = col1.text_input("Name", selected_product["name"])
                new_description = col2.text_input("Description", selected_product["description"])
                col3, col4 = st.columns(2)
                new_price = col3.number_input("Price", value=float(selected_product["price"]))
                new_stock = col4.number_input("Stock", value=selected_product["stock"], step=1)
                new_category = st.text_input("Category", selected_product["category"])
                new_seller_id = st.number_input("Seller ID", value=selected_product["seller_id"], step=1)
                update_btn = st.form_submit_button("Update")
                if update_btn:
                    updated_data = {
                        "name": new_name,
                        "description": new_description,
                        "price": new_price,
                        "stock": new_stock,
                        "category": new_category,
                        "seller_id": new_seller_id
                    }
                    res = requests.put(f"{API_URL}/products/{selected_product_id}", json=updated_data)
                    if res.ok:
                        st.success("Product updated.")
                        refresh_data()
                        st.rerun()
                    else:
                        st.error("Update failed.")

            if st.button("🗑️ Delete This Product"):
                st.session_state.confirm_delete_product = not st.session_state.confirm_delete_product

            if st.session_state.confirm_delete_product:
                st.warning("Are you sure you want to delete this product?")
                col1, col2 = st.columns(2)
                if col1.button("✅ Yes, delete product"):
                    res = requests.delete(f"{API_URL}/products/{selected_product_id}")
                    if res.ok:
                        st.success("Product deleted.")
                        st.session_state.confirm_delete_product = False
                        refresh_data()
                        st.rerun()
                if col2.button("❌ Cancel"):
                    st.session_state.confirm_delete_product = False
