import yfinance as yf
import pandas as pd
import numpy as np
from scipy.stats import percentileofscore
import streamlit as st

# Define the ETFs to screen and the benchmark (S&P 500)
etf_symbols = ['QQQ', 'SPY', 'DIA', 'ARKK', 'XLK', 'XLF', 'XLV']  # Add more as needed
benchmark_symbol = '^GSPC'  # S&P 500
lookback_periods = [63, 126, 189, 252]  # 3 months, 6 months, 9 months, 12 months
weights = [0.4, 0.2, 0.2, 0.2]  # Weights for each period

# Fetch historical data
def get_data(symbols, start, end):
    data = {}
    for symbol in symbols:
        df = yf.download(symbol, start=start, end=end)
        if df.empty:
            print(f"⚠️ No data for {symbol} - Check ticker symbol or API limits")
        else:
            data[symbol] = df['Adj Close']
    return pd.DataFrame(data)

# Get data for ETFs and S&P 500
start_date = '2023-01-01'
end_date = '2025-01-01'
all_data = get_data(etf_symbols + [benchmark_symbol], start_date, end_date)

# Check if data is available
if all_data.empty:
    st.error("No data retrieved. Check ticker symbols and API availability.")
    st.stop()

# Calculate performance over lookback periods
def calc_performance(data, lookbacks):
    perf = {}
    for period in lookbacks:
        perf[period] = data.pct_change(period).iloc[-1] + 1  # Compute returns
    return perf

# Compute relative strength scores
perf_etfs = calc_performance(all_data[etf_symbols], lookback_periods)
perf_benchmark = calc_performance(all_data[benchmark_symbol], lookback_periods)

rs_scores = {}
for etf in etf_symbols:
    weighted_rs = sum(
        weights[i] * (perf_etfs[lookback_periods[i]][etf] / perf_benchmark[lookback_periods[i]])
        for i in range(len(lookback_periods))
    ) * 100
    rs_scores[etf] = weighted_rs

# Rank ETFs on a scale of 1-99
rs_values = list(rs_scores.values())
rs_ratings = {etf: percentileofscore(rs_values, rs_scores[etf], kind='rank') for etf in etf_symbols}

# Convert to DataFrame for display
rs_df = pd.DataFrame({'ETF': rs_ratings.keys(), 'RS Rating': rs_ratings.values()})
rs_df = rs_df.sort_values(by='RS Rating', ascending=False)

# Streamlit UI
st.title("ETF Screener - RS Rating")
st.write("This app calculates and ranks ETFs based on their relative strength compared to the S&P 500.")
st.dataframe(rs_df)
