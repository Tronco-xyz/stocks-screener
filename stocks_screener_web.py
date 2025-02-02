import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from scipy.stats import rankdata

# Stock ticker list (same as before)
stock_symbols = ["MMM", "AOS", "ABT", "ABBV", "ACN", "ADBE", "AMD", "AES", "AFL", "A", "APD", "ABNB", "AKAM",
    "ALB", "ARE", "ALGN", "ALLE", "LNT", "ALL", "GOOGL", "GOOG", "MO", "AMZN", "AMCR", "AEE", "AEP",
    "AXP", "AIG", "AMT", "AWK", "AMP", "AME", "AMGN", "APH", "ADI", "ANSS", "AON", "APA", "APO",
    "AAPL", "AMAT", "APTV", "ACGL", "ADM", "ANET", "AJG", "AIZ", "T", "ATO", "ADSK", "ADP", "AZO",
    "AVB", "AVY", "AXON", "BKR", "BALL", "BAC", "BAX", "BDX", "BRK.B", "BBY", "TECH", "BIIB", "BLK",
    "BX", "BK", "BA", "BKNG", "BWA", "BSX", "BMY", "AVGO", "BR", "BRO", "BF.B", "BLDR", "BG", "BXP",
    "CHRW", "CDNS", "CZR", "CPT", "CPB", "COF", "CAH", "KMX", "CCL", "CARR", "CAT", "CBOE", "CBRE",
    "CDW", "CE", "COR", "CNC", "CNP", "CF", "CRL", "SCHW", "CHTR", "CVX", "CMG", "CB", "CHD", "CI",
    "CINF", "CTAS", "CSCO", "C", "CFG", "CLX", "CME", "CMS", "KO", "CTSH", "CL", "CMCSA", "CAG", "COP",
    "ED", "STZ", "CEG", "COO", "CPRT", "GLW", "CPAY", "CTVA", "CSGP", "COST", "CTRA", "CRWD", "CCI",
    "CSX", "CMI", "CVS", "DHR", "DRI", "DVA", "DAY", "DECK", "DE", "DELL", "DAL", "DVN", "DXCM",
    "FANG", "DLR", "DFS", "DG", "DLTR", "D", "DPZ", "DOV", "DOW", "DHI", "DTE", "DUK", "DD", "EMN",
    "ETN", "EBAY", "ECL", "EIX", "EW", "EA", "ELV", "EMR", "ENPH", "ETR", "EOG", "EPAM", "EQT",
    "EFX", "EQIX", "EQR", "ERIE", "ESS", "EL", "EG", "EVRG", "ES", "EXC", "EXPE", "EXPD", "EXR",
    "XOM", "FFIV", "FDS", "FICO", "FAST", "FRT", "FDX", "FIS", "FITB", "FSLR", "FE", "FI", "FMC",
    "F", "FTNT", "FTV", "FOXA", "FOX", "BEN", "FCX", "GRMN", "IT", "GE", "GEHC", "GEV", "GEN",
    "GNRC", "GD", "GIS", "GM", "GPC", "GILD", "GPN", "GL", "GDDY", "GS", "HAL", "HIG", "HAS",
    "HCA", "DOC", "HSIC", "HSY", "HES", "HPE", "HLT", "HOLX", "HD", "HON", "HRL", "HST", "HWM",
    "HPQ", "HUBB", "HUM", "HBAN", "HII", "IBM", "IEX", "IDXX", "ITW", "INCY", "IR", "PODD",
    "INTC", "ICE", "IFF", "IP", "IPG", "INTU", "ISRG", "IVZ", "INVH", "IQV", "IRM", "JBHT",
    "JBL", "JKHY", "J", "JNJ", "JCI", "JPM", "JNPR", "K", "KVUE", "KDP", "KEY", "KEYS", "KMB",
    "KIM", "KMI", "KKR", "KLAC", "KHC", "KR", "LHX", "LH", "LRCX", "LW", "LVS", "LDOS", "LEN",
    "LII", "LLY", "LIN", "LYV", "LKQ", "LMT", "L", "LOW", "LULU", "LYB", "MTB", "MPC", "MKTX",
    "MAR", "MMC", "MLM", "MAS", "MA", "MTCH", "MKC", "MCD", "MCK", "MDT", "MRK", "META", "MET",
    "MTD", "MGM", "MCHP", "MU", "MSFT", "MAA", "MRNA", "MHK", "MOH", "TAP", "MDLZ", "MPWR",
    "MNST", "MCO", "MS", "MOS", "MSI", "MSCI", "NDAQ", "NTAP", "NFLX", "NEM", "NWSA", "NWS",
    "NEE", "NKE", "NI", "NDSN", "NSC", "NTRS", "NOC", "NCLH", "NRG", "NUE", "NVDA", "NVR",
    "NXPI", "ORLY", "OXY", "ODFL", "OMC", "ON", "OKE", "ORCL", "OTIS", "PCAR", "PKG", "PLTR",
    "PANW", "PARA", "PH", "PAYX", "PAYC", "PYPL", "PNR", "PEP", "PFE", "PCG", "PM", "PSX",
    "PNW", "PNC", "POOL", "PPG", "PPL", "PFG", "PG", "PGR", "PLD", "PRU", "PEG", "PTC", "PSA",
    "PHM", "PWR", "QCOM", "DGX", "RL", "RJF", "RTX", "O", "REG", "REGN", "RF", "RSG", "RMD",
    "RVTY", "ROK", "ROL", "ROP", "ROST", "RCL", "SPGI", "CRM", "SBAC", "SLB", "STX", "SRE",
    "NOW", "SHW", "SPG", "SWKS", "SJM", "SW", "SNA", "SOLV", "SO", "LUV", "SWK", "SBUX",
    "STT", "STLD", "STE", "SYK", "SMCI", "SYF", "SNPS", "SYY", "TMUS", "TROW", "TTWO",
    "TPR", "TRGP", "TGT", "TEL", "TDY", "TFX", "TER", "TSLA", "TXN", "TPL", "TXT", "TMO",
    "TJX", "TSCO", "TT", "TDG", "TRV", "TRMB", "TFC", "TYL", "TSN", "USB", "UBER", "UDR",
    "ULTA", "UNP", "UAL", "UPS", "URI", "UNH", "UHS", "VLO", "VTR", "VRSN", "VRSK", "VZ",
    "VRTX", "VICI", "V", "VST", "VMC", "WRB", "GWW", "WAB", "WBA", "WMT", "DIS", "WBD",
    "WM", "WAT", "WEC", "WFC", "WELL", "WST", "WDC", "WY", "WMB", "WTW", "WDAY", "WYNN",
    "XEL", "XYL", "YUM", "ZBRA", "ZBH", "ZTS"]  # Sample for testing

