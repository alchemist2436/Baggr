
import firebase_admin
from firebase_admin import credentials, firestore

try:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()

    print("✅ Success: Connected to Firebase Firestore!")
except Exception as e:
    print("❌ Error:", e)
