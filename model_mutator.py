import os
import json
import pandas as pd
from datetime import datetime
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

from prediction_feedback import analyze_feedback_confidence

DATA_PATH = "logs/pattern_learning.json"
MODEL_PATH = "model/model.pkl"
SCALER_PATH = "model/scaler.pkl"

def load_training_data():
    if not os.path.exists(DATA_PATH):
        return None, None

    with open(DATA_PATH, "r") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    df.dropna(inplace=True)

    df["label"] = df["trade_action"].apply(lambda x: 1 if x == "buy" else 0)

    X = df[["rsi", "sentiment_score", "volume", "change_24h", "price"]]
    y = df["label"]

    return X, y

def retrain_model():
    X, y = load_training_data()
    if X is None or len(X) < 20:
        print("📭 Not enough data to retrain model.")
        return False

    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2)

    model = LogisticRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    # 🧠 Confidence-based reward analysis
    confidence_stats = analyze_feedback_confidence()
    if confidence_stats:
        avg_correct, avg_wrong = confidence_stats
        if avg_correct - avg_wrong < 0.05:
            print("⚠️ Nikki's confidence is poorly calibrated. Consider adjusting thresholds or retraining with feedback weighting.")

    print(f"🧠 New model trained. Accuracy: {accuracy:.2f}")

    if accuracy >= 0.60:
        joblib.dump(model, MODEL_PATH)
        joblib.dump(scaler, SCALER_PATH)
        print("✅ Model + scaler saved!")
        return True
    else:
        print("❌ New model not accurate enough. Keeping current brain.")
        return False

if __name__ == "__main__":
    retrain_model()
