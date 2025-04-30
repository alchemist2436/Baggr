import streamlit as st
import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import pandas as pd
import joblib
import yfinance as yf
import shap
import matplotlib.pyplot as plt



# Initialize Firebase Admin
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# Streamlit UI Setup
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

# Dashboard
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

    common_tickers = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "ITC.NS", "HDFCBANK.NS", "LT.NS", "KOTAKBANK.NS", "ASIANPAINT.NS"]
    selected_ticker = st.selectbox("Pick a stock (NSE):", common_tickers)
    manual_input = st.text_input("Or enter custom symbol (e.g. SBIN.NS)").upper()
    stock_input = manual_input if manual_input else selected_ticker

    if stock_input:
        try:
            ticker = yf.Ticker(stock_input)
            info = ticker.info

            pe = info.get("trailingPE", 0)
            roe = info.get("returnOnEquity") or 0
            roe = roe * 100
            volume = info.get("volume", 0)
            eps = info.get("trailingEps", 0)

            features = pd.DataFrame([{
                "PE": pe,
                "ROE": roe,
                "Volume": volume,
                "EPS": eps
            }])

            st.write("📊 Financial Snapshot:")
            st.dataframe(features)

            confidence = model.predict_proba(features)[0][1]
            st.success(f"🧠 Prediction Confidence: **{confidence:.2%}**")

            # Confidence Alerts
            if confidence > 0.85:
                st.warning("🔔 CONFIDENCE ALERT: High probability pick!")
            elif confidence > 0.7:
                st.info("⚠️ Moderate confidence – worth a look.")
            else:
                st.caption("🔍 Low confidence – not likely a multibagger.")

            # Explain This Pick
            if st.button("🧠 Explain This Pick"):
                st.sidebar.markdown("## 🤖 Why This Stock?")
                st.sidebar.dataframe(features)

                if roe > 15:
                    st.sidebar.success("✅ Strong ROE")
                if pe < 25:
                    st.sidebar.info("💡 Low PE")
                if eps > 20:
                    st.sidebar.success("📈 High EPS")
                if volume > 1_000_000:
                    st.sidebar.info("📊 Good liquidity")

            # SHAP Waterfall
            st.subheader("🎯 SHAP: Feature Impact on This Prediction")
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(features)
            shap.plots.waterfall(shap.Explanation(
                values=shap_values[1][0],
                base_values=explainer.expected_value[1],
                data=features.iloc[0]
            ))

            # Global Feature Importance
            st.subheader("📊 Feature Importance (Overall)")
            importances = model.feature_importances_

            fig, ax = plt.subplots()
            ax.barh(features.columns, importances)
            ax.set_xlabel("Importance Score")
            ax.set_title("BaggrAI - Feature Importances")
            st.pyplot(fig)

        except Exception as e:
            st.error(f"❌ Failed to fetch or predict: {e}")

    if st.sidebar.button("🔓 Logout"):
        st.session_state.logged_in = False
        st.rerun()
