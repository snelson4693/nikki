import time
import traceback
import os
from portfolio import load_portfolio
from data_feed import get_market_data
from utils.helpers import log_message
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn
from rich.table import Table

console = Console()

def display_dashboard():
    try:
        while True:
            os.system("cls" if os.name == "nt" else "clear")

            console.print("[bold cyan]🔄 Refreshing dashboard...[/bold cyan]")

            # ✅ Explicitly define asset type (bitcoin is crypto)
            data = get_market_data("bitcoin", asset_type="crypto")
            if not data:
                console.print("[bold red]❌ Could not fetch market data.[/bold red]")
                time.sleep(10)
                continue

            portfolio = load_portfolio()

            usd = portfolio["usd_balance"]
            btc = portfolio["btc_balance"]
            last_price = data["price"]
            value = usd + (btc * last_price)
            rsi = data["rsi"]

            history = portfolio["trade_history"]
            trades = len(history)
            wins = sum(1 for trade in history if trade['action'] == 'sell')
            win_rate = (wins / trades * 100) if trades else 0

            table = Table(title="📊 Nikki's Live Trading Dashboard", show_lines=True)
            table.add_column("Metric", justify="left")
            table.add_column("Value", justify="right")

            table.add_row("💰 USD Balance", f"${usd:,.2f}")
            table.add_row("₿ BTC Balance", f"{btc:.6f}")
            table.add_row("📈 BTC Price", f"${last_price:,.2f}")
            table.add_row("📉 RSI", f"{rsi:.2f}")
            table.add_row("📂 Total Trades", str(trades))
            table.add_row("✅ Win Rate", f"{win_rate:.2f}%")

            console.print(table)

            # Show progress bar
            profit_percent = max(0, (value - 100) / 100 * 100)
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                transient=True,
            ) as progress:
                progress.add_task("[green]📈 Profit Progress", total=100, completed=profit_percent)
                time.sleep(5)

    except KeyboardInterrupt:
        log_message("🛑 Dashboard closed by user.")
    except Exception:
        console.print("[bold red]‼️ Dashboard Error:[/bold red]")
        console.print(traceback.format_exc())

if __name__ == "__main__":
    display_dashboard()
