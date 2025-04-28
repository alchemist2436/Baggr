
import streamlit as st
import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Firebase configuration (replace these with your actual config)
firebaseConfig = {
     "apiKey": "AIzaSyBqWGy0M366wIa2SHhmlZKhfehhbj6_4Xk",
    "authDomain": "baggrai-d0fbf.firebaseapp.com",
    "databaseURL": "https://baggrai-d0fbf-default-rtdb.firebaseio.com",
    "projectId": "baggrai-d0fbf",
    "storageBucket": "baggrai-d0fbf.appspot.com",
    "messagingSenderId": "944571406375",
    "appId": "1:944571406375:web:cf4f495340215832ec9602"
}

# Load Firebase Admin credentials
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Initialize Pyrebase for auth
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

analyzer = SentimentIntensityAnalyzer()

st.set_page_config("BaggrAI", layout="wide")
st.title("🧠 BaggrAI Dashboard")

menu = st.radio("Choose", ["Login", "Register"])

if menu == "Login":
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            st.success("✅ Login successful")
            user_id = user["localId"]
            db.collection("users").document(user_id).update({"lastLogin": datetime.now()})
        except Exception as e:
            st.error(f"Login failed: {e}")

elif menu == "Register":
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Register"):
        try:
            user = auth.create_user_with_email_and_password(email, password)
            user_id = user["localId"]
            db.collection("users").document(user_id).set({
                "email": email,
                "created": datetime.now()
            })
            st.success("✅ Registered successfully")
        except Exception as e:
            st.error(e)
