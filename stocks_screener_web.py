import yfinance as yf
import pandas as pd
import numpy as np
from scipy.stats import percentileofscore
import streamlit as st

# Define ETFs to screen and benchmark (S&P 500) - Add more ETF symbols if needed!  
etf_symbols = ['QQQ', 'SPY', 'DIA', 'ARKK', 'XLK', 'XLF'] # Example list, expand it as desired
benchmark_symbol = 'SPY' 

lookback_periods = [63, 126, 189]  # Number of days for each lookback period (adjust if needed)
weights = [0.33, 0.34, 0.33]  # Weights to apply to each lookback period

# User-configurable options in Streamlit's sidebar
st.sidebar.title("ETF Screener - RS Rating")
selected_etfs = st.sidebar.multiselect("Select ETFs:", options=etf_symbols) 


def get_data(tickers, start_date, end_date):
    """Fetches historical closing price data for specified tickers."""

    try:
        df = yf.download(tickers, start=start_date, end=end_date)['Close']  # Download data 
        return df 
    except Exception as e: 
        print(f"Error fetching data: {e}") # Log the error for debugging

def calculate_rs_rating(etf_prices):
    """Calculates RS ratings based on relative performance."""

    returns = etf_prices.pct_change()  # Calculate daily returns for each ETF
    weighted_avg = (weights[0] * returns.rolling(lookback_periods[0]).mean() + 
                    weights[1] * returns.rolling(lookback_periods[1]).mean() + 
                    weights[2] * returns.rolling(lookback_periods[2]).mean())  

    rs = weighted_avg / benchmark_prices.pct_change().rolling(window=60).mean() # Adjust window as needed for the benchmark's performance period
   return rs


if selected_etfs: 

    try:
        start_date = "2023-01-01"  # Set your desired start date (YYYY-MM-DD)
        end_date = "2023-10-26" # Set your desired end date (YYYY-MM-DD)

        all_data = get_data(selected_etfs + [benchmark_symbol], start_date, end_date) 

        # Calculate RS ratings
        rs_ratings = {}  
        for etf in selected_etfs:  
            performance = calculate_rs_rating(all_data[etf]) # Calculate performance for each ETF individually. Replace 'benchmark' with the benchmark ticker if needed!    
            rs_ratings[etf] = performance.mean() 

        # Rank ETFs on a scale of 1-99 (use percentileofscore) - Adjust as needed based on your dataset and ranking logic

    except ValueError as e:
        st.error(str(e))


