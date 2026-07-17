import pandas as pd
import joblib
import os

from xgboost import XGBClassifier

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)

INPUT = "data/AI_Dataset.csv"

MODEL_DIR = "models"
MODEL_FILE = "models/xgboost_model.pkl"

if not os.path.exists(INPUT):
    print("Dataset not found!")
    exit()

# -----------------------------
# Load Dataset
# -----------------------------

df = pd.read_csv(INPUT)

X = df.drop("Target", axis=1)
y = df["Target"]

# -----------------------------
# Split Data
# -----------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    shuffle=True,
)

# -----------------------------
# Train Model
# -----------------------------

model = XGBClassifier(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.05,
    objective="binary:logistic",
    random_state=42,
)

model.fit(X_train, y_train)

# -----------------------------
# Prediction
# -----------------------------

predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("=" * 60)
print("PHOENIX AI TRADER")
print("=" * 60)

print(f"Accuracy : {accuracy*100:.2f}%")

print("\nClassification Report\n")

print(classification_report(y_test, predictions))

print("Confusion Matrix\n")

print(confusion_matrix(y_test, predictions))

# -----------------------------
# Save Model
# -----------------------------

os.makedirs(MODEL_DIR, exist_ok=True)

joblib.dump(model, MODEL_FILE)

print("\nModel Saved")

print(MODEL_FILE)
