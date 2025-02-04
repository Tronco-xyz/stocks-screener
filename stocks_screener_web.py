import yfinance as yf

# Test fetching data manually
ticker = "SPY"
start_date = "2024-01-01"
end_date = "2024-12-31"

df = yf.download(ticker, start=start_date, end=end_date)

if df.empty:
    print(f"❌ No data for {ticker}. Possible API issue.")
else:
    print(f"✅ Successfully retrieved data for {ticker}:")
    print(df.head())
