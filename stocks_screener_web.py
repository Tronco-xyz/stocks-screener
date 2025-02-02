import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

# Define stock list
stock_list = ["AAPL", "META", "TSLA", "STC", "NVDA", "GOOGL", "MSFT", "AMZN", "NFLX", "AMD"]

# Function to fetch historical data from Yahoo Finance
def get_stock_data(symbol, period="1y"):
    try:
        stock = yf.download(symbol, period=period, interval="1d", progress=False)
        
        # Check for 'Adj Close' or fallback to 'Close'
        if "Adj Close" in stock.columns:
            return stock["Adj Close"]
        elif "Close" in stock.columns:
            return stock["Close"]
        else:
            st.warning(f"❌ No 'Close' or 'Adj Close' data for {symbol}.")
            return None
    except Exception as e:
        st.warning(f"❌ Error fetching data for {symbol}: {e}")
        return None

# Fetch S&P 500 data (Using SPY ETF as a proxy)
st.write("🔄 Fetching S&P 500 Data (SPY ETF)...")
sp500 = get_stock_data("^GSPC")

# Ensure SPY data is available
if sp500 is None or sp500.empty:
    st.error("🚨 Failed to fetch S&P 500 data. Please check Yahoo Finance connectivity.")
    st.stop()

# Fetch stock data with error handling
st.write("🔄 Fetching Stock Data...")
valid_stocks = {}

for symbol in stock_list:
    data = get_stock_data(symbol)
    if data is not None and not data.empty:
        valid_stocks[symbol] = data
    else:
        st.warning(f"⚠️ Skipping {symbol} due to missing or invalid data.")

# Replace stock_data with only valid stocks
stock_data = valid_stocks

# Function to calculate Relative Strength (RS)
def calculate_relative_strength(stock_prices, sp500_prices):
    rs_values = {}
    
    for symbol, prices in stock_prices.items():
        if prices is None or sp500_prices is None or prices.empty or sp500_prices.empty:
            st.warning(f"⚠️ Skipping {symbol} due to missing data.")
            continue  # Skip stocks without valid data

        # Ensure we have enough history (at least 252 days for 1-year RS)
        if len(prices) < 252 or len(sp500_prices) < 252:
            st.warning(f"⚠️ Skipping {symbol} - Not enough historical data.")
            continue

        rs_ratio = prices / sp500_prices  # Stock Price / S&P 500 Price

        # Compute RS over different timeframes
        rs_1w = (rs_ratio / rs_ratio.shift(5) - 1) * 100
        rs_1m = (rs_ratio / rs_ratio.shift(21) - 1) * 100
        rs_3m = (rs_ratio / rs_ratio.shift(63) - 1) * 100
        rs_6m = (rs_ratio / rs_ratio.shift(126) - 1) * 100
        rs_1y = (rs_ratio / rs_ratio.shift(252) - 1) * 100

        # Drop rows with NaN values before storing the results
        rs_data = pd.DataFrame({
            "RS_1W": rs_1w,
            "RS_1M": rs_1m,
            "RS_3M": rs_3m,
            "RS_6M": rs_6m,
            "RS_1Y": rs_1y
        }).dropna()

        # Ensure at least one valid row exists before saving
        if rs_data.empty:
            st.warning(f"⚠️ Skipping {symbol} - Insufficient data after dropping NaNs.")
            continue
        
        rs_values[symbol] = rs_data
    
    return rs_values

# Compute RS for stocks
st.write("📊 Calculating Relative Strength...")
rs_scores = calculate_relative_strength(stock_data, sp500)

# Function to rank stocks with weighted RS
def rank_stocks(rs_data):
    if not rs_data:  # If no stocks have valid RS data, stop execution
        st.error("🚨 No valid Relative Strength data available. Try again later.")
        st.stop()

    latest_rs = {symbol: df.iloc[-1] for symbol, df in rs_data.items() if not df.empty}
    ranked_df = pd.DataFrame(latest_rs).T

    # Ensure valid RS columns exist before ranking
    required_columns = ["RS_1W", "RS_1M", "RS_3M", "RS_6M", "RS_1Y"]
    if not all(col in ranked_df.columns for col in required_columns):
        st.error("🚨 RS calculation failed due to missing columns.")
        st.stop()

    # Apply weighted ranking (1M & 3M get double weight)
    ranked_df["RS_Avg"] = (ranked_df["RS_1W"] + 
                            2 * ranked_df["RS_1M"] + 
                            2 * ranked_df["RS_3M"] + 
                            ranked_df["RS_6M"] + 
                            ranked_df["RS_1Y"]) / 6

    ranked_df = ranked_df.sort_values(by="RS_Avg", ascending=False)
    return ranked_df

# Rank stocks
st.write("🏆 Ranking Stocks...")
ranked_stocks = rank_stocks(rs_scores)

# Streamlit Dashboard
st.title("📈 Stock Screener - Relative Strength Analysis")

# Display Ranked Table
st.subheader("Ranked Stocks by Weighted Relative Strength")
st.dataframe(ranked_stocks)

# Plot Ranking Chart
fig = px.bar(
    ranked_stocks,
    x=ranked_stocks.index,
    y="RS_Avg",
    title="Stock Ranking by Weighted Relative Strength",
    text="RS_Avg",
)
st.plotly_chart(fig)
