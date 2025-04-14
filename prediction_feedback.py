import os
import json
from datetime import datetime

FEEDBACK_LOG = "logs/prediction_feedback.json"

def record_prediction_result(coin, was_correct, confidence, expected, actual):
    os.makedirs("logs", exist_ok=True)

    record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "coin": coin,
        "confidence": confidence,
        "expected": expected,
        "actual": actual,
        "was_correct": was_correct
    }

    if os.path.exists(FEEDBACK_LOG):
        with open(FEEDBACK_LOG, "r") as f:
            logs = json.load(f)
    else:
        logs = []

    logs.append(record)
    with open(FEEDBACK_LOG, "w") as f:
        json.dump(logs[-1000:], f, indent=2)  # Keep last 1000 feedback logs

def analyze_feedback_confidence():
    if not os.path.exists(FEEDBACK_LOG):
        return None

    with open(FEEDBACK_LOG, "r") as f:
        logs = json.load(f)

    correct = [log for log in logs if log["was_correct"]]
    wrong = [log for log in logs if not log["was_correct"]]

    if not correct or not wrong:
        return None

    avg_conf_correct = sum([log["confidence"] for log in correct]) / len(correct)
    avg_conf_wrong = sum([log["confidence"] for log in wrong]) / len(wrong)

    print(f"📊 Avg Confidence → Correct: {avg_conf_correct:.2f}, Wrong: {avg_conf_wrong:.2f}")
    return avg_conf_correct, avg_conf_wrong
