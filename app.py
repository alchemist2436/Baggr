import streamlit as st
import os
from dotenv import load_dotenv
import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize environment
load_dotenv()  # Load .env file

# ======================
# FIREBASE INITIALIZATION
# ======================

# 1. Firebase Admin SDK (for Firestore)
if not firebase_admin._apps:
    firebase_credentials = {
        "type": "service_account",
        "project_id": os.getenv("FIREBASE_PROJECT_ID"),
        "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
        "token_uri": "https://oauth2.googleapis.com/token"
    }
    cred = credentials.Certificate(firebase_credentials)
    firebase_admin.initialize_app(cred)
    db_firestore = firestore.client()  # Firestore instance

# 2. Pyrebase (for Realtime DB/Auth)
firebase_config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID")
}
firebase = pyrebase.initialize_app(firebase_config)
db_realtime = firebase.database()  # Realtime DB instance
auth = firebase.auth()  # Authentication instance

# ================
# STREAMLIT UI
# ================
st.title("🔥 Firebase Integration Demo")

tab1, tab2 = st.tabs(["Realtime DB", "Auth Demo"])

with tab1:
    st.subheader("Realtime Database")
    if st.button("Read DB"):
        data = db_realtime.child("/").get().val()
        st.json(data)

with tab2:
    st.subheader("Authentication")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Sign Up"):
        try:
            user = auth.create_user_with_email_and_password(email, password)
            st.success(f"Created user: {user['email']}")
        except Exception as e:
            st.error(str(e))

# ======================
# FIRESTORE DEMO (OPTIONAL)
# ======================
if st.checkbox("Show Firestore Demo"):
    doc_ref = db_firestore.collection("test").document("demo")
    doc_ref.set({"message": "Hello from Streamlit!"})
    doc = doc_ref.get()
    st.write("Firestore document:", doc.to_dict())