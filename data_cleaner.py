import pandas as pd
import numpy as np

def clean_stock_data(stock_data):
    cleaned_data = {}

    for ticker, df in stock_data.items():
        df_clean = df.copy()

        df_clean.fillna(method='ffill', inplace=True)
        df_clean.fillna(method='bfill', inplace=True)
        df_clean = df_clean.dropna()

        df_clean['Daily_Return'] = df_clean['Adj Close'].pct_change()
        df_clean['Cumulative_Return'] = (1 + df_clean['Daily_Return']).cumprod() - 1
        df_clean['MA_20'] = df_clean['Adj Close'].rolling(window=20).mean()
        df_clean['MA_50'] = df_clean['Adj Close'].rolling(window=50).mean()
        df_clean['Volatility'] = df_clean['Daily_Return'].rolling(window=20).std()
        df_clean['Ticker'] = ticker

        cleaned_data[ticker] = df_clean
        print(f"[OK] Cleaned {ticker}: {len(df_clean)} rows, missing values: {df_clean.isnull().sum().sum()}")

    return cleaned_data

def get_portfolio_stats(cleaned_data):
    stats = {}

    for ticker, df in cleaned_data.items():
        latest = df.iloc[-1]
        total_return = df['Cumulative_Return'].iloc[-1]
        avg_daily_return = df['Daily_Return'].mean()
        annual_volatility = df['Daily_Return'].std() * np.sqrt(252)

        stats[ticker] = {
            'Current_Price': latest['Adj Close'],
            'Total_Return_3Y': total_return,
            'Avg_Daily_Return': avg_daily_return,
            'Annual_Volatility': annual_volatility,
            'Latest_Date': df.index[-1],
            'MA_20': latest['MA_20'],
            'MA_50': latest['MA_50'],
        }

    return pd.DataFrame(stats).T

if __name__ == "__main__":
    from data_fetcher_mock import fetch_stock_data

    portfolio = ["AAPL", "MSFT", "JPM", "JNJ", "XOM"]
    raw_data = fetch_stock_data(portfolio)
    cleaned_data = clean_stock_data(raw_data)
    stats = get_portfolio_stats(cleaned_data)

    print("\n=== PORTFOLIO STATISTICS ===")
    print(stats)
