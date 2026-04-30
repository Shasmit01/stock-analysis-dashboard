import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_mock_stock_data(ticker, days=756):
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    prices = {'AAPL': 150, 'MSFT': 280, 'JPM': 150, 'JNJ': 160, 'XOM': 95}
    start_price = prices.get(ticker, 100)

    returns = np.random.normal(0.0005, 0.02, days)
    price = start_price * np.exp(np.cumsum(returns))

    if ticker == 'AAPL':
        price = price * 1.3
    elif ticker == 'MSFT':
        price = price * 1.25
    elif ticker == 'JPM':
        price = price * 1.05

    df = pd.DataFrame({
        'Date': dates,
        'Open': price * np.random.uniform(0.99, 1.01, days),
        'High': price * np.random.uniform(1.00, 1.02, days),
        'Low': price * np.random.uniform(0.98, 1.00, days),
        'Close': price,
        'Adj Close': price,
        'Volume': np.random.randint(1000000, 100000000, days)
    })

    df.set_index('Date', inplace=True)
    return df

def fetch_stock_data(tickers, period_years=3):
    stock_data = {}
    days = 365 * period_years
    print(f"Generating mock data for {len(tickers)} stocks ({days} days)")

    for ticker in tickers:
        print(f"Generating {ticker}...")
        try:
            df = generate_mock_stock_data(ticker, days=days)
            stock_data[ticker] = df
            print(f"[OK] {ticker}: {len(df)} trading days loaded")
        except Exception as e:
            print(f"[ERROR] {ticker}: {e}")

    return stock_data

if __name__ == "__main__":
    portfolio = ["AAPL", "MSFT", "JPM", "JNJ", "XOM"]
    data = fetch_stock_data(portfolio)
    for ticker, df in data.items():
        print(f"\n{ticker} - Last 5 days:")
        print(df.tail())
