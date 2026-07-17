import pandas as pd
import joblib

from xgboost import XGBClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

print("=" * 60)
print("Phoenix AI Trader V2")
print("=" * 60)

# Load dataset
df = pd.read_csv("data/AI_Features.csv")

# Features
features = [
    "EMA20",
    "EMA50",
    "EMA100",
    "EMA200",
    "RSI",
    "MACD",
    "MACD_Signal",
    "MACD_Hist",
    "ATR",
    "ADX",
    "Return1",
    "Return5",
    "Volume_MA",
]

X = df[features]
y = df["Target"]

# Time-based split (no shuffling)
split = int(len(df) * 0.8)

X_train = X.iloc[:split]
X_test = X.iloc[split:]

y_train = y.iloc[:split]
y_test = y.iloc[split:]

model = XGBClassifier(
    objective="multi:softprob",
    num_class=3,
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    random_state=42,
)

model.fit(X_train, y_train)

pred = model.predict(X_test)

print("\nClassification Report\n")
print(classification_report(y_test, pred))

print("\nConfusion Matrix\n")
print(confusion_matrix(y_test, pred))

joblib.dump(model, "models/xgboost_v2.pkl")

print("\nModel Saved")
print("models/xgboost_v2.pkl")