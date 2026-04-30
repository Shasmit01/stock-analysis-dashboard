#!/usr/bin/env python
import sys
print("Python version:", sys.version)

try:
    import yfinance as yf
    print("[OK] yfinance imported")

    print("Attempting to download AAPL data...")
    data = yf.download('AAPL', start='2024-01-01', end='2024-02-01', progress=False)

    if data.empty:
        print("[ERROR] No data returned")
    else:
        print(f"[OK] Downloaded {len(data)} rows")
        print(data.head())

except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
