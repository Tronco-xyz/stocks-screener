import yfinance as yf
import pandas as pd
import talib

# Define your ticker symbols and period (e.g., one year)
tickers = ["AAPL", "MSFT"]  # Add more tickers here if needed
period = "1y" 

# Download historical data using yfinance
data_multiple = yf.download(tickers, period=period) 

# Calculate Relative Strength (RS): This requires S&P 500 data which needs to be downloaded separately
spx_data = yf.download("SPX", period=period)  # Download SPX data for the same period
for ticker in tickers:
    data_multiple[ticker]['RS'] = data_multiple[ticker]['Close'] / spx_data['Adj Close'] 

# Calculate RSI using talib library 
for ticker in tickers:
    data_multiple[ticker]['RSI_14'] = talib.RSI(data_multiple[ticker]['Close'], timeperiod=14)   

# Define your screening criteria (adjust these values based on your strategy)
rs_threshold = 1.2 
rsi_level = 40

# Filter the data based on RS and RSI
filtered_data = data_multiple[(data_multiple['RS'] > rs_threshold) & \
                             (data_multiple['RSI_14'] < rsi_level)]

print("\n-------------------\nFiltered Stock Data:\n-------------------")
print(filtered_data[['Close', 'RS', 'RSI_14']]) 


