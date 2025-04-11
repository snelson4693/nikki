from data_feed import get_market_data
from trade_engine import evaluate_trade
from risk_manager import is_trade_allowed
from wallet import execute_trade

def main():
    print("🚀 Nikki is starting up...")

    # Get market data
    market_data = get_market_data()

    # Check if trading conditions are met
    if is_trade_allowed(market_data):
        trade_signal = evaluate_trade(market_data)

        if trade_signal:
            execute_trade(trade_signal)
        else:
            print("🔍 No valid trade signal detected.")
    else:
        print("⚠️ Trading conditions not met. Skipping...")

if __name__ == "__main__":
    main()
