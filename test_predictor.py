import pandas as pd
from app.ai.predictor import predict_signal

df = pd.read_csv("data/AI_Features.csv")

signal, confidence = predict_signal(df)

print("=" * 40)
print("Phoenix AI Prediction")
print("=" * 40)
print("Signal     :", signal)
print(f"Confidence : {confidence:.2f}%")