# Streamlit UI
st.title("SP500 Stocks Screener & RS Ranking")
st.write("Live Stocks ranking based on relative strength vs SP500.")

# Fetch historical price data from Yahoo Finance
st.write("Fetching latest data...")
all_symbols = stock_symbols + ["SPY"]  # Add SPY for benchmark comparison
try:
    stock_data = yf.download(all_symbols, period="1y", interval="1d")
except Exception as e:
    st.error(f"Error fetching data: {e}")
    st.stop()

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
    try:
        if available_days["SPY"] >= days and stock_data["SPY"].iloc[-days] != 0:
            spy_performance[period] = round(((stock_data["SPY"].iloc[-1] - stock_data["SPY"].iloc[-days]) / stock_data["SPY"].iloc[-days] * 100), 2)
        else:
            spy_performance[period] = np.nan
    except IndexError:
        spy_performance[period] = np.nan

    performance[period] = {}
    for stock in valid_stocks:
        try:
            if available_days[stock] >= days:
                performance[period][stock] = round(((stock_data[stock].iloc[-1] - stock_data[stock].iloc[-days]) / stock_data[stock].iloc[-days] * 100), 2)
            else:
                performance[period][stock] = np.nan
        except (KeyError, IndexError) as e:
            st.warning(f"Skipping {stock} due to error: {e}")
            performance[period][stock] = np.nan

performance_df = pd.DataFrame(performance)
performance_df.fillna(0, inplace=True)

# Calculate RS vs SPY safely
for period in lookback_periods.keys():
    if period in spy_performance and not np.isnan(spy_performance[period]) and spy_performance[period] != 0:
        performance_df[f"RS vs SPY {period}"] = np.where(
            performance_df[period] != 0,
            performance_df[period] / spy_performance[period],
            np.nan
        )
    else:
        performance_df[f"RS vs SPY {period}"] = np.nan

performance_df.replace([np.inf, -np.inf], np.nan, inplace=True)

# Normalize RS vs SPY into a percentile ranking (0-100)
for period in lookback_periods.keys():
    if f"RS vs SPY {period}" in performance_df.columns and performance_df[f"RS vs SPY {period}"].notna().any():
        performance_df[f"RS vs SPY {period}"] = rankdata(performance_df[f"RS vs SPY {period}"], method="average") / len(performance_df[f"RS vs SPY {period}"]) * 100

# Calculate moving averages
ma_200 = stock_data.rolling(window=200).mean()
ema_5 = stock_data.ewm(span=5, adjust=False).mean()
ema_20 = stock_data.ewm(span=20, adjust=False).mean()

# Determine if price is above 200-day SMA
above_ma_200 = stock_data.iloc[-1] > ma_200.iloc[-1]

# Determine EMA trend
ema_trend_values = np.where(ema_5.iloc[-1].reindex(valid_stocks) > ema_20.iloc[-1].reindex(valid_stocks), "EMA 5 > EMA 20", "EMA 5 < EMA 20")
ema_trend = pd.Series(ema_trend_values, index=valid_stocks)

# Compute stock volatility
volatility_1M = stock_data.pct_change().rolling(21).std().iloc[-1]
volatility_3M = stock_data.pct_change().rolling(63).std().iloc[-1]

# Prepare final screening table
data_table = pd.DataFrame({
    "Stock Ticker": performance_df.index,
    "RS vs SPY 1Y": performance_df["RS vs SPY 1Y"].round(2),
    "RS vs SPY 3Q": performance_df["RS vs SPY 3Q"].round(2),
    "RS vs SPY 2Q": performance_df["RS vs SPY 2Q"].round(2),
    "RS vs SPY 1Q": performance_df["RS vs SPY 1Q"].round(2),
    "RS vs SPY 1M": performance_df["RS vs SPY 1M"].round(2),
    "RS vs SPY 1W": performance_df["RS vs SPY 1W"].round(2),
    "Above 200 SMA": above_ma_200.reindex(performance_df.index).fillna(False).astype(bool).tolist(),
    "EMA Trend": ema_trend.reindex(performance_df.index).fillna("Unknown").tolist(),
    "Volatility 1M": volatility_1M.reindex(performance_df.index).round(4),
    "Volatility 3M": volatility_3M.reindex(performance_df.index).round(4),
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
