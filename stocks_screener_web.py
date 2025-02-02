import requests
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

# Alpha Vantage API Key
API_KEY = "7R2S6Y8ZU9LGA4BQ"

# Define stock list (You can modify this later)
stock_list = ["AAPL", "META", "TSLA", "STC", "NVDA", "GOOGL", "MSFT", "AMZN", "NFLX", "AMD"]

# Function to fetch historical data from Alpha Vantage
def get_stock_data(symbol):
    url = f"https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": symbol,
        "apikey": API_KEY,
        "outputsize": "full",
        "datatype": "json"
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if "Time Series (Daily)" not in data:
        st.error(f"Error fetching data for {symbol}. Check API limits.")
        return None
    
    df = pd.DataFrame(data["Time Series (Daily)"]).T
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    df = df.rename(columns={"5. adjusted close": "Close"})
    df["Close"] = df["Close"].astype(float)
    
    return df[["Close"]]

# Fetch S&P 500 data (Using SPY ETF as a proxy)
st.write("Fetching S&P 500 Data...")
sp500 = get_stock_data("SPY")

# Fetch stock data
st.write("Fetching Stock Data...")
stock_data = {symbol: get_stock_data(symbol) for symbol in stock_list}

# Function to calculate Relative Strength (RS)
def calculate_relative_strength(stock_prices, sp500_prices):
    rs_values = {}
    
    for symbol, prices in stock_prices.items():
        if prices is None:
            continue  # Skip stocks without data
        
        rs_ratio = prices["Close"] / sp500_prices["Close"]
        
        # Compute RS over different timeframes
        rs_1w = (rs_ratio / rs_ratio.shift(5) - 1) * 100
        rs_1m = (rs_ratio / rs_ratio.shift(21) - 1) * 100
        rs_3m = (rs_ratio / rs_ratio.shift(63) - 1) * 100
        rs_6m = (rs_ratio / rs_ratio.shift(126) - 1) * 100
        rs_1y = (rs_ratio / rs_ratio.shift(252) - 1) * 100
        
        rs_values[symbol] = pd.DataFrame({
            "RS_1W": rs_1w,
            "RS_1M": rs_1m,
            "RS_3M": rs_3m,
            "RS_6M": rs_6m,
            "RS_1Y": rs_1y
        })
    
    return rs_values

# Compute RS for stocks
st.write("Calculating Relative Strength...")
rs_scores = calculate_relative_strength(stock_data, sp500)

# Function to rank stocks with weighted RS
def rank_stocks(rs_data):
    latest_rs = {symbol: df.iloc[-1] for symbol, df in rs_data.items() if not df.empty}
    ranked_df = pd.DataFrame(latest_rs).T
    
    # Apply weighted ranking (1M & 3M get double weight)
    ranked_df["RS_Avg"] = (ranked_df["RS_1W"] + 
                            2 * ranked_df["RS_1M"] + 
                            2 * ranked_df["RS_3M"] + 
                            ranked_df["RS_6M"] + 
                            ranked_df["RS_1Y"]) / 6
    
    ranked_df = ranked_df.sort_values(by="RS_Avg", ascending=False)
    return ranked_df

# Rank stocks
st.write("Ranking Stocks...")
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
