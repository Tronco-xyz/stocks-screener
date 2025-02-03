import yfinance as yf
import pandas as pd
import numpy as np

def get_etf_data(ticker, period='1y', interval='1d'):
    """Fetches historical data for an ETF from Yahoo Finance."""
    etf = yf.Ticker(ticker)
    data = etf.history(period=period, interval=interval)
    return data

def calculate_rsi(data, window=14):
    """Calculates the Relative Strength Index (RSI)."""
    delta = data['Close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    
    avg_gain = pd.Series(gain).rolling(window=window, min_periods=1).mean()
    avg_loss = pd.Series(loss).rolling(window=window, min_periods=1).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    data['RSI'] = rsi
    return data

def get_rsi_for_timeframes(ticker):
    """Fetches ETF data and calculates RSI for daily, weekly, and monthly timeframes."""
    daily_data = get_etf_data(ticker, period='6mo', interval='1d')
    weekly_data = get_etf_data(ticker, period='2y', interval='1wk')
    monthly_data = get_etf_data(ticker, period='5y', interval='1mo')
    
    daily_rsi = calculate_rsi(daily_data)
    weekly_rsi = calculate_rsi(weekly_data)
    monthly_rsi = calculate_rsi(monthly_data)
    
    return {
        'Daily RSI': daily_rsi['RSI'].iloc[-1],
        'Weekly RSI': weekly_rsi['RSI'].iloc[-1],
        'Monthly RSI': monthly_rsi['RSI'].iloc[-1]
    }

def screen_etfs(etf_list):
    """Screens multiple ETFs and returns their RSI values."""
    results = []
    for etf in etf_list:
        try:
            rsi_values = get_rsi_for_timeframes(etf)
            results.append({'Ticker': etf, **rsi_values})
        except Exception as e:
            print(f"Error fetching data for {etf}: {e}")
    
    df = pd.DataFrame(results)
    return df

# Example usage
etfs = ['SPY', 'QQQ', 'DIA', 'ARKK', 'VTI']  # Add more ETFs as needed
etf_screener_results = screen_etfs(etfs)
print(etf_screener_results)
