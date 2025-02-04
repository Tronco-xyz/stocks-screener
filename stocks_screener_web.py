import yfinance as yf

# Test fetching data manually in Streamlit
ticker = "SPY"
start_date = "2024-01-01"
end_date = "2024-12-31"

df = yf.download(ticker, start=start_date, end=end_date)

import streamlit as st

st.write(f"Fetching data for {ticker} from {start_date} to {end_date}...")

if df.empty:
    st.error(f"❌ No data for {ticker}. Possible API issue.")
else:
    st.success(f"✅ Successfully retrieved data for {ticker}!")
    st.write(df.head())  # Show the first few rows
