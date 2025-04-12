import json
from portfolio import load_portfolio

def analyze_performance():
    portfolio = load_portfolio()
    history = portfolio.get("trade_history", [])

    if not history:
        print("📭 No trades found.")
        return

    total_trades = len(history)
    total_sells = sum(1 for t in history if t["action"] == "sell")
    total_buys = total_trades - total_sells

    usd = portfolio["usd_balance"]
    btc = portfolio["btc_balance"]
    last_price = portfolio["last_trade_price"]
    portfolio_value = usd + (btc * last_price)

    net_profit = portfolio_value - 100
    roi = (net_profit / 100) * 100

    print("📊 Nikki's Trade Performance Report")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"Total Trades:      {total_trades}")
    print(f"Buys:              {total_buys}")
    print(f"Sells:             {total_sells}")
    print(f"Final USD:         ${usd:.2f}")
    print(f"Final BTC:         {btc:.6f}")
    print(f"Last Trade Price:  ${last_price}")
    print(f"Total Value:       ${portfolio_value:.2f}")
    print(f"Net Profit:        ${net_profit:.2f}")
    print(f"ROI:               {roi:.2f}%")

if __name__ == "__main__":
    analyze_performance()
