import os
import pickle
import numpy as np
from datetime import datetime
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import json

MODEL_DIR = "model"
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
FUSION_LOG = os.path.join(MODEL_DIR, "fusion_history.json")


def load_model_and_scaler(path):
    try:
        with open(os.path.join(path, "model.pkl"), "rb") as f:
            model = pickle.load(f)
        with open(os.path.join(path, "scaler.pkl"), "rb") as f:
            scaler = pickle.load(f)
        return model, scaler
    except Exception as e:
        print(f"❌ Failed to load model or scaler from {path}: {e}")
        return None, None


def average_model_weights(models):
    weights = [m.coef_ for m in models if hasattr(m, "coef_")]
    intercepts = [m.intercept_ for m in models if hasattr(m, "intercept_")]

    if not weights or not intercepts:
        raise ValueError("❌ No valid model weights to merge.")

    avg_weights = np.mean(weights, axis=0)
    avg_intercepts = np.mean(intercepts, axis=0)

    fused_model = LogisticRegression()
    fused_model.coef_ = avg_weights
    fused_model.intercept_ = avg_intercepts
    fused_model.classes_ = models[0].classes_ if hasattr(models[0], "classes_") else np.array([0, 1])
    return fused_model


def average_scalers(scalers):
    means = np.array([s.mean_ for s in scalers])
    vars_ = np.array([s.var_ for s in scalers])

    avg_scaler = StandardScaler()
    avg_scaler.mean_ = np.mean(means, axis=0)
    avg_scaler.var_ = np.mean(vars_, axis=0)
    avg_scaler.scale_ = np.sqrt(avg_scaler.var_)
    return avg_scaler


def log_fusion_event(model_paths):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "sources": sorted(set(model_paths))
    }
    existing = []
    if os.path.exists(FUSION_LOG):
        try:
            with open(FUSION_LOG, "r") as f:
                existing = json.load(f)
        except json.JSONDecodeError:
            print("⚠️ fusion_history.json was malformed. Reinitializing.")
            existing = []
    if log_entry not in existing:
        existing.append(log_entry)
        with open(FUSION_LOG, "w") as f:
            json.dump(existing, f, indent=2)


def discover_model_sources():
    sources = set()
    for base in [MODEL_DIR, "brain_repo/model"]:
        if os.path.exists(os.path.join(base, "model.pkl")) and os.path.exists(os.path.join(base, "scaler.pkl")):
            sources.add(base)

        fusion_path = os.path.join(base, "fusion.json")
        if os.path.exists(fusion_path):
            try:
                with open(fusion_path, "r") as f:
                    fusion_data = json.load(f)
                    if isinstance(fusion_data, list):
                        sources.update(fusion_data)
            except Exception as e:
                print(f"⚠️ Failed to read fusion.json from {fusion_path}: {e}")

    return sorted(sources)


def fuse_models():
    sources = discover_model_sources()
    print(f"🔬 Fusing models from: {sources}")
    models = []
    scalers = []

    for src in sources:
        model, scaler = load_model_and_scaler(src)
        if model and scaler:
            models.append(model)
            scalers.append(scaler)

    if len(models) < 2:
        print("⚠️ Not enough valid models to perform fusion.")
        return

    fused_model = average_model_weights(models)
    fused_scaler = average_scalers(scalers)

    try:
        os.makedirs(MODEL_DIR, exist_ok=True)
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(fused_model, f)
        with open(SCALER_PATH, "wb") as f:
            pickle.dump(fused_scaler, f)
        print("✅ Fused model and scaler saved.")
        log_fusion_event(sources)
    except Exception as e:
        print(f"❌ Failed to save fused model or scaler: {e}")


if __name__ == "__main__":
    fuse_models()
