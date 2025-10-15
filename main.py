import csv
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

import csv

def parse_trading_data(file_path):
    """
    Parse trading data from a CSV file using csv.reader.

    :param file_path: Path to the CSV file.
    :return: A list of parsed records as dictionaries.
    """
    with open(file_path, 'r') as file:
        reader = csv.reader(file, delimiter=';')  # Use csv.reader for faster row processing
        headers = next(reader)  # Read the header row

        # Predefine indices for column access
        current_time_idx = headers.index('currentTime')
        trade_px_idx = headers.index('tradePx')
        trade_amt_idx = headers.index('tradeAmt')

        # Process rows
        data = []
        for row in reader:
            record = {
                'currentTime': int(row[current_time_idx]) if row[current_time_idx] else None,
                'tradePx': float(row[trade_px_idx]) if row[trade_px_idx] else None,
                'tradeAmt': int(row[trade_amt_idx]) if row[trade_amt_idx] else None,
                'action': row[headers.index('action')],  # Use direct index lookup for other columns
                'orderId': row[headers.index('orderId')],
                'orderProduct': row[headers.index('orderProduct')],
                'orderSide': row[headers.index('orderSide')],
            }
            data.append(record)
    return data

def format_price(value, _):
    """Format the y-axis as plain numbers."""
    return f"{value:.2f}"

def plot_cumulative_pnl(cumulative_pnl_data):
    """
    Plot cumulative PnL for a dictionary of ticker IDs.

    :param cumulative_pnl_data: Dictionary where keys are ticker IDs and values are lists of cumulative PnL values.
    """
    plt.style.use('dark_background')
    plt.figure(figsize=(10, 6))
    
    for ticker, pnl_values in cumulative_pnl_data.items():
        plt.plot(pnl_values, label=ticker, linewidth=2)  # Thicker lines for better visibility
    
    plt.title("Cumulative PnL for Tickers", fontsize=14, color='white')
    plt.xlabel("Time (steps or events)", fontsize=12, color='white')
    plt.ylabel("Cumulative PnL", fontsize=12, color='white')
    plt.legend(title="Ticker IDs", fontsize=10, title_fontsize=12, facecolor='black', edgecolor='white')
    plt.grid(color='gray', linestyle='--', linewidth=0.5)
    plt.tick_params(colors='white')  # White ticks for dark mode
    
    # Format y-axis labels to display prices properly
    plt.gca().yaxis.set_major_formatter(FuncFormatter(format_price))
    
    plt.show()

if __name__ == "__main__":
    file_path = "test_logs.csv"  # Replace with your actual file path
    parsed_data = parse_trading_data(file_path)
    
    cumulativePnL = {}
    runningPnL = {}
    
    for record in parsed_data:
        if record["action"] != "filled":
            continue

        ticker = record["orderProduct"]
        side = record["orderSide"]
        price = record["tradePx"]
        quantity = record["tradeAmt"]

        running_ticker = runningPnL.setdefault(ticker, {"cost_basis": 0, "stock": 0, "realized_pnl": 0})
        cumulative_ticker = cumulativePnL.setdefault(ticker, [0])

        if side == "buy":
            running_ticker["cost_basis"] += price * quantity
            running_ticker["stock"] += quantity
        elif side == "sell":
            if running_ticker["stock"] >= quantity:
                avg_cost = running_ticker["cost_basis"] / running_ticker["stock"]
                profit = (price - avg_cost) * quantity

                running_ticker["cost_basis"] -= avg_cost * quantity
                running_ticker["stock"] -= quantity
                running_ticker["realized_pnl"] += profit
                cumulative_ticker.append(running_ticker["realized_pnl"])
            else:
                print(f"Error: Not enough stock to sell for ticker {ticker}")
                print(f"Tried to sell {quantity} but only have {running_ticker['stock']} available")
    
    # Extract realized PnL for each ticker
    realized_pnl = {ticker: data["realized_pnl"] for ticker, data in runningPnL.items()}

    # Calculate the total realized PnL using a lambda function
    total_realized_pnl = sum(map(lambda x: x, realized_pnl.values()))

    # Output results
    print("1. Total Realized PnL:", total_realized_pnl)
    print("2. Realized PnL by Ticker:", realized_pnl)
    plot_cumulative_pnl(cumulativePnL)
    
    print(runningPnL)