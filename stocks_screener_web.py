import yfinance as yf
import pandas as pd
from datetime import date, timedelta 

import streamlit as st

# --- Function to calculate Relative Strength (RS) --- #
def calculate_rs(df, period):
  """Calculates RS for a given DataFrame and time period."""

  if period == '6 Months':   
    target_date = date.today() - timedelta(days=180) 
  elif period == '3 Months': 
    target_date = date.today() - timedelta(days=90)
  elif period == '10 Days':
    target_date = date.today() - timedelta(days=10)

  df['Close'] = df[period].fillna(method='ffill') # Fill missing values with forward fill
  rs = (df['Close'][target_date] / df['Close'].iloc[-2]) 
  return rs   

# --- Streamlit App Setup --- #

st.title("S&P 500 Relative Strength Analysis")

# Get a list of S&P 500 tickers
sp500_tickers = yf.Ticker("^GSPC").info['constituents']  

selected_stocks = st.multiselect("Select Stocks (up to 10):", sp500_tickers)   # Allow users to choose stocks

if selected_stocks: # Only proceed if stocks are selected
    start_date = date(2023, 1, 1)  # Set a starting date for data retrieval
    end_date = date.today()       

    data = yf.download(tickers=selected_stocks, start=start_date, end=end_date)['Close']  
   
    for stock in selected_stocks:
        stock_df = data[stock].copy() 


        # Calculate RS for different periods and display results using Streamlit's table component

       st.subheader(f"{stock}") # Add a subheader for each stock 
       rs_6m = calculate_rs(stock_df, '6 Months')  
       rs_3m = calculate_rs(stock_df, '3 Months')   
       rs_10d = calculate_rs(stock_df, '10 Days')

       with st.expander("Relative Strength"): # Expandable section for RS details 
           st.write(f"6 Months: {rs_6m:.2%}")  
           st.write(f"3 Months: {rs_3m:.2%}")    
           st.write(f"10 Days: {rs_10d:.2%}")      


