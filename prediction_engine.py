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

    os.makedirs("model", exist_ok=True)
    joblib.dump(model, MODEL_FILE)
    joblib.dump(scaler, SCALER_FILE)

    print(f"🧠 Model trained — Accuracy: {accuracy:.2f}")
    return model, scaler

def load_model():
    try:
        if os.path.exists(MODEL_FILE) and os.path.exists(SCALER_FILE):
            model = joblib.load(MODEL_FILE)
            scaler = joblib.load(SCALER_FILE)
            print("🧠 Loaded saved model and scaler.")
            return model, scaler
        else:
            print("📦 No saved model found — training new one...")
            return train_and_save_model()
    except Exception as e:
        print(f"❌ Model load error: {e}")
        return None

def predict_price_movement(model, scaler, data, sentiment_summary):
    try:
        sentiment_score = sentiment_summary.get("positive", 0) - sentiment_summary.get("negative", 0)
        rsi = float(data.get("rsi", 50))
        volume = float(data.get("volume", 0))

        input_features = [[rsi, volume, sentiment_score]]
        input_scaled = scaler.transform(input_features)
        prob = model.predict_proba(input_scaled)[0][1]

        # 🧠 Inject emotional bias
        adjusted_prob = prob
        if sentiment_score > 3:
            adjusted_prob += 0.05  # Greed — boost optimism
        elif sentiment_score < -3:
            adjusted_prob -= 0.05  # Fear — reduce confidence

        adjusted_prob = max(0.0, min(1.0, adjusted_prob))  # Clamp between 0–1

        print(f"🔮 Base: {prob:.2f} | Bias-adjusted: {adjusted_prob:.2f} → {'✅ Confident' if adjusted_prob >= CONFIDENCE_THRESHOLD else '❌ Not confident'}")

        data["confidence"] = adjusted_prob  # 🔁 Attach adjusted confidence back to data
        return adjusted_prob >= CONFIDENCE_THRESHOLD
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return False


if __name__ == "__main__":
    train_and_save_model()
