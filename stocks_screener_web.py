import yfinance as yf
import pandas as pd
import numpy as np
from scipy.stats import percentileofscore
import streamlit as st

# Define the ETFs to screen and the benchmark (S&P 500)
etf_symbols = ['QQQ', 'SPY', 'DIA', 'ARKK', 'XLK', 'XLF', 'XLV']  # Add more as needed
benchmark_symbol = 'SPY'  # Ensure benchmark is uppercase
lookback_periods = [63, 126, 189, 252]  # 3 months, 6 months, 9 months, 12 months
weights = [0.4, 0.2, 0.2, 0.2]  # Weights for each period

# Fetch historical data
def get_data(symbols, start, end):
    data = {}
    failed_symbols = []
    for symbol in symbols:
        print(f"Fetching data for {symbol} from {start} to {end}...")
        try:
            df = yf.download(symbol, start=start, end=end)
            
            if df.empty:
                print(f"⚠️ No data for {symbol}. Skipping...")
                failed_symbols.append(symbol)
                continue  # Skip this symbol if no data
            
            # Adjust for MultiIndex DataFrame (Yahoo sometimes returns 'Price' as top level)
            if isinstance(df.columns, pd.MultiIndex):
                if 'Close' in df.columns.get_level_values(1):  
                    df = df.xs('Close', level=1, axis=1)  # Extract 'Close' prices only
            
            # If 'Close' column is still missing, try 'Adj Close' as fallback
            if 'Close' not in df.columns:
                if 'Adj Close' in df.columns:
                    df['Close'] = df['Adj Close']  # Use 'Adj Close' if available
                else:
                    print(f"⚠️ No 'Close' or 'Adj Close' column for {symbol}. Full response:\n{df.head()}")
                    failed_symbols.append(symbol)
                    continue  # Skip if no valid closing price is found
            
            print(f"✅ Data retrieved for {symbol}:\n{df.head()}")
            data[symbol] = df['Close']
        except Exception as e:
            print(f"❌ Error retrieving {symbol}: {e}")
            failed_symbols.append(symbol)
            continue
    
    if failed_symbols:
        print(f"❌ Failed to retrieve data for: {', '.join(failed_symbols)}")
    
    if not data:
        print("❌ No valid data retrieved. Possible API issue or incorrect ticker symbols.")
        raise ValueError("No valid data retrieved for any symbol.")
    
    return pd.DataFrame(data)

# Get data for ETFs and S&P 500
start_date = '2024-01-01'  # Reduce date range for testing
end_date = '2024-12-31'
try:
    all_data = get_data(etf_symbols + [benchmark_symbol], start_date, end_date)
except ValueError as e:
    st.error(str(e))
    st.stop()

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
rs_df = pd.DataFrame({'ETF': list(rs_ratings.keys()), 'RS Rating': list(rs_ratings.values())})
rs_df = rs_df.sort_values(by='RS Rating', ascending=False)

# Streamlit UI
st.title("ETF Screener - RS Rating")
st.write("This app calculates and ranks ETFs based on their relative strength compared to the S&P 500.")
st.dataframe(rs_df)
