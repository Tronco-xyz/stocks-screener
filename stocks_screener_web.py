import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from scipy.stats import rankdata

# Stock ticker list (same as before)
stock_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]  # Sample for testing

# Streamlit UI
st.title("SP500 Stocks Screener & RS Ranking")
st.write("Live Stocks ranking based on relative strength vs SP500.")

# Fetch historical price data from Yahoo Finance
st.write("Fetching latest data...")
all_symbols = stock_symbols + ["SPY"]  # Add SPY for benchmark comparison
stock_data = yf.download(all_symbols, period="1y", interval="1d")
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
valid_stocks = [stock for stock in stock_symbols if available_days[stock] >= 63]
stock_data = stock_data[valid_stocks + ["SPY"]]

# Calculate performance over different periods
performance = {}
spy_performance = {}
for period, days in lookback_periods.items():
    performance[period] = {
        stock: round(((stock_data[stock].iloc[-1] - stock_data[stock].iloc[-days]) / stock_data[stock].iloc[-days] * 100), 2)
        if available_days[stock] >= days else np.nan for stock in valid_stocks
    }
    if available_days["SPY"] >= days:
        spy_performance[period] = round(((stock_data["SPY"].iloc[-1] - stock_data["SPY"].iloc[-days]) / stock_data["SPY"].iloc[-days] * 100), 2)
    else:
        spy_performance[period] = np.nan  # Handle missing SPY data gracefully

performance_df = pd.DataFrame(performance)

# Fill missing values to avoid NaN issues
performance_df.fillna(0, inplace=True)

# Calculate RS vs SPY with error handling
for period in lookback_periods.keys():
    if not np.isnan(spy_performance[period]) and spy_performance[period] != 0:  # Ensure SPY data is available and non-zero
        performance_df[f"RS vs SPY {period}"] = performance_df[period] / spy_performance[period]
    else:
        performance_df[f"RS vs SPY {period}"] = np.nan  # Avoid division errors

# Replace infinite values with NaN
performance_df.replace([np.inf, -np.inf], np.nan, inplace=True)

# Normalize RS vs SPY into a percentile ranking (0-100)
for period in lookback_periods.keys():
    if performance_df[f"RS vs SPY {period}"].notna().any():
        performance_df[f"RS vs SPY {period}"] = rankdata(performance_df[f"RS vs SPY {period}"], method="average") / len(performance_df[f"RS vs SPY {period}"]) * 100

# Calculate moving averages
ma_200 = stock_data.rolling(window=200).mean()
ema_5 = stock_data.ewm(span=5, adjust=False).mean()
ema_20 = stock_data.ewm(span=20, adjust=False).mean()

# Determine if price is above 200-day SMA
above_ma_200 = stock_data.iloc[-1] > ma_200.iloc[-1]

# Determine EMA trend (Ensure Index Alignment)
ema_trend_values = np.where(ema_5.iloc[-1].reindex(valid_stocks) > ema_20.iloc[-1].reindex(valid_stocks), "EMA 5 > EMA 20", "EMA 5 < EMA 20")
ema_trend = pd.Series(ema_trend_values, index=valid_stocks)

# Prepare final screening table
data_table = pd.DataFrame({
    "Stock Ticker": performance_df.index,
    "RS vs SPY 1Y": performance_df["RS vs SPY 1Y"].round(2),
    "RS vs SPY 3Q": performance_df["RS vs SPY 3Q"].round(2),
    "RS vs SPY 2Q": performance_df["RS vs SPY 2Q"].round(2),
    "RS vs SPY 1Q": performance_df["RS vs SPY 1Q"].round(2),
    "RS vs SPY 1M": performance_df["RS vs SPY 1M"].round(2),
    "RS vs SPY 1W": performance_df["RS vs SPY 1W"].round(2),
    "Above 200 SMA": above_ma_200.reindex(performance_df.index).fillna(False).tolist(),
    "EMA Trend": ema_trend.reindex(performance_df.index).fillna("Unknown").tolist()
})

# Display screener table
st.dataframe(data_table.sort_values(by="RS vs SPY 1Y", ascending=False))

# Download button
st.download_button(
    label="Download CSV",
    data=data_table.to_csv(index=False),
    file_name="stock_screener.csv",
    mime="text/csv"
)
