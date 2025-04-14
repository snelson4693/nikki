import pandas as pd
import json
import os

# Function to load trade log data
def load_trade_log(file_path="logs/trade_log.csv"):
    try:
        # Read the CSV without headers and use column indexes directly
        trades = pd.read_csv(file_path, header=None)
        
        # Ensure correct column access by index (matching 8 columns in your CSV)
        trades.columns = ['timestamp', 'coin', 'price', 'volume', 'action', 'amount', 'status', 'signal']  # Adjusted to 8 columns
        
        return trades
    except Exception as e:
        print(f"Error loading trade log: {e}")
        return None
# Function to evaluate strategy performance autonomously
def evaluate_performance(trades):
    if trades is None or trades.empty:
        print("No trades to evaluate.")
        return None
    
    # Ensure 'price' and 'amount' are numeric and handle errors by converting invalid values to NaN
    trades['price'] = pd.to_numeric(trades['price'], errors='coerce')
    trades['amount'] = pd.to_numeric(trades['amount'], errors='coerce')
    
    # Set NaN values in 'amount' to 0 (if you want to keep those rows)
    trades['amount'] = trades['amount'].fillna(0)
    
    # Add profit column based on price and amount (adjust this as needed)
    trades['profit'] = trades['price'] * trades['amount']
    
    # Filter executed trades that were successful based on the status and signal
    executed_trades = trades[trades["status"] == 10]  # Success is indicated by status == 10
    successful_trades = executed_trades[executed_trades["signal"] != "no_signal"]  # Ensure signal is not 'no_signal'
    
    # Calculate performance metrics
    total_profit = successful_trades["profit"].sum()
    total_trades = len(successful_trades)
    average_profit = total_profit / total_trades if total_trades > 0 else 0
    
    print(f"Total profit: {total_profit}")
    print(f"Total number of successful trades: {total_trades}")
    print(f"Average profit per trade: {average_profit}")
    
    return {
        "total_profit": total_profit,
        "total_trades": total_trades,
        "average_profit": average_profit
    }
# Autonomous strategy adjustment
def adjust_strategy(performance_metrics, config_file="config.json"):
    # Nikki autonomously adjusts strategy if the performance is below expectations
    if performance_metrics["average_profit"] < 0:
        print("Nikki's performance below expectations. Autonomously adjusting strategy...")
        
        # Load current config
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Adjust strategy autonomously based on performance
        config["min_confidence"] = max(config["min_confidence"] - 0.05, 0.2)  # Lower confidence threshold
        config["max_trade_amount"] = max(config["max_trade_amount"] * 0.9, 1)  # Decrease max trade size
        config["min_trade_amount"] = max(config["min_trade_amount"] * 0.9, 0.01)  # Decrease min trade size
        
        # Save the updated config back to file
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)
        
        print("Nikki's strategy adjusted and saved.")

# Autonomous feedback logging
def log_feedback(performance_metrics, file_path="self_feedback_log.json"):
    feedback = {
        "performance_metrics": performance_metrics,
        "adjustments": {
            "min_confidence": performance_metrics["average_profit"] < 0 and 0.7 or 0.8,  # Example adjustment
            "max_trade_amount": 100,
            "min_trade_amount": 0.01
        },
        "timestamp": pd.to_datetime("now").isoformat()
    }
    
    # Append feedback to the log file
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            feedback_log = json.load(f)
    else:
        feedback_log = []
    
    feedback_log.append(feedback)
    
    with open(file_path, 'w') as f:
        json.dump(feedback_log, f, indent=4)
    
    print("Nikki's feedback logged successfully.")

# Main function to run the autonomous feedback loop
def main():
    # Load trade log and evaluate performance autonomously
    trades = load_trade_log()
    performance = evaluate_performance(trades)
    
    if performance:
        # Nikki autonomously adjusts strategy based on feedback
        adjust_strategy(performance)
        
        # Log Nikki's autonomous feedback and adjustments
        log_feedback(performance)

if __name__ == "__main__":
    main()
