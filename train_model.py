import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier

# Load features
df = pd.read_csv("stock_features.csv")
df["target"] = np.random.choice([0, 1], size=len(df), p=[0.7, 0.3])  # Fake binary target

# Train model
X = df.drop(columns=["ticker", "target"])
y = df["target"]
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# Save new compatible model
joblib.dump(model, "model.pkl")
print("✅ Model trained and saved as model.pkl")

