import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def fetch_stock_data(tickers, period_years=3):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * period_years)
    stock_data = {}

    print(f"Fetching data from {start_date.date()} to {end_date.date()}")

    for ticker in tickers:
        print(f"Downloading {ticker}...")
        try:
            df = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)
            if df.empty:
                print(f"[ERROR] {ticker}: No data returned")
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            if 'Close' in df.columns and 'Adj Close' not in df.columns:
                df['Adj Close'] = df['Close']

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
