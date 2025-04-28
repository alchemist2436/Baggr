
import streamlit as st
import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Firebase Config (Replace with your actual values)
firebaseConfig = {
    "apiKey": "AIzaSyBqWGy0M366wIa2SHhmlZKhfehhbj6_4Xk",
    "authDomain": "baggrai-d0fbf.firebaseapp.com",
    "databaseURL": "https://baggrai-d0fbf-default-rtdb.firebaseio.com",
    "projectId": "baggrai-d0fbf",
    "storageBucket": "baggrai-d0fbf.appspot.com",
    "messagingSenderId": "944571406375",
    "appId": "1:944571406375:web:cf4f495340215832ec9602"
}

# Initialize Firebase Admin
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

st.set_page_config(page_title="BaggrAI", layout="wide")
st.title("🧠 BaggrAI Login Portal")

# Session state for login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Main UI
menu = st.sidebar.selectbox("Menu", ["Login", "Register"])

if not st.session_state.logged_in and menu == "Login":
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            st.session_state.logged_in = True
            st.session_state.email = email
            st.session_state.user_id = user["localId"]

            # Update lastLogin in Firestore
            db.collection("users").document(user["localId"]).set({
                "email": email,
                "lastLogin": datetime.now()
            }, merge=True)

            st.success("✅ Login successful!")
            st.rerun()
        except Exception as e:
            st.error(f"Login failed: {e}")

elif not st.session_state.logged_in and menu == "Register":
    email = st.text_input("New Email")
    password = st.text_input("New Password", type="password")
    if st.button("Register"):
        try:
            user = auth.create_user_with_email_and_password(email, password)
            st.success("✅ Registration successful. Please login.")
        except Exception as e:
            st.error(f"Registration failed: {e}")

# Logged In User View
if st.session_state.logged_in:
    st.sidebar.success(f"👋 Welcome, {st.session_state.email}")
    user_id = st.session_state.user_id

    # Get user role from Firestore
    user_doc = db.collection("users").document(user_id).get()
    role = user_doc.to_dict().get("role", "viewer")

    if role == "admin":
        st.sidebar.markdown("👑 **Admin Panel**")
        st.sidebar.button("🔁 Reset All Alerts")
        st.sidebar.button("📤 Export Data")
        st.sidebar.info("Access: Full control")

    else:
        st.sidebar.info("🔍 Access: Viewer mode")

    # Dashboard Placeholder
    st.subheader("📈 BaggrAI Dashboard")
    st.info("Here you will see your portfolio predictions, top picks, filters, and visual analytics.")

    if st.sidebar.button("🔓 Logout"):
        st.session_state.logged_in = False
        st.rerun()

