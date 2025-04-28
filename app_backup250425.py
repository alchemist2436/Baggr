
import streamlit as st
import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import pandas as pd
import joblib
import yfinance as yf

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
    st.markdown("### 🔎 Real-Time Stock Prediction")

    try:
        model = joblib.load("model.pkl")
    except Exception as e:
        st.error(f"⚠️ Could not load model: {e}")
        st.stop()

    # Real-Time Stock Lookup
    stock_input = st.text_input("Enter stock symbol (e.g. RELIANCE.NS or INFY.NS):").upper()
    if stock_input:
        try:
            ticker = yf.Ticker(stock_input)
            info = ticker.info
            #st.write("📦 Raw Yahoo Finance Info:", info)  
            pe = info.get("trailingPE", 0)
            roe = info.get("returnOnEquity", 0)
            volume = info.get("volume", 0)
            eps = info.get("trailingEps", 0)

            features = pd.DataFrame([{
                "PE": pe,
                "ROE": roe * 100 if roe else 0,
                "Volume": volume,
                "EPS": eps
            }])

            st.write("📊 Fetched Financials:")
            st.dataframe(features)

            # Predict using model
            confidence = model.predict_proba(features)[0][1]
            st.success(f"🧠 Prediction Confidence: **{confidence:.2%}**")

        except Exception as e:
            st.error(f"❌ Failed to fetch or predict: {e}")

    if st.sidebar.button("🔓 Logout"):
        st.session_state.logged_in = False
        st.rerun()
