import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from scipy.stats import rankdata

# Stock ticker list (same as before)
stock_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]  # Sample for testing

# Streamlit UI
st.title("SP500 Stocks Screener & RS Ranking")
st.write("Live Stocks ranking based on relative strength.")

# Fetch historical price data from Yahoo Finance
st.write("Fetching latest data...")
stock_data = yf.download(stock_symbols, period="1y", interval="1d")
if stock_data.empty:
    st.error("Yahoo Finance returned empty data. Check stock symbols and API limits.")
    st.stop()

# Extract 'Close' prices
if isinstance(stock_data.columns, pd.MultiIndex):
    stock_data = stock_data['Close']

# Ensure stocks have enough data
available_days = stock_data.count()
max_days = available_days.max()

# Define time periods
lookback_periods = {"1Y": 252, "3Q": 189, "2Q": 126, "1Q": 63, "1M": 21, "1W": 5}
valid_stocks = [stock for stock in stock_data.columns if available_days[stock] >= 63]
stock_data = stock_data[valid_stocks]

# Calculate performance over different periods
performance = {}
for period, days in lookback_periods.items():
    performance[period] = {
        stock: round(((stock_data[stock].iloc[-1] - stock_data[stock].iloc[-days]) / stock_data[stock].iloc[-days] * 100), 2)
        if available_days[stock] >= days else np.nan for stock in valid_stocks
    }
performance_df = pd.DataFrame(performance)

# Calculate RS General score based on new formula
performance_df["RS General"] = (performance_df["1Q"] * 2) + performance_df["2Q"] + performance_df["3Q"] + performance_df["1Y"]

# Normalize RS General as a percentile score
performance_df["RS General Percentile"] = rankdata(performance_df["RS General"], method="average") / len(performance_df["RS General"]) * 100

# Calculate moving averages
ma_200 = stock_data.rolling(window=200).mean()
ema_5 = stock_data.ewm(span=5, adjust=False).mean()
ema_20 = stock_data.ewm(span=20, adjust=False).mean()

# Determine if price is above 200-day SMA
above_ma_200 = stock_data.iloc[-1] > ma_200.iloc[-1]

# Determine EMA trend
ema_trend = pd.Series(np.where(ema_5.iloc[-1] > ema_20.iloc[-1], "EMA 5 > EMA 20", "EMA 5 < EMA 20"), index=valid_stocks)

# Prepare final screening table
data_table = pd.DataFrame({
    "Stock Ticker": performance_df.index,
    "RS General": performance_df["RS General Percentile"].round(2),
    "RS 1W": performance_df["1W"].round(2),
    "RS 1M": performance_df["1M"].round(2),
    "RS 3M": performance_df["3Q"].round(2),
    "Above 200 SMA": above_ma_200.reindex(performance_df.index).fillna(False).tolist(),
    "EMA Trend": ema_trend.reindex(performance_df.index).fillna("Unknown").tolist()
})

# Display screener table
st.dataframe(data_table.sort_values(by="RS General", ascending=False))

# Download button
st.download_button(
    label="Download CSV",
    data=data_table.to_csv(index=False),
    file_name="stock_screener.csv",
    mime="text/csv"
)
