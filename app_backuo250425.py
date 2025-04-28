import streamlit as st
import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import pandas as pd
import joblib

# Firebase Config
firebaseConfig = {
    "apiKey": "AIzaSyBqWGy0M366wIa2SHhmlZKhfehhbj6_4Xk",
    "authDomain": "baggrai-d0fbf.firebaseapp.com",
    "databaseURL": "https://baggrai-d0fbf-default-rtdb.firebaseio.com",
    "projectId": "baggrai-d0fbf",
    "storageBucket": "baggrai-d0fbf.appspot.com",
    "messagingSenderId": "944571406375",
    "appId": "1:944571406375:web:cf4f495340215832ec9602"
}

# Firebase Admin Init
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

st.set_page_config(page_title="BaggrAI", layout="wide")
st.title("🧠 BaggrAI - Login")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

menu = st.sidebar.selectbox("Menu", ["Login", "Register"])

# LOGIN
if not st.session_state.logged_in and menu == "Login":
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            st.session_state.logged_in = True
            st.session_state.email = email
            st.session_state.user_id = user["localId"]
            db.collection("users").document(user["localId"]).set({
                "email": email,
                "lastLogin": datetime.now()
            }, merge=True)
            st.success("✅ Login successful")
            st.rerun()
        except Exception as e:
            st.error(f"Login failed: {e}")

# REGISTER
elif not st.session_state.logged_in and menu == "Register":
    email = st.text_input("New Email")
    password = st.text_input("New Password", type="password")
    if st.button("Register"):
        try:
            auth.create_user_with_email_and_password(email, password)
            st.success("✅ Registration successful. Please login.")
        except Exception as e:
            st.error(f"Registration failed: {e}")

# DASHBOARD
if st.session_state.logged_in:
    st.sidebar.success(f"👋 {st.session_state.email}")
    user_id = st.session_state.user_id
    role = db.collection("users").document(user_id).get().to_dict().get("role", "viewer")

    if role == "admin":
        st.sidebar.markdown("👑 Admin Panel")
        st.sidebar.button("🔁 Reset Alerts")
        st.sidebar.button("📤 Export Data")

    st.subheader("📈 BaggrAI Dashboard")

    # PREDICTION ENGINE
    st.markdown("### 🔮 Prediction Engine")
    try:
        model = joblib.load("model.pkl")
        df = pd.read_csv("stock_features.csv")

        # Predict confidence
        if hasattr(model, "predict_proba"):
            df["confidence"] = model.predict_proba(df.drop(columns=["ticker"]))[:, 1]
        else:
            df["confidence"] = model.predict(df.drop(columns=["ticker"]))

        st.success("✅ Predictions loaded")
        st.dataframe(df.sort_values("confidence", ascending=False).head(5))
        st.bar_chart(df.sort_values("confidence", ascending=False).set_index("ticker")["confidence"])

        # STOCK SEARCH
        st.subheader("🔎 Search for a Stock")
        search_term = st.text_input("Enter stock name (e.g. RELIANCE)")

        if search_term:
            st.info(f"🔎 Searching for: {search_term.upper()}")
            match = df["ticker"].str.upper().str.strip() == search_term.upper().strip()
            result = df[match]

            if not result.empty:
                st.success(f"✅ Found: {search_term.upper()}")
                st.dataframe(result)
            else:
                st.warning("⚠️ No match found. Please check the spelling.")

    except Exception as e:
        st.warning(f"Prediction engine failed: {e}")

    if st.sidebar.button("🔓 Logout"):
        st.session_state.logged_in = False
        st.rerun()

