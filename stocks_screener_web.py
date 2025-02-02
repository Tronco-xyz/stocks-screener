import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from scipy.stats import rankdata

# Fetch S&P 500 stock symbols
@st.cache_data
def get_sp500_stocks():
    table = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
    return table["Symbol"].tolist()

stock_symbols = get_sp500_stocks()

# Streamlit UI
st.title("Stock Screener & RS Ranking")
st.write("Live stock ranking based on relative strength.")

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

# Adjust 12M lookback dynamically
lookback_periods = {"12M": min(252, max_days), "3M": 63, "1M": 21, "1W": 5}

valid_stocks = [stock for stock in stock_data.columns if available_days[stock] >= 63]
stock_data = stock_data[valid_stocks]

# Calculate performance over available periods
performance = {}
for period, days in lookback_periods.items():
    performance[period] = {
        stock: round(((stock_data[stock].iloc[-1] - stock_data[stock].iloc[-days]) / stock_data[stock].iloc[-days] * 100), 2)
        if available_days[stock] >= days else np.nan for stock in valid_stocks
    }

performance_df = pd.DataFrame(performance)

# Calculate moving averages
ma_200 = stock_data.rolling(window=200).mean()
ma_50 = stock_data.rolling(window=50).mean()
ema_5 = stock_data.ewm(span=5, adjust=False).mean()
ema_20 = stock_data.ewm(span=20, adjust=False).mean()

# Determine if price is above or below 200-day & 50-day MA
above_ma_200 = stock_data.iloc[-1] > ma_200.iloc[-1]
above_ma_50 = stock_data.iloc[-1] > ma_50.iloc[-1]
ema_trend = pd.Series(np.where(ema_5.iloc[-1] > ema_20.iloc[-1], "EMA 5 > EMA 20", "EMA 5 < EMA 20"), index=valid_stocks)

# Calculate RS Rankings (percentile-based scores from 1-99)
rs_ratings = {}
for period in lookback_periods.keys():
    valid_performance = performance_df[period].dropna()
    ranked = rankdata(valid_performance, method="average") / len(valid_performance) * 99
    rs_ratings[period] = dict(zip(valid_performance.index, np.round(ranked, 2)))

rs_ratings_df = pd.DataFrame(rs_ratings, index=performance_df.index).fillna(np.nan)

# Add filters
st.sidebar.header("Filters")
filter_rs_12m = st.sidebar.checkbox("RS 12M > 80")
filter_above_ma_200 = st.sidebar.checkbox("Above 200 MA")
filter_above_ma_50 = st.sidebar.checkbox("Above 50 MA")
filter_ema_trend = st.sidebar.checkbox("EMA 5 > EMA 20")

# Store results in a DataFrame
stock_ranking = pd.DataFrame({
    "Stock": performance_df.index,
    "RS Rating 12M": rs_ratings_df["12M"].tolist(),
    "RS Rating 3M": rs_ratings_df["3M"].tolist(),
    "RS Rating 1M": rs_ratings_df["1M"].tolist(),
    "RS Rating 1W": rs_ratings_df["1W"].tolist(),
    "Above 200 MA": above_ma_200.reindex(performance_df.index).fillna(False).tolist(),
    "Above 50 MA": above_ma_50.reindex(performance_df.index).fillna(False).tolist(),
    "EMA Trend": ema_trend.reindex(performance_df.index).fillna("Unknown").tolist()
})

# Apply filters safely
if filter_rs_12m:
    stock_ranking = stock_ranking[stock_ranking["RS Rating 12M"] > 80]
if filter_above_ma_200:
    stock_ranking = stock_ranking[stock_ranking["Above 200 MA"]]
if filter_above_ma_50:
    stock_ranking = stock_ranking[stock_ranking["Above 50 MA"]]
if filter_ema_trend:
    stock_ranking = stock_ranking[stock_ranking["EMA Trend"] == "EMA 5 > EMA 20"]

# Add performance metrics at the end, ensuring proper alignment
performance_columns = ["12M Performance (%)", "3M Performance (%)", "1M Performance (%)", "1W Performance (%)"]
for col in performance_columns:
    period = col.replace(" Performance (%)", "")
    if period in performance_df.columns:
        stock_ranking[col] = performance_df[period].reindex(stock_ranking["Stock"]).values

# Ensure only two decimal places for all numerical columns
for col in stock_ranking.select_dtypes(include=[np.number]).columns:
    stock_ranking[col] = stock_ranking[col].round(2)

# Display Stock Rankings in Streamlit
st.dataframe(stock_ranking.sort_values(by="RS Rating 12M", ascending=False))

# Download Button
st.download_button(
    label="Download CSV",
    data=stock_ranking.to_csv(index=False),
    file_name="stock_ranking.csv",
    mime="text/csv"
)
