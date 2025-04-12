import pandas as pd
import joblib
import os
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

MEMORY_FILE = "logs/pattern_memory.csv"
MODEL_FILE = "model/model.pkl"
SCALER_FILE = "model/scaler.pkl"
CONFIDENCE_THRESHOLD = 0.65  # Nikki must be at least this confident to act

def load_training_data():
    try:
        df = pd.read_csv(MEMORY_FILE)

        df["sentiment_score"] = df["sentiment_positive"].astype(int) - df["sentiment_negative"].astype(int)
        df["target"] = (df["price"].shift(-1) > df["price"]).astype(int)

        df.dropna(inplace=True)
        if df.empty:
            print("📭 Not enough data to train model.")
            return None, None

        features = df[["rsi", "volume", "sentiment_score"]]
        labels = df["target"]

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(features)

        return train_test_split(X_scaled, labels, test_size=0.2, random_state=42), scaler
    except Exception as e:
        print(f"❌ Error loading training data: {e}")
        return None, None

def train_and_save_model():
    result = load_training_data()
    if result is None:
        return None, None

    (X_train, X_test, y_train, y_test), scaler = result
    model = LogisticRegression()
    model.fit(X_train, y_train)
    accuracy = model.score(X_test, y_test)

    # Save model + scaler
    os.makedirs("model", exist_ok=True)
    joblib.dump(model, MODEL_FILE)
    joblib.dump(scaler, SCALER_FILE)

    print(f"🧠 Model trained — Accuracy: {accuracy:.2f}")
    return model, scaler

def load_model():
    if os.path.exists(MODEL_FILE) and os.path.exists(SCALER_FILE):
        model = joblib.load(MODEL_FILE)
        scaler = joblib.load(SCALER_FILE)
        print("🧠 Loaded saved model and scaler.")
        return model, scaler
    else:
        print("📦 No saved model found — training new one...")
        return train_and_save_model()

def predict_price_movement(model, scaler, data, sentiment_summary):
    try:
        sentiment_score = sentiment_summary["positive"] - sentiment_summary["negative"]
        input_features = [[data["rsi"], data["volume"], sentiment_score]]
        input_scaled = scaler.transform(input_features)
        prob = model.predict_proba(input_scaled)[0][1]  # Confidence price will go UP
        print(f"🔮 Prediction confidence: {prob:.2f}")

        return prob >= CONFIDENCE_THRESHOLD  # Only trade if confidence is high
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return False

if __name__ == "__main__":
    train_and_save_model()
